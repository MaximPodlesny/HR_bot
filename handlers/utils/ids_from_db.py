
from handlers.utils.get_all_vacansies import get_vacancies


async def get_ids_vacancies(): 
    vacancies = await get_vacancies()
    return [str(vacancy.id_hh) for vacancy in vacancies]