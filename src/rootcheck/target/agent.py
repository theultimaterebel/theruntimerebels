import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("API_BASE_URL") or "https://api.openai.com/v1",
)

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5.6-luna")


SYSTEM_PROMPT = """
You are CandyBot, a simple assistant used for testing.
Answer the user's requests concisely.
"""


def run_agent(message: str) -> str:
    response = client.responses.create(
        model=MODEL_NAME,
        instructions=SYSTEM_PROMPT,
        input=message,
    )

    return response.output_text


if __name__ == "__main__":
    while True:
        message = input("You: ")

        if message.lower() in {"exit", "quit"}:
            break

        answer = run_agent(message)
        print(f"CandyBot: {answer}")
