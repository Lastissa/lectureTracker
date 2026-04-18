from restframework.serializers import ModelSerializer
from .models import BackedUpData


class BackedUpDataSerializer(ModelSerializer):
    class Meta:
        model = BackedUpData
        fields = "__all__"
        
        
    