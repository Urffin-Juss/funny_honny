import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_password_login_works(client):
    user_model = get_user_model()
    user_model.objects.create_user(username="operator", password="secret", role="admin")

    response = client.post("/login/", data={"username": "operator", "password": "secret"})

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/workspace/")
