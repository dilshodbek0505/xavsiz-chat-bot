def build_greeting(first_name: str | None) -> str:
    name = (first_name or "").strip()
    if not name:
        return "Salom!"
    return f"Salom, {name}!"
