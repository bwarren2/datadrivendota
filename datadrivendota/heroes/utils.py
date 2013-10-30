def list_to_choice_list(items):
    return [(item, item.replace("_", " ").title()) for item in items]
