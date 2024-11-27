import requests
import json
import os
from dotenv import load_dotenv


def evaluate_job_match(job_title, job_description, resume_content):
    load_dotenv()
    OPENROUTER_API_KEY = os.getenv("API_KEY")
    
    prompt = f"""Please evaluate this job application and provide detailed feedback:

    Job Title: {job_title}

    Job Description:
    {job_description}

    Resume Content:
    {resume_content}

    Please analyze:
    1. Overall match score (0-100)
    2. Key matching skills and qualifications
    3. Missing or gaps in qualifications
    4. Specific suggestions for improvement
    """

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            data=json.dumps({
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [
                    {"role": "system", "content": "You are an expert HR recruiter who provides detailed resume evaluations."},
                    {"role": "user", "content": prompt}
                ]
            })
        )
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
    except Exception as e:
        return f"Error processing API response: {e}"

def get_ats_score(resume_content):
    load_dotenv()
    OPENROUTER_API_KEY = os.getenv("API_KEY")
    
    ats_prompt = f"""You are a highly critical ATS system evaluator. Analyze this resume with extreme scrutiny.
    
    Scoring Guidelines:
    - Start with a base score of 30
    - Maximum possible score is 80
    - Deduct 10 points for any missing core section
    - Deduct 5 points for each formatting inconsistency
    - Deduct 8 points for non-quantified achievements
    - Deduct 3 points for each generic skill without context
    - Require specific metrics and achievements for scores above 50
    
    Resume Content:
    {resume_content}
    
    IMPORTANT: Return ONLY a number between 0-80. Do not include any other text or symbols."""

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            data=json.dumps({
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [
                    {"role": "system", "content": "You are an extremely strict ATS scoring system. Never score above 80."},
                    {"role": "user", "content": ats_prompt}
                ]
            })
        )
        response_data = response.json()
        score_text = response_data['choices'][0]['message']['content'].strip()
        return int(''.join(filter(str.isdigit, score_text)))
    except Exception as e:
        return f"Error calculating ATS score: {e}"