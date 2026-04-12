from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=True,          # Set to False in production
    pool_pre_ping=True  # Ensures stale connections are refreshed
)

# 🔍 Debug: Verify the connected database
# try:
#     with engine.connect() as conn:
#         db_name = conn.execute(text("SELECT current_database();")).scalar()
#         print(f"✅ Connected to database: {db_name}")
# except Exception as e:
#     print(f"❌ Database Connection Error: {e}")

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# Base class for models
Base = declarative_base()