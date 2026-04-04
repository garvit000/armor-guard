"""
Database Configuration — ArmorGuard AI
=======================================
Stores trade history, risk state, and persistent execution logs.
Uses SQLAlchemy with SQLite for the hackathon MVP.
"""

from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import json

Base = declarative_base()

class TradeLog(Base):
    __tablename__ = 'trade_logs'

    id = Column(Integer, primary_key=True)
    order_id = Column(String, unique=True, nullable=False)
    ticker = Column(String, nullable=False)
    action = Column(String, nullable=False)
    qty = Column(Integer, nullable=False)
    fill_price = Column(Float, nullable=False)
    notional = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ActionHistory(Base):
    """Logs every attempted action (allowed or blocked)"""
    __tablename__ = 'action_history'

    id = Column(Integer, primary_key=True)
    command = Column(String, nullable=False)
    intent_token = Column(String, default="") # The cryptographic hash generated
    ticker = Column(String)
    action = Column(String)
    qty = Column(Integer)
    status = Column(String, nullable=False) # 'ALLOWED' or 'BLOCKED'
    reasons = Column(String) # JSON string of reasons
    audit_trail = Column(String) # JSON list of timeline events [{time, actor, event, status}]
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Setup Engine
engine = create_engine('sqlite:///armor.db', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Because we're modifying the schema of ActionHistory, we will just wipe the table conceptually
    # but for SQLite without alembic, the easiest hackathon way is to drop and recreate.
    # Note: TradeLog won't be dropped if we just create, but ActionHistory needs the new column.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized with new Audit Log schema.")
