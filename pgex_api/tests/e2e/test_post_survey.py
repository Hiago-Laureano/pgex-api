from pytest import fixture, mark
from datetime import datetime
from rest_framework.test import APIClient
from pgex_api.serializers import SurveySerializer
from pgex_api.models import User, Survey

@fixture
def data_post():
    data = {
        'id': 2,
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
    class models():
        questions = {
            'question_about_b': [
                {'id': 1, 'question': 'test_question_1', 'is_descriptive': False},
                {'id': 2, 'question': 'test_question_2', 'is_descriptive': False}
            ],
            'question_about_a': [
                {'id': 3, 'question': 'test_question_3', 'is_descriptive': False},
                {'id': 4, 'question': 'test_question_4', 'is_descriptive': True}]
        }
        survey = Survey.objects.create(name = "old_name", n_questions = SurveySerializer().count_questions(questions), questions = questions)
        normal_user = User.objects.create_user(email="test1@test.com", password="12345", first_name="Test1", last_name="T3")
        staff_user = User.objects.create_user(email="test2@test.com", password="12345", first_name="Test2", last_name="T2", is_staff=True)
        superuser = User.objects.create_superuser(email="test3@test.com", password="12345", first_name="Test3", last_name="T1")
    models = models()
    return models

@mark.parametrize("field,incorrect_value", [["name", True], ["questions", "text"], ["active", 3], ["active_until", 3]])
@mark.django_db
def test_post_validate_type_field(field, incorrect_value, models, data_post):
    data_post[field] = incorrect_value
    client = APIClient()
    client.force_authenticate(user=models.staff_user)
    response = client.post("/api/v1/surveys/", data_post, format="json")
    assert response.status_code == 400
    assert list(response.json().keys()) == [field]

@mark.parametrize("field", ["name", "questions"])
@mark.django_db
def test_post_validate_is_required_field(field, models, data_post):
    del(data_post[field])
    client = APIClient()
    client.force_authenticate(user=models.staff_user)
    response = client.post("/api/v1/surveys/", data_post, format="json")
    assert response.status_code == 400
    assert list(response.json().keys()) == [field]

@mark.django_db
def test_post_failed_no_authorized(models, data_post):
    client = APIClient()
    client.force_authenticate(user=models.normal_user)
    response = client.post("/api/v1/surveys/", data_post, format="json")
    assert response.status_code == 403
    assert list(response.json().keys()) == ["detail"]

@mark.django_db
def test_post_failed_no_authenticated(data_post):
    client = APIClient()
    response = client.post("/api/v1/surveys/", data_post, format="json")
    assert response.status_code == 401
    assert list(response.json().keys()) == ["detail"]

@mark.django_db
def test_post_success_with_all_fields(models, data_post):
    client = APIClient()
    client.force_authenticate(user=models.staff_user)
    response = client.post("/api/v1/surveys/", data_post, format="json")
    expected_data = {**data_post,
        'created': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'updated': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
    assert response.status_code == 201
    assert response.json() == expected_data

@mark.django_db
def test_post_success_with_only_necessary_fields(models, data_post):
    client = APIClient()
    client.force_authenticate(user=models.staff_user)
    data = {"name": data_post["name"],
            "questions": data_post["questions"]
        }
    response = client.post("/api/v1/surveys/", data, format="json")
    expected_data = {**data_post,
        'created': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'updated': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
    assert response.status_code == 201
    assert response.json() == expected_data

@mark.django_db
def test_post_respond_success(models):
    client = APIClient()
    data_response = {"id": 1,
            "responses": {"1": "response1", "2": "response2", "3": "response3", "4": "response4"},
            "survey": models.survey.id
        }
    response = client.post("/api/v1/surveys/1/respond/", data_response, format="json")
    expected_data = {**data_response,
        'created': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'updated': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
    assert response.status_code == 201
    assert response.json() == expected_data

@mark.django_db
def test_post_respond_failed_not_fount_survey():
    client = APIClient()
    data_response = {"id": 1,
            "response": {"1": "response1", "2": "response2", "3": "response3", "4": "response4"},
            "survey": 100
        }
    response = client.post("/api/v1/surveys/1/respond/", data_response, format="json")
    assert response.status_code == 400
    assert list(response.json().keys()) == ["survey", "responses"]

@mark.django_db
def test_post_respond_failed_fewer_responses_than_questions_raise_error(models):
    client = APIClient()
    data_response = {"id": 1,
            "response": {"1": "response1", "2": "response2", "3": "response3"},
            "survey": models.survey.id
        }
    response = client.post("/api/v1/surveys/1/respond/", data_response, format="json")
    assert response.status_code == 400
    assert list(response.json().keys()) == ["responses"]

@mark.django_db
def test_post_respond_failed_incorrect_question_id_raise_error(models):
    client = APIClient()
    data_response = {"id": 1,
            "response": {"1": "response1", "2": "response2", "3": "response3", "10": "response10"},
            "survey": models.survey.id
        }
    response = client.post("/api/v1/surveys/1/respond/", data_response, format="json")
    assert response.status_code == 400
    assert list(response.json().keys()) == ["responses"]