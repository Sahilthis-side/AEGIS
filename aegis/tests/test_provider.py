from aegis.providers.openai import OpenAIProvider


def test_openai_provider_creation():

    provider = OpenAIProvider(
        model="gpt-5",
        api_key="test-key",
    )

    assert provider.model == "gpt-5"