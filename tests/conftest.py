# tests/conftest.py

import pytest
from app import create_app  # Assuming you have a factory function to create the Flask app
from flask import Flask

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DEBUG": False
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
