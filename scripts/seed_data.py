#!/usr/bin/env python3
"""Seed database with test tenants, users, and knowledge."""
import asyncio
import sys
import os
from pathlib import Path

# Set working directory to project root for .env loading
project_root = Path(__file__).parent.parent
os.chdir(project_root)

# Add backend to path
sys.path.insert(0, str(project_root / "backend"))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker, engine, Base
from app.core.security import get_password_hash
from app.models import Tenant, User, TenantKnowledge


async def seed_data():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        # Create tenants
        restaurant = Tenant(name="Mario's Pizza", type="restaurant")
        property_mgmt = Tenant(name="Oak Street Property", type="property")
        session.add_all([restaurant, property_mgmt])
        await session.flush()

        # Create users for restaurant
        restaurant_users = [
            User(
                tenant_id=restaurant.id,
                email="mario@pizza.com",
                name="Mario",
                password_hash=get_password_hash("password123"),
                role="manager",
            ),
            User(
                tenant_id=restaurant.id,
                email="luigi@pizza.com",
                name="Luigi",
                password_hash=get_password_hash("password123"),
                role="employee",
            ),
            User(
                tenant_id=restaurant.id,
                email="peach@pizza.com",
                name="Peach",
                password_hash=get_password_hash("password123"),
                role="employee",
            ),
        ]
        session.add_all(restaurant_users)
        await session.flush()

        # Create users for property
        property_users = [
            User(
                tenant_id=property_mgmt.id,
                email="john@oakst.com",
                name="John",
                password_hash=get_password_hash("password123"),
                role="tenant",
            ),
            User(
                tenant_id=property_mgmt.id,
                email="jane@oakst.com",
                name="Jane",
                password_hash=get_password_hash("password123"),
                role="tenant",
            ),
            User(
                tenant_id=property_mgmt.id,
                email="bob@oakst.com",
                name="Bob",
                password_hash=get_password_hash("password123"),
                role="tenant",
            ),
        ]
        session.add_all(property_users)
        await session.flush()

        # Add knowledge for restaurant
        restaurant_knowledge = [
            TenantKnowledge(
                tenant_id=restaurant.id,
                content=f"Staff roster: Mario (manager, works Mon-Fri 9am-5pm), Luigi (employee, works Mon-Wed 6am-2pm), Peach (employee, works Thu-Sun 2pm-10pm). Mario's user_id is {restaurant_users[0].id}, Luigi's user_id is {restaurant_users[1].id}, Peach's user_id is {restaurant_users[2].id}.",
                category="roster",
                embedding=None,  # Will be set by embeddings later
            ),
            TenantKnowledge(
                tenant_id=restaurant.id,
                content="Business hours: Monday-Sunday 11am-10pm. Deliveries accepted between 8am-11am on weekdays only.",
                category="schedule",
            ),
            TenantKnowledge(
                tenant_id=restaurant.id,
                content="Restaurant rules: All employees must report 30 minutes before shift. Deliveries must be received by on-duty staff. If no manager present, senior employee makes decisions.",
                category="rules",
            ),
        ]
        session.add_all(restaurant_knowledge)

        # Add knowledge for property
        property_knowledge = [
            TenantKnowledge(
                tenant_id=property_mgmt.id,
                content=f"Property address: 123 Oak Street, London, UK. Tenants: John (Room 1, user_id={property_users[0].id}), Jane (Room 2, user_id={property_users[1].id}), Bob (Room 3, user_id={property_users[2].id}).",
                category="roster",
                embedding=None,
            ),
            TenantKnowledge(
                tenant_id=property_mgmt.id,
                content="Cleaning schedule: Professional cleaning every Tuesday at 10am. All tenants must ensure common areas are accessible.",
                category="schedule",
            ),
            TenantKnowledge(
                tenant_id=property_mgmt.id,
                content="House rules: Quiet hours 10pm-8am. No smoking inside. Bins collected every Thursday morning. Shared kitchen must be cleaned after use.",
                category="rules",
            ),
        ]
        session.add_all(property_knowledge)

        await session.commit()
        print("Seed data created successfully!")
        print(f"Restaurant tenant ID: {restaurant.id}")
        print(f"Property tenant ID: {property_mgmt.id}")
        print("Test credentials: password123 for all users")
        print("\nRestaurant users:")
        for user in restaurant_users:
            print(f"  - {user.email} ({user.role})")
        print("\nProperty users:")
        for user in property_users:
            print(f"  - {user.email} ({user.role})")


if __name__ == "__main__":
    asyncio.run(seed_data())
