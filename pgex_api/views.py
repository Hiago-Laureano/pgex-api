from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import *
from .models import Survey
from .serializers import SurveySerializer, ResponseSerializer

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
    


