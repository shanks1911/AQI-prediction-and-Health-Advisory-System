import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env variables if using locally
load_dotenv()

# Initialize the OpenAI client using your API key
client = OpenAI(base_url="https://models.github.ai/inference",
                api_key=os.getenv("OPENAI_o1_MINI_API_KEY"))  # or GITHUB_TOKEN if used

def get_aqi_advice(forecasted_aqi, user_health_issues=None):
    system_prompt = (
        "You are a helpful assistant that provides general wellness and environmental advice based on Air Quality Index (AQI) levels. "
        "Use official public health sources such as WHO, CDC, EPA, and CPCB guidelines. "
        "When a user shares personal sensitivities or health concerns, offer supportive and informative suggestions for minimizing discomfort or exposure."
    )

    user_prompt = f"The upcoming AQI forecast is: {forecasted_aqi}.\n"
    if user_health_issues:
        user_prompt += (
            f"The user mentioned the following health sensitivities: {user_health_issues}.\n"
            "What practical wellness tips or environmental precautions should they follow?"
        )
    else:
        user_prompt += "What are some general helpful tips for staying healthy in this air quality range?"

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.6,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()
