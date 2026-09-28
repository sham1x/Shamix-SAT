import pytest
from pydantic import ValidationError
from backend.app.config import Settings

def test_sensitive_files_and_backend_code_return_404(client):
    forbidden_paths = [
        "/.env",
        "/.git/config",
        "/backend/data/shamix.db",
        "/backend/app/config.py",
        "/tests/conftest.py"
    ]
    for path in forbidden_paths:
        resp = client.get(path)
        assert resp.status_code == 404, f"Path {path} returned {resp.status_code}, expected 404"

def test_secret_key_rejects_placeholders_and_defaults():
    # Reject placeholders starting with CHANGE_ME
    with pytest.raises(ValidationError):
        Settings(SECRET_KEY="CHANGE_ME_generate_with_python_-c_secrets")
    
    # Reject strings containing 'default'
    with pytest.raises(ValidationError):
        Settings(SECRET_KEY="my_super_secret_key_contains_default_word_here")

    # Reject keys shorter than 32 characters
    with pytest.raises(ValidationError):
        Settings(SECRET_KEY="short_key")
