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
        
        
        
        
class AuthStorage(models.Model):
    #i used foreign key bcos i dont want unique to be true
    _user = models.ForeignKey(User, on_delete=models.CASCADE)
    auth_key = models.CharField(null = False, blank = False, max_length = 200) #random string mix of Aa0symbols
    expiration_time = models.IntegerField()#time.time()
    
    
#This to curb mistake backup overiding and reverse backup data
class allBackUpHistory(models.Model):
    _user = models.ForeignKey(User, on_delete=models.CASCADE)
    history = models.JSONField(null=True, blank=True, default=list)
    currentData = models.JSONField(null=True, blank=True, default=list)
    time = models.DateTimeField(auto_now=True,)
     
    def __str__(self):
         return "allBackUpHistory"
