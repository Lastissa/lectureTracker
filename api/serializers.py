from rest_framework.serializers import ModelSerializer
from .models import *
from django.contrib.auth.models import User


class HistorySerializer(ModelSerializer):
    class Meta:
        model = History
        fields = "__all__"
        
    
        
        
class CurrentDataSerializer(ModelSerializer):
    class Meta:
        model = CurrentData
        fields = "__all__"


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'email', 'password', 'last_login', 'date_joined', 'is_active']
        

class OtpSorageSerializer(ModelSerializer):
    class Meta:
        model = OtpSorage
        fields = "__all__"
        


class AuthSorageSerializer(ModelSerializer):
    class Meta:
        model = AuthStorage
        fields = "__all__"