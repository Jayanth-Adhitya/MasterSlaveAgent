# Coolify Deployment Guide

This guide explains how to deploy the Multi-tenant Agent Prototype to Coolify.

## Prerequisites

1. **Coolify Server**: Have Coolify installed and running on your server
2. **Git Repository**: Push this codebase to a Git repository (GitHub, GitLab, etc.)
3. **Google Gemini API Key**: Obtain from Google AI Studio

## Deployment Steps

### 1. Prepare Your Repository

Ensure your repository includes:
- `docker-compose.prod.yml`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker/init.sql`

### 2. Create New Application in Coolify

1. Go to your Coolify dashboard
2. Click **"Add New Resource"**
3. Select **"Application"**
4. Choose your Git source (GitHub, GitLab, etc.)
5. Select the repository containing this project

### 3. Configure Build Pack

1. In the application settings, select **"Docker Compose"** as the build pack
2. Set the **Docker Compose Location** to: `docker-compose.prod.yml`
3. Leave **Base Directory** as `/` (root)

### 4. Configure Environment Variables

In Coolify's environment variables section, add:

```
# Required
DOMAIN=your-app.your-domain.com
POSTGRES_PASSWORD=<generate-secure-password>
JWT_SECRET_KEY=<generate-secure-32+-char-string>
GOOGLE_API_KEY=<your-gemini-api-key>

# Optional (defaults shown)
POSTGRES_USER=postgres
POSTGRES_DB=agent_db
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
APP_NAME=Agent Prototype
DEBUG=false
```

**Security Notes:**
- Generate a strong password for `POSTGRES_PASSWORD` (use `openssl rand -hex 32`)
- Generate a secure JWT secret (use `openssl rand -hex 32`)
- Never commit real credentials to the repository

### 5. Configure Domain

1. In Coolify, go to the **"Domains"** section
2. Add your domain (e.g., `agent.yourdomain.com`)
3. Coolify will automatically configure Traefik and SSL

### 6. Deploy

1. Click **"Deploy"** in Coolify
2. Monitor the build logs for any errors
3. Wait for all services to become healthy

### 7. Initialize Database

After first deployment, you need to seed initial data:

1. SSH into your Coolify server
2. Run the seed script:
```bash
docker exec -it agent_backend python -c "
import asyncio
import sys
sys.path.insert(0, '/app')
from app.core.database import async_session_maker, engine, Base
from app.core.security import get_password_hash
from app.models import Tenant, User, TenantKnowledge

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        # Create a test tenant
        tenant = Tenant(name='Test Business', type='business')
        session.add(tenant)
        await session.flush()

        # Create test user
        user = User(
            tenant_id=tenant.id,
            email='admin@test.com',
            name='Admin',
            password_hash=get_password_hash('password123'),
            role='admin',
        )
        session.add(user)
        await session.commit()
        print(f'Created tenant {tenant.id} and user admin@test.com')

asyncio.run(seed())
"
```

Or copy and run the `scripts/seed_data.py` file inside the container.

## Architecture Overview

The deployment consists of these services:

- **postgres**: PostgreSQL database with pgvector extension
- **redis**: Message queue for async processing
- **backend**: FastAPI application server
- **worker**: Background worker for LLM processing
- **frontend**: Nginx serving React SPA with API proxy

## Monitoring

### Health Checks

- **Frontend**: `GET /health` → Returns "healthy"
- **Backend**: `GET /health` → Returns JSON with status
- **PostgreSQL**: Uses `pg_isready` command
- **Redis**: Uses `redis-cli ping`

### Logs

View logs in Coolify dashboard or via Docker:
```bash
docker logs agent_backend
docker logs agent_worker
docker logs agent_frontend
```

## Updating

1. Push changes to your Git repository
2. In Coolify, click **"Redeploy"**
3. Coolify will rebuild and restart services with zero downtime

## Troubleshooting

### Common Issues

1. **"No Available Server" Error**
   - Check health checks are passing: `docker ps`
   - Verify all containers are running

2. **Database Connection Failed**
   - Ensure PostgreSQL container is healthy
   - Check DATABASE_URL environment variable

3. **LLM Not Responding**
   - Verify GOOGLE_API_KEY is set correctly
   - Check worker logs for API errors

4. **WebSocket Connection Issues**
   - Ensure Traefik is configured for WebSocket upgrade
   - Check nginx.conf proxy settings

### Reset Database

If needed, reset and reseed:
```bash
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
# Then run seed script
```

## Security Recommendations

1. **Change default passwords** - Never use defaults in production
2. **Use strong JWT secret** - At least 32 characters, randomly generated
3. **Enable HTTPS** - Coolify handles this automatically via Traefik
4. **Regular backups** - Set up PostgreSQL backup schedule
5. **Monitor resources** - Watch CPU/memory usage of worker service

## Scaling Considerations

For higher load:
- Add more worker replicas
- Use external PostgreSQL (managed database)
- Use external Redis (managed cache)
- Consider load balancing multiple backend instances

## Support

For issues:
- Check Coolify documentation: https://coolify.io/docs
- Review application logs in Coolify dashboard
- Monitor health check statuses
