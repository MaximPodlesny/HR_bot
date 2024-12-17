
from db.create_table import AdminPenal
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
# from config import DATABASE_URL
DATABASE_URL = "postgresql://postgres:2565525@localhost:5432/vacancy"
def get_db():
    engine = create_engine(DATABASE_URL, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
def get_admins():
    session = get_db()

    return set([int(i) for i in (session.query(AdminPenal)).first().admin_ids.split(' ')])