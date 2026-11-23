import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
from app.config import Config  # noqa: E402

EJEMPLOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ejemplos")


@pytest.fixture
def app(tmp_path):
    class ConfigPrueba(Config):
        TESTING = True
        DATABASE = str(tmp_path / "prueba.db")
        SECRET_KEY = "prueba"
    return create_app(ConfigPrueba)


@pytest.fixture
def cliente(app):
    return app.test_client()


def ingresar(cliente, usuario="admin", clave="admin123"):
    return cliente.post("/login", data={"usuario": usuario, "password": clave}, follow_redirects=True)
