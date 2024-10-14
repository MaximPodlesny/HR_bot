import aiohttp
from bot.config import HH_API_KEY

async def search_candidates(vacancy_title: str) -> List[Dict]:
    """Searches for candidates on HH.ru based on vacancy title."""
    async with aiohttp.ClientSession() as session:
        url = "https://api.hh.ru/vacancies"
        params = {
            "text": vacancy_title,
            "per_page": 20,  # Adjust the number of results per page as needed
            "page": 1,  # Start with the first page
        }
        headers = {"Authorization": f"Bearer {HH_API_KEY}"}
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                candidates = data.get("items", [])
                return candidates
            else:
                return []

async def publish_vacancy(vacancy_data: Dict) -> bool:
    """Publishes a vacancy on HH.ru."""
    async with aiohttp.ClientSession() as session:
        url = "https://api.hh.ru/vacancies"
        headers = {"Authorization": f"Bearer {HH_API_KEY}"}
        async with session.post(url, headers=headers, json=vacancy_data) as response:
            if response.status == 201:  # Status code 201 indicates successful creation
                return True
            else:
                return False

async def get_candidate_details(candidate_id: int) -> Dict:
    """Retrieves details of a candidate from HH.ru."""
    async with aiohttp.ClientSession() as session:
        url = f"https://api.hh.ru/vacancies/{candidate_id}"
        headers = {"Authorization": f"Bearer {HH_API_KEY}"}
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {}