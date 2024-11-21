from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from root_api.settings import MEDIA_URL
from .permissions import *
from .models import Survey, Response as ResponseModel
from .serializers import SurveySerializer, ResponseSerializer
from . services import export_questions_JSON, create_report_HTML

class SurveyViewSet(viewsets.ModelViewSet):
    serializer_class = SurveySerializer
    queryset = Survey.objects.all().order_by("id")
    def get_permissions(self):
        if(self.action == "destroy"):
            permission_classes = [IsSuperuser]
        elif(self.action == "respond"):
            permission_classes = [permissions.AllowAny]
        elif(self.action == "retrieve"):
            permission_classes = [SurveyIsActiveOrIsAdminUser]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail = True, methods = ["post"])
    def respond(self, request, pk = None):
        serializer = ResponseSerializer(data = request.data, context = {"pk": pk})
        if(serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    @action(detail = True, methods = ["get"])
    def confirmation(self, request, pk = None):
        if(request.GET.get("cc")):
            model = ResponseModel.objects.filter(survey = pk, confirmation_code = request.GET.get("cc")).first()
            if(model):
                return Response({"valid": True}, status = status.HTTP_200_OK)
            else:
                return Response({"valid": False}, status = status.HTTP_200_OK)
        else:
            return Response({"detail": 'Parâmetro de URL "cc" inexistente'}, status = status.HTTP_400_BAD_REQUEST)
    @action(detail = True, methods = ["get"])
    def json(self, request, pk = None):
        survey = self.get_object()
        file_name = export_questions_JSON(survey.questions, survey.name)
        return Response({"link": f"{MEDIA_URL}{file_name}"}, status = status.HTTP_200_OK)
    @action(detail = True, methods = ["get"])
    def report(self, request, pk = None):
        survey = self.get_object()
        serializer = ResponseSerializer(ResponseModel.objects.filter(survey = survey.id), many = True)
        if(serializer.data):
            file_name = create_report_HTML(survey, serializer.data)
            return Response({"link": f"{MEDIA_URL}{file_name}"}, status = status.HTTP_200_OK)
        return Response({"detail": "Não há respostas para gerar um relatório"}, status = status.HTTP_400_BAD_REQUEST)


