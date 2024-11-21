from pytest import fixture, mark
from rest_framework.test import APIClient
from root_api.settings import MEDIA_URL, BASE_DIR
import os

from pgex_api.models import User, Survey, Response

@fixture
def models():
    class Models():
        survey1 = Survey.objects.create(name = "name1", active = False, n_questions = 1, questions = {"title": [{'id': 1, 'question': 'test_question_0', 'is_descriptive': False}]})
        survey2 = Survey.objects.create(name = "name2", n_questions = 1, questions = {"title": [{'id': 1, 'question': 'test_question_0', 'is_descriptive': False}]})
        response = Response.objects.create(survey = survey1, responses = {"1": 4})
        response2 = Response.objects.create(survey = survey1, responses = {"1": 5})
        normal_user = User.objects.create_user(email="test1@test.com", password="12345", first_name="Test1", last_name="T3")
        staff_user = User.objects.create_user(email="test2@test.com", password="12345", first_name="Test2", last_name="T2", is_staff=True)
        superuser = User.objects.create_superuser(email="test3@test.com", password="12345", first_name="Test3", last_name="T1")
        def removeFile(self, file):
            try:
                os.remove(f"{BASE_DIR}/{MEDIA_URL}{file}")
            except:
                pass
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

@mark.django_db
def test_get_validation_of_confirmation_code_is_successful_with_valid_code(models):
    client = APIClient()
    client.force_authenticate(user=models.staff_user)
    response = client.get(f"/api/v1/surveys/{models.response.survey.id}/confirmation/?cc={models.response.confirmation_code}")
    assert response.status_code == 200
    assert response.json() == {"valid": True}

@mark.django_db
def test_get_validation_of_confirmation_code_is_failed_without_url_parameter(models):
    client = APIClient()
    client.force_authenticate(user=models.staff_user)
    response = client.get(f"/api/v1/surveys/{models.response.survey.id}/confirmation/")
    assert response.status_code == 400
    assert list(response.json().keys()) == ["detail"]

@mark.django_db
def test_get_validation_of_confirmation_code_is_successful_with_no_valid_code(models):
    client = APIClient()
    client.force_authenticate(user=models.staff_user)
    response = client.get(f"/api/v1/surveys/{models.response.survey.id}/confirmation/?cc=123")
    assert response.status_code == 200
    assert response.json() == {"valid": False}

@mark.django_db
def test_get_link_of_json_file_with_questions(models):
    client = APIClient()
    client.force_authenticate(user=models.staff_user)
    response = client.get(f"/api/v1/surveys/{models.survey1.id}/json/")
    assert response.status_code == 200
    assert response.json() == {"link": f"{MEDIA_URL}{models.survey1.name}.json"}
    models.removeFile(f"{models.survey1.name}.json")

@mark.django_db
def test_get_link_of_report_file_in_HTML(models):
    client = APIClient()
    client.force_authenticate(user=models.staff_user)
    response = client.get(f"/api/v1/surveys/{models.survey1.id}/report/")
    assert response.status_code == 200
    assert response.json() == {"link": f"{MEDIA_URL}{models.survey1.name}.html"}
    models.removeFile(f"{models.survey1.name}.html")