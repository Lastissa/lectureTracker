from django.urls import path
from . import views


urlpatterns = [
    path('', views.home),
   #Single function
    path('viewData/', views.viewData),

    path('backupData/', views.backupView),
    
    path('deactivateAccount/', views.deactivateAccount) ,      
    
    #Mass functions
    path('deleteAllData/', views.deleteAllData),
    
    path('viewAllData/', views.viewAllData),
    
    #Updates
    path('updatePassword/', views.updatePassword),
    
    path('updateEmail/', views.updateEmail),
    
    path('updateUsername/', views.updateUsername),
    
]