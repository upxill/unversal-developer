from graph import create_graph


def main():
    app = create_graph()
    user_lang = (
        input("Enter language (python, java, rust, go, node, sql): ").strip().lower()
    )
    user_task = input("Enter the user story/task: ").strip()

    inputs = {
        "user_story": user_task,
        "language": user_lang,
        "code": "",
        "feedback": "",
        "test_report": "",
        "iterations": 0,
        "is_passing": False,
    }

    final_output = app.invoke(inputs)

    print("\n--- FINAL CODE OUTPUT ---")
    print(final_output["code"])


if __name__ == "__main__":
    main()
