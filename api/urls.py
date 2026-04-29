from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),

    # Single function
    path('viewData/', views.frontendViewData),
    path('viewData/json/', views.viewData),

    path('backupData/', views.backupView),
    path('backupData/json/', views.backupView),

    path('deactivateAccount/', views.deactivateAccount),
    path('deactivateAccount/json/', views.deactivateAccount),

    # Mass functions
    path('deleteAllData/', views.deleteAllData),
    path('deleteAllData/json/', views.deleteAllData),

    path('viewAllData/', views.viewAllData),
    path('viewAllData/json/', views.viewAllData),

    # Updates
    path('updatePassword/', views.updatePassword),
    path('updatePassword/json/', views.updatePassword),

    path('updateEmail/', views.updateEmail),
    path('updateEmail/json/', views.updateEmail),

    path('updateUsername/', views.updateUsername),
    path('updateUsername/json/', views.updateUsername),
]