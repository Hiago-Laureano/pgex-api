import os
import re
from datetime import datetime
import json
import plotly.express as px
from root_api.settings import BASE_DIR

def random_code():
    return f"{os.urandom(10).hex()}{datetime.now().strftime('%d%m%y%H%M%S')}"

def create_mediaURL(path = "media"):
    if(not os.path.exists(f"{BASE_DIR}/{path}")):
        os.makedirs(f"{BASE_DIR}/{path}")


def create_pieChart(values):
    data = {
        "Avaliação": ["Insatisfatório", "Regular", "Bom", "Muito bom", "Excelente"],
        "Votos": values
    }
    chart = px.pie(data_frame=data, values="Votos", names="Avaliação")
    return chart

def export_questions_JSON(data, name, dir="media"):
    create_mediaURL(dir)
    path = f"{BASE_DIR}/{dir}/{re.sub('[^a-zA-Z0-9]', '_', name)}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return f"{re.sub('[^a-zA-Z0-9]', '_', name)}.json"

def create_report_HTML(survey, responses, dir="media"):
    create_mediaURL(dir)
    values = {}
    for i in responses:
        for j in i["responses"].keys():
            if j in values.keys():
                if(type(i["responses"][j]) == int):
                    values[j][i["responses"][j]-1] += 1
                else:
                    values[j].append(i["responses"][j])
            else:
                if(type(i["responses"][j]) == int):
                    values[j] = [0, 0, 0, 0, 0]
                    values[j][i["responses"][j]-1] += 1
                else:
                    values[j] = [i["responses"][j]]
    path = f"{BASE_DIR}/{dir}/{re.sub('[^a-zA-Z0-9]', '_', survey.name)}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write('<meta charset="utf-8"/>')
        f.write('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">')
        f.write('<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>')
        f.write('<h6 class="text-start ms-2">%s%s</h6>' %("Gerado em ", datetime.now().strftime("%d/%m/%Y às %H:%M")))
        f.write('<h1 class="text-center my-3">Relatório %s</h1>' %(survey.name))
        for i in survey.questions.keys():
            f.write('<h3 class="text-center mt-5 bg-danger text-white">%s</h3>' %(i))
            for j in survey.questions[i]:
                f.write('<h4 class="text-center mt-5">%s</h4>' %(j["question"]))
                if(j["is_descriptive"]):
                    f.write('<ul class="list-group mb-5">')
                    for comment in values[str(j["id"])]:
                        f.write('<li class="list-group-item">%s</li>' %(comment))
                    f.write('</ul>')
                else:
                    chart = create_pieChart(values[str(j["id"])])
                    f.write(chart.to_html(full_html=False, include_plotlyjs='cdn'))
    return f"{re.sub('[^a-zA-Z0-9]', '_', survey.name)}.html"