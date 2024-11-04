from pytest import fixture, mark
from datetime import datetime
from rest_framework.test import APIClient

from pgex_api.models import User, Survey

@fixture
def data_patch():
    data = {
        'id': 1,
        'name': 'name_test',
        'questions': {
            'question_about_b': [
                {'id': 1, 'question': 'test_question_1', 'is_descriptive': False},
                {'id': 2, 'question': 'test_question_2', 'is_descriptive': False}
            ],
        'question_about_a': [
            {'id': 3, 'question': 'test_question_3', 'is_descriptive': False},
            {'id': 4, 'question': 'test_question_4', 'is_descriptive': True}]
        },
        'n_questions': 4,
        'active': True,
        'active_until': None
        }
    return data

@fixture
def models():
    class Models():
        survey = Survey.objects.create(name = "old_name", n_questions = 1, questions = {"title": [{'id': 1, 'question': 'test_question_0', 'is_descriptive': False}]})
        normal_user = User.objects.create_user(email="test1@test.com", password="12345", first_name="Test1", last_name="T3")
        staff_user = User.objects.create_user(email="test2@test.com", password="12345", first_name="Test2", last_name="T2", is_staff=True)
        superuser = User.objects.create_superuser(email="test3@test.com", password="12345", first_name="Test3", last_name="T1")
    models = Models()
    return models

@mark.parametrize("field,incorrect_value", [["name", True], ["questions", "text"], ["active", 3], ["active_until", 3]])
@mark.django_db
def test_patch_validate_type_field(field, incorrect_value, models, data_patch):
    data_patch[field] = incorrect_value
    client = APIClient()
    client.force_authenticate(user=models.staff_user)
    response = client.patch("/api/v1/surveys/1/", data_patch, format="json")
    assert response.status_code == 400
    assert list(response.json().keys()) == [field]

@mark.django_db
def test_patch_failed_no_authorized(models, data_patch):
    client = APIClient()
    client.force_authenticate(user=models.normal_user)
    response = client.patch("/api/v1/surveys/1/", data_patch, format="json")
    assert response.status_code == 403
    assert list(response.json().keys()) == ["detail"]

@mark.django_db
def test_patch_failed_no_authenticated(data_patch):
    client = APIClient()
    response = client.patch("/api/v1/surveys/1/", data_patch, format="json")
    assert response.status_code == 401
    assert list(response.json().keys()) == ["detail"]

@mark.django_db
def test_patch_success_with_all_fields(models, data_patch):
    client = APIClient()
    client.force_authenticate(user=models.staff_user)
    response = client.patch("/api/v1/surveys/1/", data_patch, format="json")
    expected_data = {**data_patch,
        'created': models.survey.created,
        'updated': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
    assert response.status_code == 200
    assert response.json() == expected_data