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
        
        

class OtpSorage(models.Model):
    email = models.CharField(null= False, blank = False)
    otp = models.CharField(null = False, blank = False, max_length = 6)
    otp_sent_time = models.IntegerField()#time.time()
    otp_unique_id = models.TextField() # a 100 digit unique id ( numbers only)
    
    def __str__(self):
        return "OtpStorage"