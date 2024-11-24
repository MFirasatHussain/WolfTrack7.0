import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Validate if the API key is set
if not openai.api_key:
    raise ValueError("OpenAI API key is not set. Please check your .env file or environment variables.")

def get_gpt_suggestions(job_name, job_description, resume_content):
    """
    Sends data to GPT and retrieves suggestions for improving the resume.
    :param job_name: Name of the job.
    :param job_description: Description of the job.
    :param resume_content: Extracted content from the resume.
    :return: GPT's suggestions.
    """
    prompt = f"""
    I have a job titled "{job_name}" with the following description:
    {job_description}

    The resume contains:
    {resume_content}

    Please suggest improvements to align this resume with the job description.
    """
    try:
        # Send the prompt to the GPT API
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use GPT-3 model
            prompt=prompt,
            max_tokens=500,            # Adjust tokens to control response length
            temperature=0.7            # Set creativity level
        )
        # Return the suggestions from GPT
        return response.choices[0].text.strip()
    except Exception as e:
        # Log the error and return a meaningful message
        print(f"Error interacting with GPT API: {e}")
        return "Failed to fetch suggestions. Please try again later."
