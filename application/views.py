from django.contrib.auth import logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class Logout(APIView):
    def get(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)
