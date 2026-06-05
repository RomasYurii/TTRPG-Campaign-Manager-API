import pytest
import uuid
from fastapi.testclient import TestClient
from main import app


# Якщо фікстура client вже є у файлі, другу створювати не треба
@pytest.fixture
def client():
    return TestClient(app)


def test_register_user_success(client):
    """Тестуємо успішну реєстрацію нового користувача"""
    unique_id = str(uuid.uuid4())[:8]  # Генеруємо короткий унікальний рядок

    response = client.post(
        "/register",
        json={
            "username": f"newuser_{unique_id}",
            "email": f"newuser_{unique_id}@example.com",
            "password": "secure_password",
            "role": "player"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "User created successfully"
    assert data["username"] == f"newuser_{unique_id}"


def test_register_duplicate_user(client):
    """Тестуємо, що не можна зареєструвати двох користувачів з однаковими даними"""
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "username": f"dupuser_{unique_id}",
        "email": f"dupuser_{unique_id}@example.com",
        "password": "secure_password"
    }

    # 1. Перша реєстрація - має пройти успішно
    response1 = client.post("/register", json=user_data)
    assert response1.status_code == 201

    # 2. Друга реєстрація з тими ж даними - має повернути помилку 400
    response2 = client.post("/register", json=user_data)
    assert response2.status_code == 400
    assert "Username or email already registered" in response2.json()["detail"]


def test_read_users_me_success(client):
    """Тестуємо доступ до захищеного роуту з валідним токеном"""
    unique_id = str(uuid.uuid4())[:8]
    username = f"meuser_{unique_id}"
    password = "my_super_password"

    # 1. Створюємо користувача
    client.post(
        "/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": password
        }
    )

    # 2. Логінимось, щоб отримати токен (зверни увагу: тут data=, а не json=)
    login_response = client.post(
        "/login",
        data={"username": username, "password": password}
    )
    token = login_response.json()["access_token"]

    # 3. Звертаємось до захищеного ендпоінту, передаючи токен у заголовках
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/users/me", headers=headers)

    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["username"] == username
    assert me_data["email"] == f"{username}@example.com"
    assert "role" in me_data


def test_read_users_me_unauthorized(client):
    """Тестуємо, що без токена доступ до /users/me заборонено"""
    # Звертаємось без передачі заголовка Authorization
    response = client.get("/users/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"