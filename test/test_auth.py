import pytest
from fastapi.testclient import TestClient
from main import app
from database.database import SessionLocal  # Підключи свою сесію БД
from database.models import User  # Підключи модель
from security import get_password_hash  # Підключи функцію хешування


@pytest.fixture
def client():
    return TestClient(app)


def test_login_success(client):
    # --- 1. ПІДГОТОВКА ДАНИХ (Arrange) ---
    db = SessionLocal()
    # Перевіряємо, чи користувач вже є (щоб тест не падав при повторному запуску)
    user = db.query(User).filter(User.username == "testuser").first()
    if not user:
        # Створюємо користувача з ПРАВИЛЬНО захешованим паролем
        hashed_pw = get_password_hash("correct_password")
        new_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hashed_pw,
            role="dm"  # Відразу даємо йому роль Майстра, наприклад
        )
        db.add(new_user)
        db.commit()
    db.close()

    # --- 2. ВИКОНАННЯ ЗАПИТУ (Act) ---
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "correct_password"}
    )

    # --- 3. ПЕРЕВІРКА РЕЗУЛЬТАТУ (Assert) ---
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


# Інші тести залишаються без змін...
def test_login_wrong_password(client):
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_user_not_found(client):
    response = client.post(
        "/login",
        data={"username": "unknown_user", "password": "some_password"}
    )
    assert response.status_code == 401