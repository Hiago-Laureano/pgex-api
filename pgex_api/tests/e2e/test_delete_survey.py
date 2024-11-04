from pytest import fixture, mark
from rest_framework.test import APIClient

from pgex_api.models import User, Survey

@fixture
def models():
    class Models():
        survey = Survey.objects.create(name = "old_name", n_questions = 1, questions = {"title": [{'id': 1, 'question': 'test_question_0', 'is_descriptive': False}]})
        normal_user = User.objects.create_user(email="test1@test.com", password="12345", first_name="Test1", last_name="T3")
        staff_user = User.objects.create_user(email="test2@test.com", password="12345", first_name="Test2", last_name="T2", is_staff=True)
        superuser = User.objects.create_superuser(email="test3@test.com", password="12345", first_name="Test3", last_name="T1")
    models = Models()
    return models

@mark.django_db
def test_delete_failed_staff_user_no_authorized(models):
    client = APIClient()
    client.force_authenticate(user=models.staff_user)
    response = client.delete("/api/v1/surveys/1/")
    assert response.status_code == 403
    assert list(response.json().keys()) == ["detail"]

@mark.django_db
def test_delete_failed_normal_user_no_authorized(models):
    client = APIClient()
    client.force_authenticate(user=models.normal_user)
    response = client.delete("/api/v1/surveys/1/")
    assert response.status_code == 403
    assert list(response.json().keys()) == ["detail"]

@mark.django_db
def test_delete_failed_no_authenticated():
    client = APIClient()
    response = client.delete("/api/v1/surveys/1/")
    assert response.status_code == 401
    assert list(response.json().keys()) == ["detail"]

@mark.django_db
def test_delete_success(models):
    client = APIClient()
    client.force_authenticate(user=models.superuser)
    response = client.delete("/api/v1/surveys/1/")
    assert response.status_code == 204