from django.shortcuts import render
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response

# Create your views here.


@api_view(['POST'])
def backup(request):
    return Response({"message": "Backup successful!"})