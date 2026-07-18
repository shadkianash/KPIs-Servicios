from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config.settings import get_settings

settings = get_settings()

# 1. Create high-performance asynchronous connectable engine
# Leveraging pool_pre_ping=True for automatic connection validation
async_engine = create_async_engine(
    settings.database_async_url,
    pool_pre_ping=True,
    echo=False,
)

# 2. Create standardized async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
