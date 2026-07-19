from app1 import run_agent as golden_agent
from app2 import run_chat as designer_agents

while True:
    print("\n===== MENU BUILDER =====")
    print("1. Golden Recipe & Price Agent")
    print("2. Designer  Menu Design Agent")
    print("3. Exit")

    choice = input("Choose an agent: ")

    if choice == "1":
        user_input = input(">> ")
        print(golden_agent(user_input))

    elif choice == "2":
        user_input = input(">> ")
        print(designer_agent(user_input))

    elif choice == "3":
        print("Goodbye!")
        break

    else:
        print("Invalid choice. Please try again.")