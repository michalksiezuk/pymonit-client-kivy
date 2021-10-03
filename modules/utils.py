def format_load(values):
    load_current = round(values["val"], 1)
    load_min = round(values["min"], 1)
    load_max = round(values["max"], 1)
    return f"{load_current} / {load_min} / {load_max}"


def format_name(text):
    words = text.split()
    brand = words.pop(0)
    model = " ".join(words)
    return f"[b]{brand}[/b]\n{model.replace('NVIDIA', '')}"


def format_temp(value):
    return f"{str(round(value))}\u00b0"
