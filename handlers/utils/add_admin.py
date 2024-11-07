

from db.create_table import AdminPenal
from handlers.utils.candidate import get_db


async def add_admin_id(id):
    session = get_db()
    admins = session.query(AdminPenal)
    admins.admin_ids = f'{admins.admin_ids} {id}'

    session.add(admins)
    session.commit()