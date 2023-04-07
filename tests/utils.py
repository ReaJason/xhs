import json


def beauty_print(data: dict):
    print(json.dumps(data, ensure_ascii=False, indent=2))
