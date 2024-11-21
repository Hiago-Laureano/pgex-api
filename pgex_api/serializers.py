from rest_framework import serializers
from .models import Survey, Response
from datetime import datetime

class SurveySerializer(serializers.ModelSerializer):
    active_until = serializers.DateTimeField(format = "%d/%m/%Y", required = False, allow_null = True)
    class Meta:
        model = Survey
        fields = [
            "id",
            "name",
            "questions",
            "n_questions",
            "active",
            "active_until",
            "created",
            "updated"
        ]
        extra_kwargs = {
            "active": {"default": True},
            "n_questions": {"read_only": True}
        }
    def count_questions(self, questions):
        count = 0
        for i in questions.values():
            for j in i:
                count += 1
        return count

    def create(self, validated_data):
        validated_data["n_questions"] = self.count_questions(validated_data["questions"])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if(validated_data.get("questions")):
            validated_data["n_questions"] = self.count_questions(validated_data["questions"])
        return super().update(instance, validated_data)

    def validate_questions(self, value):
        valid = False
        if(type(value) == dict):
            stop = False
            for i in value.values():
                if(stop):
                    break
                for j in i:
                    if(list(j.keys()) == ["id", "question", "is_descriptive"]):
                        valid = True
                    else:
                        valid = False
                        stop = True
                        break
        if(valid):
            return value
        else:
            raise serializers.ValidationError("Formatação do JSON incorreta. Deve ser {'*your title for this list of question*': [{'id', 'question', 'is_descriptive'}]}")

class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = [
            "id",
            "survey",
            "responses",
            "confirmation_code",
            "created",
            "updated"
        ]
        extra_kwargs = {
            "confirmation_code": {"read_only": True}
        }
    def validate_survey(self, value):
        if(value.active):
            if(not value.active_until):
                return value
            elif(value.active_until > datetime.now() and value.active):
                return value
        value.active = False
        value.save()
        raise serializers.ValidationError("A pesquisa não está mais aberta")

    def validate_responses(self, value):
        pk = self.context["pk"]
        survey_target = Survey.objects.filter(id = pk).first()
        if(not survey_target):
            raise serializers.ValidationError("Pesquisa referênciada não encontrada")
        list_ids_questions = []
        for i in survey_target.questions.values():
            for j in i:
                list_ids_questions.append(str(j["id"]))
        if(sorted(list_ids_questions) != sorted(list(value.keys()))):
            raise serializers.ValidationError("Os ids das perguntas não estão batendo com os das respostas")
        if(len(value) == survey_target.n_questions):
            return value
        else:
            raise serializers.ValidationError("Número de respostas não é igual ao de perguntas da pesquisa")
