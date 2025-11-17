import json
import logging
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser

from app.core.config import get_settings
from app.models import Tenant, User, TenantKnowledge, Notification, Message
from app.schemas.action import LLMResponse, NotifyUserAction, LogEventAction

logger = logging.getLogger(__name__)
settings = get_settings()


class SlaveAgent:
    """Agent instance for a specific tenant."""

    def __init__(self, tenant_id: int):
        self.tenant_id = tenant_id
        self.tenant_info: dict[str, Any] = {}
        self.user_roster: list[dict] = []
        self.knowledge_base: list[str] = []
        self.conversation_memory: dict[str, list] = {}  # key: user_id:session_id

        # Initialize LLM
        api_key = settings.google_api_key
        if not api_key:
            logger.warning("GOOGLE_API_KEY not set - LLM calls will fail")
        else:
            logger.info(f"Using Gemini API key: {api_key[:10]}...")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.3,
        )
        self.parser = JsonOutputParser(pydantic_object=LLMResponse)

    async def load_tenant_context(self, session: AsyncSession):
        """Load tenant information and knowledge base."""
        # Load tenant info
        tenant = await session.get(Tenant, self.tenant_id)
        if tenant:
            self.tenant_info = {
                "id": tenant.id,
                "name": tenant.name,
                "type": tenant.type,
            }

        # Load user roster
        result = await session.execute(
            select(User).where(User.tenant_id == self.tenant_id)
        )
        users = result.scalars().all()
        self.user_roster = [
            {"id": u.id, "name": u.name, "email": u.email, "role": u.role}
            for u in users
        ]

        # Load knowledge base (simple text retrieval for PoC)
        result = await session.execute(
            select(TenantKnowledge).where(TenantKnowledge.tenant_id == self.tenant_id)
        )
        knowledge = result.scalars().all()
        self.knowledge_base = [k.content for k in knowledge]

        logger.info(
            f"Loaded context for tenant {self.tenant_id}: {len(self.user_roster)} users, {len(self.knowledge_base)} knowledge items"
        )

    def _get_memory_key(self, user_id: int, session_id: str) -> str:
        return f"{user_id}:{session_id}"

    def _get_conversation_history(self, user_id: int, session_id: str) -> list:
        key = self._get_memory_key(user_id, session_id)
        return self.conversation_memory.get(key, [])

    def _add_to_memory(self, user_id: int, session_id: str, role: str, content: str):
        key = self._get_memory_key(user_id, session_id)
        if key not in self.conversation_memory:
            self.conversation_memory[key] = []
        self.conversation_memory[key].append({"role": role, "content": content})

    def _build_system_prompt(self, user_info: dict) -> str:
        """Build system prompt with tenant context."""
        knowledge_text = "\n".join(
            [f"- {k}" for k in self.knowledge_base]
        )
        roster_text = "\n".join(
            [
                f"- {u['name']} (ID: {u['id']}, Role: {u['role']}, Email: {u['email']})"
                for u in self.user_roster
            ]
        )

        return f"""You are an AI assistant for {self.tenant_info.get('name', 'Unknown')} ({self.tenant_info.get('type', 'business')}).

Current user: {user_info.get('name')} (ID: {user_info.get('id')}, Role: {user_info.get('role')})

Team Members:
{roster_text}

Business Knowledge:
{knowledge_text}

Your role:
1. Help users with their queries using the business context provided
2. When appropriate, notify other team members about important information
3. Be concise and helpful

IMPORTANT: You MUST respond in valid JSON format with this exact structure:
{{
  "response": "Your response message to the user",
  "actions": [
    {{
      "type": "notify_user",
      "user_id": <integer user_id from roster>,
      "message": "notification message"
    }}
  ]
}}

The "actions" array can be empty if no notifications are needed.
Only notify users when the message contains information that others need to know (e.g., schedule changes, deliveries, important events).
When notifying, always use the user_id from the Team Members list above.

Example response with notification:
{{
  "response": "I'll notify the morning shift about the delivery.",
  "actions": [
    {{
      "type": "notify_user",
      "user_id": 2,
      "message": "Delivery scheduled for tomorrow at 10am"
    }}
  ]
}}

Example response without notification:
{{
  "response": "The cleaning is scheduled for Tuesday at 10am.",
  "actions": []
}}
"""

    async def process_message(
        self,
        session: AsyncSession,
        user_id: int,
        user_info: dict,
        session_id: str,
        message: str,
    ) -> LLMResponse:
        """Process a user message and return response with actions."""
        # Ensure context is loaded
        if not self.tenant_info:
            await self.load_tenant_context(session)

        # Build messages for LLM
        messages = [SystemMessage(content=self._build_system_prompt(user_info))]

        # Add conversation history
        history = self._get_conversation_history(user_id, session_id)
        for msg in history[-10:]:  # Last 10 messages for context
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        # Add current message
        messages.append(HumanMessage(content=message))

        # Call LLM
        try:
            response = await self.llm.ainvoke(messages)
            response_text = response.content

            # Parse JSON response
            try:
                # Try to extract JSON from response
                parsed = self._parse_llm_response(response_text)
                llm_response = LLMResponse(**parsed)
            except Exception as parse_error:
                logger.warning(f"Failed to parse LLM response: {parse_error}")
                # Fallback: treat entire response as text, no actions
                llm_response = LLMResponse(response=response_text, actions=[])

            # Update memory
            self._add_to_memory(user_id, session_id, "user", message)
            self._add_to_memory(
                user_id, session_id, "assistant", llm_response.response
            )

            return llm_response

        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            return LLMResponse(
                response=f"I apologize, but I encountered an error processing your request. Please try again.",
                actions=[],
            )

    def _parse_llm_response(self, text: str) -> dict:
        """Extract JSON from LLM response text."""
        # Try to find JSON in the response
        text = text.strip()

        # If wrapped in markdown code block
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        # Parse JSON
        return json.loads(text)

    async def execute_actions(
        self,
        session: AsyncSession,
        from_user_id: int,
        actions: list,
    ):
        """Execute actions returned by the LLM."""
        for action in actions:
            if isinstance(action, NotifyUserAction):
                await self._execute_notify_user(
                    session, from_user_id, action.user_id, action.message
                )
            elif isinstance(action, LogEventAction):
                logger.info(f"Event logged: {action.event}")
            else:
                logger.warning(f"Unknown action type: {type(action)}")

    async def _execute_notify_user(
        self,
        session: AsyncSession,
        from_user_id: int,
        to_user_id: int,
        message: str,
    ):
        """Create notification for a user."""
        # Verify target user belongs to same tenant
        target_user = await session.get(User, to_user_id)
        if not target_user or target_user.tenant_id != self.tenant_id:
            logger.error(
                f"Cannot notify user {to_user_id}: not in tenant {self.tenant_id}"
            )
            return

        notification = Notification(
            tenant_id=self.tenant_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            message=message,
            read=False,
        )
        session.add(notification)
        await session.flush()
        logger.info(f"Created notification from user {from_user_id} to {to_user_id}")
