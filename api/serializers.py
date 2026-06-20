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
        fields = ['id','username', 'email', 'last_login', 'date_joined', 'is_active', 'is_staff']
        

class OtpSorageSerializer(ModelSerializer):
    class Meta:
        model = OtpSorage
        fields = "__all__"
        


class AuthSorageSerializer(ModelSerializer):
    class Meta:
        model = AuthStorage
        fields = "__all__"
        
        
class allBackUpHistorySerializer(ModelSerializer):
    class Meta:
        model = allBackUpHistory
        fields = "__all__"
    