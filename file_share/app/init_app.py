from typing import Any

from file_share.database import Database
from file_share.app.app import FileShareApp
from file_share.definitions.procedures import create_cert
from file_share.definitions import certs_dir

db_instance = Database()


def is_first_init():
    return db_instance.get_me() is None


def first_init_app(name: str, password: str, config: dict[str, Any]) -> FileShareApp:
    if not db_instance.add_me(name, password):
        raise ValueError("This is not first app run.")
    create_cert(name, certs_dir)
    return FileShareApp(db_instance.get_token(password), config)


def init_app(password: str, config: dict[str, Any]) -> FileShareApp:
    return FileShareApp(db_instance.get_token(password), config)
