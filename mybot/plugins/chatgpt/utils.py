def build_openai_request(context: str, max_tokens: int, model: str = "gpt-4o"):
    return {
        "model": model,
        "messages": [{"role": "user", "content": context}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

