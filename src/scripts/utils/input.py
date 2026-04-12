def ask(prompt: str, required: bool = True):
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("Value required")
