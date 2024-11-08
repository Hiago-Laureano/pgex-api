from pytest import fixture, mark
from rest_framework.test import APIClient

from pgex_api.models import User, Survey

@fixture
def models():
    class Models():
        survey1 = Survey.objects.create(name = "name1", active = False, n_questions = 1, questions = {"title": [{'id': 1, 'question': 'test_question_0', 'is_descriptive': False}]})
        survey2 = Survey.objects.create(name = "name2", n_questions = 1, questions = {"title": [{'id': 1, 'question': 'test_question_0', 'is_descriptive': False}]})
        normal_user = User.objects.create_user(email="test1@test.com", password="12345", first_name="Test1", last_name="T3")
        staff_user = User.objects.create_user(email="test2@test.com", password="12345", first_name="Test2", last_name="T2", is_staff=True)
        superuser = User.objects.create_superuser(email="test3@test.com", password="12345", first_name="Test3", last_name="T1")
    models = Models()
    return models

@mark.django_db
def test_get_all_failed_no_authorized(models):
    client = APIClient()
    client.force_authenticate(user=models.normal_user)
    response = client.get("/api/v1/surveys/")
    assert response.status_code == 403
    assert list(response.json().keys()) == ["detail"]

@mark.django_db
def test_get_all_failed_no_authenticated():
    client = APIClient()
    response = client.get("/api/v1/surveys/")
    assert response.status_code == 401
    assert list(response.json().keys()) == ["detail"]

@mark.django_db
def test_get_all_success(models):
    client = APIClient()
    client.force_authenticate(user=models.staff_user)
    response = client.get("/api/v1/surveys/")
    assert response.status_code == 200
    assert len(response.json()["results"]) == 2

@mark.django_db
def test_get_specific_survey_no_active_failed_no_authorized(models):
    client = APIClient()
    client.force_authenticate(user=models.normal_user)
    response = client.get("/api/v1/surveys/1/")
    assert response.status_code == 403
    assert list(response.json().keys()) == ["detail"]

@mark.django_db
def test_get_specific_survey_no_active_success(models):
    client = APIClient()
    client.force_authenticate(user=models.staff_user)
    data = {
        'id': models.survey1.id,
        'name': models.survey1.name,
        'questions': models.survey1.questions,
        'n_questions': models.survey1.n_questions,
        'active': models.survey1.active,
        'active_until': models.survey1.active_until,
        'created': models.survey1.created,
        'updated': models.survey1.updated
        }

    response = client.get("/api/v1/surveys/1/")
    assert response.status_code == 200
    assert response.json() == data

@mark.django_db
def test_get_specific_survey_active_success(models):
    client = APIClient()
    response = client.get("/api/v1/surveys/2/")
    data = {
        'id': models.survey2.id,
        'name': models.survey2.name,
        'questions': models.survey2.questions,
        'n_questions': models.survey2.n_questions,
        'active': models.survey2.active,
        'active_until': models.survey2.active_until,
        'created': models.survey2.created,
        'updated': models.survey2.updated
        }
    assert response.status_code == 200
    assert response.json() == data