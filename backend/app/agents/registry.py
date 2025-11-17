"""Registry for managing SlaveAgent instances."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.slave_agent import SlaveAgent

logger = logging.getLogger(__name__)

# In-memory registry of agent instances
_agent_registry: dict[int, SlaveAgent] = {}


async def get_or_create_agent(tenant_id: int, session: AsyncSession) -> SlaveAgent:
    """Get existing agent for tenant or create new one."""
    if tenant_id not in _agent_registry:
        logger.info(f"Creating new SlaveAgent for tenant {tenant_id}")
        agent = SlaveAgent(tenant_id)
        await agent.load_tenant_context(session)
        _agent_registry[tenant_id] = agent
    else:
        logger.debug(f"Reusing existing SlaveAgent for tenant {tenant_id}")

    return _agent_registry[tenant_id]


def clear_agent_registry():
    """Clear all agent instances (for testing)."""
    _agent_registry.clear()
