import asyncio
from app.core.database import async_session_maker
from app.core.security import get_password_hash
from app.models import Tenant, User, TenantKnowledge
from sqlalchemy import select

async def seed():
    async with async_session_maker() as session:
        # Check if data exists
        result = await session.execute(select(Tenant))
        existing = result.first()
        if existing:
            print("Data already exists, skipping seed")
            return

        # Create restaurant tenant
        tenant = Tenant(name="Mario's Pizza", type="restaurant")
        session.add(tenant)
        await session.flush()

        # Create users
        users = [
            User(
                tenant_id=tenant.id,
                email="mario@pizza.com",
                name="Mario",
                password_hash=get_password_hash("password123"),
                role="manager"
            ),
            User(
                tenant_id=tenant.id,
                email="luigi@pizza.com",
                name="Luigi",
                password_hash=get_password_hash("password123"),
                role="employee"
            ),
            User(
                tenant_id=tenant.id,
                email="peach@pizza.com",
                name="Peach",
                password_hash=get_password_hash("password123"),
                role="employee"
            ),
        ]
        session.add_all(users)
        await session.flush()

        # Add knowledge
        knowledge = [
            TenantKnowledge(
                tenant_id=tenant.id,
                content=f"Staff roster: Mario (manager, user_id={users[0].id}), Luigi (employee, user_id={users[1].id}), Peach (employee, user_id={users[2].id}). Mario works Mon-Fri 9am-5pm, Luigi works Mon-Wed 6am-2pm, Peach works Thu-Sun 2pm-10pm.",
                category="roster"
            ),
            TenantKnowledge(
                tenant_id=tenant.id,
                content="Business hours: Monday-Sunday 11am-10pm. Deliveries accepted between 8am-11am on weekdays only.",
                category="schedule"
            ),
            TenantKnowledge(
                tenant_id=tenant.id,
                content="Restaurant rules: All employees must report 30 minutes before shift. Deliveries must be received by on-duty staff. If no manager present, senior employee makes decisions.",
                category="rules"
            ),
        ]
        session.add_all(knowledge)

        await session.commit()
        print(f"✓ Created tenant: {tenant.name}")
        print(f"✓ Created {len(users)} users")
        print(f"✓ Created {len(knowledge)} knowledge items")
        print("\nLogin credentials:")
        print("  mario@pizza.com / password123")
        print("  luigi@pizza.com / password123")
        print("  peach@pizza.com / password123")

if __name__ == "__main__":
    asyncio.run(seed())
