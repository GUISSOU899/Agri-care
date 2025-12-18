from sqlalchemy import create_engine, MetaData
from app.core.config import settings
from app.models import * # Import all models to ensure metadata is populated

def reset_db():
    print(f"Resetting database at {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    meta = MetaData()
    meta.reflect(bind=engine)
    print(f"Found tables: {list(meta.tables.keys())}")
    meta.drop_all(bind=engine)
    print("All tables dropped.")

if __name__ == "__main__":
    reset_db()
