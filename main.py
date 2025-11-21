from src.workflow import run_volunteer_agent_flow

# --- Run the project! ---
if __name__ == "__main__":

    my_request = "I live near Karnataka and need a list of volunteer work available this weekend"

    final_answer = run_volunteer_agent_flow(my_request)

    print("\n========= FINAL RESPONSE =========\n")
    print(final_answer)
    print("\n==================================\n")
