#Class for histry of backed up data, including the data and the date 
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
#History of backed up data, including the data and the date
class History(models.Model):
    data = models.JSONField(null=True, blank=True, default=list)
    _user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return "History"
    
    
#For the user current data
class CurrentData(models.Model):
    data = models.JSONField(null=True, blank=True, default=list)
    _user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return "CurrentData"