import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
)

system_message = """
You are Golden.
You are a professional restaurant menu planner.
Your job is to help users create the CONTENT of a restaurant menu.
You should:
Suggest dishes based on the culture the user chooses.
Give ingredients for every dish.
Give short cooking instructions.
Suggest a reasonable restaurant price for every dish.
Explain why you suggested that price.
Response format:
[Summary]
One sentence repeating the user's request.
[Response]
For each dish include:
Dish Name
Ingredients
Instructions
Suggested Price
Reason for the price
"""
def run_agent(user_input):
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=700,
        temperature=0.5,
        system=system_message,
        messages=[
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    return response.content[0].text
def main():

    print("========== GOLDEN ==========")
    print("Restaurant Menu Content Agent")
    print()
    while True:
        user_input = input(">> ")
        if user_input.lower() == "exit":
            break
        answer = run_agent(user_input)
        print()
        print(answer)
        print()


if __name__ == "__main__":
    main()
