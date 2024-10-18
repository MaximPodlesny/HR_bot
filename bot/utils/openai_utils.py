from bot.config import OPENAI_API_KEY
from openai import OpenAI
from typing import Dict, List

client = OpenAI(api_key=OPENAI_API_KEY)

async def extract_vacancy_data(vacancy_description: str) -> Dict:
    """
    Extracts key information from a vacancy description using OpenAI.
    """
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful HR assistant. Extract the following information from the text: title, responsibilities, requirements, skills, experience."},
            {"role": "user", "content": vacancy_description},
        ],
    )
    extracted_data = response.choices[0].message.content.strip()
    # Process the extracted data (e.g., split into key-value pairs)
    # ...
    return extracted_data

async def generate_interview_questions(vacancy_description: str, vacancy_requirements: str) -> List[str]:
    """
    Generates relevant interview questions based on the vacancy description and requirements.
    """
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful HR assistant. Generate 5 relevant interview questions based on the provided vacancy description and requirements."},
            {"role": "user", "content": f"Vacancy Description: {vacancy_description}\nVacancy Requirements: {vacancy_requirements}"},
        ],
    )
    questions = response.choices[0].message.content.strip().split("\n")
    return questions

async def analyze_candidate_response(question: str, candidate_answer: str) -> str:
    """
    Analyzes a candidate's answer to an interview question using OpenAI.
    """
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful HR assistant. Analyze the following candidate response to an interview question and provide insights."},
            {"role": "user", "content": f"Question: {question}\nAnswer: {candidate_answer}"},
        ],
    )
    analysis = response.choices[0].message.content.strip()
    return analysis