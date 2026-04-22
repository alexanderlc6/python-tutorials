from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = 'postgresql://admin:123456@localhost:5432/agent_demo'

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class RepoInfo(Base):
    __tablename__ = 'repo_info'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    stars = Column(Integer)
    forks = Column(Integer)
    lastest_update = Column(DateTime)

Base.metadata.create_all(bind=engine)