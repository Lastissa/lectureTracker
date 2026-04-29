from django.urls import path
from . import views


urlpatterns = [
    path('', views.home),
   #Single function
    path('viewData/', views.viewData), #query params for data collection

    path('backupData/', views.backupView),  #body for data collection
    
    path('deactivateAccount/', views.deactivateAccount) ,  #query params for data collection
    
    #Mass functions
    path('deleteAllData/', views.deleteAllData),  #query params for data collection
    
    path('viewAllData/', views.viewAllData),  #nothing needed for data collection
    
    #Updates
    path('updatePassword/', views.updatePassword),  #body for data collection
    
    path('updateEmail/', views.updateEmail),  #query params for data collection
    
    path('updateUsername/', views.updateUsername),  #Nothing for data collection
    
]