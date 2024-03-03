import os


def get_env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes", "True")


def enable_server_download() -> bool:
    return get_env_bool("SERVER_DOWNLOAD", False)
