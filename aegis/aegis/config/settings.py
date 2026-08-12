import os

from dotenv import load_dotenv


load_dotenv()


class Settings:

    def __init__(self):

        self.gemini_api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        self.gemini_model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash",
        )

        self.openai_api_key = os.getenv(
            "OPENAI_API_KEY"
        )

        self.openai_model = os.getenv(
            "OPENAI_MODEL",
            "gpt-5",
        )

        self.anthropic_api_key = os.getenv(
            "ANTHROPIC_API_KEY"
        )

        self.anthropic_model = os.getenv(
            "ANTHROPIC_MODEL",
            "",
        )

        self.openrouter_api_key = os.getenv(
            "OPENROUTER_API_KEY"
        )

        self.openrouter_model = os.getenv(
            "OPENROUTER_MODEL",
            "openrouter/free",
        )

        self.openrouter_base_url = os.getenv(
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1",
        )


settings = Settings()
