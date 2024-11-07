from db.create_table import AdminPenal
from handlers.utils.candidate import get_db


async def del_admin_id(id):
    session = get_db()
    admins = session.query(AdminPenal)
    admins.admin_ids = ' '.join([i for i in admins.admin_ids.split(' ') if i != str(id)])

    session.add(admins)
    session.commit()