from django.shortcuts import render
from rest_framework.decorators import APIView

class Home(APIView):
    def get(self, request):
        return render(request, 'v2/landing_page.html')