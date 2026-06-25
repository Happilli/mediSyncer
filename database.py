import os

from dotenv import load_dotenv

# making tables visible to sqlmodel
from sqlmodel import Session, create_engine

load_dotenv()


# configuration variables
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# connection url [using pymysql]
database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


# engine
engine = create_engine(database_url)


# getting the session
def get_session():
    with Session(engine) as session:
        yield session
