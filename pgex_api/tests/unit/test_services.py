from pytest import mark, fixture
import json
import os
import re
import shutil
from root_api.settings import BASE_DIR
from pgex_api.models import Survey, Response as ResponseModel
from pgex_api.serializers import ResponseSerializer
from pgex_api.services import random_code, export_questions_JSON, create_report_HTML, create_mediaURL

@fixture
def models():
    class Data():
        name_path = "media_test"
        survey = Survey.objects.create(name = "form", n_questions = 1, questions = {
            "title": [{'id': 1, 'question': 'test_question_1', 'is_descriptive': False}],
            "title2": [{'id': 2, 'question': 'test_question_2', 'is_descriptive': True}]
        })
        response1 = ResponseModel.objects.create(survey = survey, responses = {"1": 4, "2": "test"})
        response2 = ResponseModel.objects.create(survey = survey, responses = {"1": 4, "2": "test"})
        response_serializer = ResponseSerializer(ResponseModel.objects.filter(survey = survey.id), many = True)
        def createPath(self):
            try:
                os.makedirs(f"{BASE_DIR}/{self.name_path}")
            except:
                pass
        def removePath(self):
            try:
                shutil.rmtree(f"{BASE_DIR}/{self.name_path}")
            except:
                pass
    return Data()

def test_if_function_random_code_generate_unique_random_string():
    array = []
    for i in range(0, 100):
        array.append(random_code())
    assert type(array[0]) == str
    assert len(array) == len(list(set(array)))

@mark.django_db
def test_function_create_mediaURL(models):
    create_mediaURL(models.name_path)
    assert os.path.exists(f"{BASE_DIR}/{models.name_path}") == True
    models.removePath()

@mark.django_db
def test_function_export_questions_JSON(models):
    file_name = export_questions_JSON(models.survey.questions, models.survey.name, dir = models.name_path)
    assert file_name == re.sub('[^a-zA-Z0-9]', '_', models.survey.name)+".json"
    assert os.path.isfile(f"{BASE_DIR}/{models.name_path}/{file_name}") == True
    f = open(f"{BASE_DIR}/{models.name_path}/{file_name}", "r", encoding="utf-8")
    assert json.load(f) == models.survey.questions
    f.close()
    models.removePath()

@mark.django_db
def test_function_create_report_HTML(models):
    file_name = create_report_HTML(models.survey, models.response_serializer.data, dir = models.name_path)
    assert file_name == re.sub('[^a-zA-Z0-9]', '_', models.survey.name)+".html"
    assert os.path.isfile(f"{BASE_DIR}/{models.name_path}/{file_name}") == True
    models.removePath()