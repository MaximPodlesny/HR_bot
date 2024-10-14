import aiohttp
from typing import Dict, Optional
from bot.config import BITRIX_API_KEY, BITRIX_DOMAIN, BITRIX_API_URL

async def create_lead(candidate_data: Dict) -> Optional[Dict]:
    """
    Creates a new lead in Bitrix24 for a candidate.
    """
    async with aiohttp.ClientSession() as session:
        url = f"{BITRIX_API_URL}/crm.lead.add"
        data = {
            "fields": {
                "NAME": candidate_data.get("name"),
                "PHONE": candidate_data.get("phone"),
                "EMAIL": candidate_data.get("email"),
                "SOURCE_ID": "telegram_bot",  # Set the lead source to Telegram
                "STATUS_ID": "NEW",  # Set the initial lead status to "NEW"
            }
        }
        headers = {
            "Authorization": f"Bearer {BITRIX_API_KEY}",
            "Content-Type": "application/json",
        }
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

async def update_lead(lead_id: int, candidate_data: Dict) -> bool:
    """
    Updates an existing lead in Bitrix24 with candidate data.
    """
    async with aiohttp.ClientSession() as session:
        url = f"{BITRIX_API_URL}/crm.lead.update"
        data = {
            "id": lead_id,
            "fields": {
                "NAME": candidate_data.get("name"),
                "PHONE": candidate_data.get("phone"),
                "EMAIL": candidate_data.get("email"),
                "SOURCE_ID": "telegram_bot",  # Update lead source if necessary
                "STATUS_ID": "NEW",  # Update lead status based on candidate progress
            }
        }
        headers = {
            "Authorization": f"Bearer {BITRIX_API_KEY}",
            "Content-Type": "application/json",
        }
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                return True
            else:
                return False

async def create_task(lead_id: int, task_description: str): # -> Optional[Dict]:
    """
    Creates a new task in Bitrix24 associated with a lead.
    """
    async with aiohttp.ClientSession() as session:
        url = f"{BITRIX_API_URL}/tasks.task.add"
        data = {
            "fields": {
                "TITLE": task_description,
                "RESPONSIBLE_ID": "your_user_id_in_bitrix",  # Set the responsible user for the task
                "CRM_ENTITY_ID": lead_id,  # Link the task to the lead
                "CRM_ENTITY_TYPE": "CRM",  # Specify CRM entity type
            }
        }
        headers = {
            "Authorization": f"Bearer {BITRIX_API_KEY}",
            "Content-Type": "application/json",
        }
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None