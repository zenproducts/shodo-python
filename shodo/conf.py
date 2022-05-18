import os


def conf():
    return {
        "API_TOKEN": os.environ["SHODO_API_TOKEN"],
        "API_ROOT": os.environ["SHODO_API_ROOT"],
    }
