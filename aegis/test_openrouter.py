import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1",
    ),
)


response = client.chat.completions.create(
    model=os.getenv(
        "OPENROUTER_MODEL",
        "openrouter/free",
    ),
    messages=[
        {
            "role": "user",
            "content": (
                "Reply with exactly: "
                "AEGIS OPENROUTER TEST OK"
            ),
        }
    ],
)


print(
    response.choices[0].message.content
)