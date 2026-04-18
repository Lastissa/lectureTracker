from django.db import models

# Create your models here.

class BackedUpData(models.Model):
    data = models.TextField()
    lastBackUp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "backedUpData"