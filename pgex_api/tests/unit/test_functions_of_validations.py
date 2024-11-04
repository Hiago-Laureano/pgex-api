from pytest import fixture, mark
from datetime import datetime
from rest_framework.exceptions import ValidationError
from pgex_api.serializers import SurveySerializer, ResponseSerializer, Survey

@fixture
def data():
    questions = {
            "question_about_b": [
                {"id": 1, "question": "test_question_1", "is_descriptive": False},
                {"id": 2, "question": "test_question_2", "is_descriptive": False}
            ],
            "question_about_a": [
                {"id": 3, "question": "test_question_3", "is_descriptive": False},
                {"id": 4, "question": "test_question_4", "is_descriptive": True}
            ]
        }
    return questions

@fixture
def models(data):
    class models():
        survey = Survey.objects.create(name = "old_name", n_questions = SurveySerializer().count_questions(data), questions = data)
        survey_expired = Survey.objects.create(name = "old_name2", n_questions = SurveySerializer().count_questions(data), questions = data, active_until = datetime(2022, 1, 1, 12, 12, 12))
    models = models()
    return models

def test_function_count_questions_return_count_of_questions(data):
    assert SurveySerializer().count_questions(data) == 4

def test_validate_questions_return_sent_parameter(data):
    survey = SurveySerializer()
    try:
        response = survey.validate_questions(data)
    except Exception as e:
        response = type(e)
    assert response == data

def test_validate_questions_without_is_descriptive_raise_error(data):
    survey = SurveySerializer()
    new_data = {**data, 
                "question_about_c": [
                {"id": 5, "question": "test_question_5", "is_descriptive": False},
                {"id": 6, "question": "test_question_6"}
            ]}
    try:
        response = survey.validate_questions(new_data)
    except Exception as e:
        response = type(e)
    assert response == ValidationError

def test_validate_questions_without_question_raise_error(data):
    survey = SurveySerializer()
    new_data = {**data, 
                "question_about_c": [
                {"id": 5, "question": "test_question_5", "is_descriptive": False},
                {"id": 6, "is_descriptive": False}
            ]}
    try:
        response = survey.validate_questions(new_data)
    except Exception as e:
        response = type(e)
    assert response == ValidationError

def test_validate_questions_without_id_raise_error(data):
    survey = SurveySerializer()
    new_data = {**data, 
                "question_about_c": [
                {"question": "test_question_5", "is_descriptive": False},
                {"id": 6, "question": "test_question_6", "is_descriptive": False}
            ]}
    try:
        response = survey.validate_questions(new_data)
    except Exception as e:
        response = type(e)
    assert response == ValidationError

def test_validate_questions_with_extra_field_raise_error(data):
    survey = SurveySerializer()
    new_data = {**data, 
                "question_about_c": [
                {"id": 5, "question": "test_question_5", "is_descriptive": False, "extra_field": 2},
                {"id": 6, "question": "test_question_6", "is_descriptive": False}
            ]}
    try:
        response = survey.validate_questions(new_data)
    except Exception as e:
        response = type(e)
    assert response == ValidationError

@mark.django_db
def test_validate_responses_return_sent_parameter(models):
    response_serializer = ResponseSerializer(context = {"pk": models.survey.id})
    data = {"1": "a", "2": "b", "3": "c", "4": "d"}
    try:
        response = response_serializer.validate_responses(data)
    except Exception as e:
        response = type(e)
    assert response == data

@mark.django_db
def test_validate_responses_with_incorrect_question_id_raise_error(models):
    response_serializer = ResponseSerializer(context = {"pk": models.survey.id})
    data = {"1": "a", "2": "b", "3": "c", "10": "d"}
    try:
        response = response_serializer.validate_responses(data)
    except Exception as e:
        response = type(e)
    assert response == ValidationError

@mark.django_db
def test_validate_responses_fewer_responses_than_questions_raise_error(models):
    response_serializer = ResponseSerializer(context = {"pk": models.survey.id})
    data = {"1": "a", "2": "b", "3": "c"}
    try:
        response = response_serializer.validate_responses(data)
    except Exception as e:
        response = type(e)
    assert response == ValidationError

@mark.django_db
def test_validate_responses_survey_not_found_raise_error():
    response_serializer = ResponseSerializer(context = {"pk": 20})
    data = {"1": "a", "2": "b", "3": "c"}
    try:
        response = response_serializer.validate_responses(data)
    except Exception as e:
        response = type(e)
    assert response == ValidationError

@mark.django_db
def test_validate_responses_survey_expired_active_until_raise_error(models):
    try:
        response = ResponseSerializer().validate_survey(models.survey_expired)
    except Exception as e:
        response = type(e)
    assert response == ValidationError
    assert models.survey_expired.active == False

@mark.django_db
def test_validate_responses_survey_not_expired_active_until_return_sent_parameter(models):
    data = models.survey
    try:
        response = ResponseSerializer().validate_survey(data)
    except Exception as e:
        response = type(e)
    assert response == data