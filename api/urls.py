from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),

    # Single function
    path('viewData/', views.frontendViewData),
    path('viewData/json/', views.viewData),

    path('backupData/', views.frontendbackupData),
    path('backupData/json/', views.backupData),

    path('deactivateAccount/', views.deactivateAccount),
    path('deactivateAccount/json/', views.deactivateAccount),
    
    path('deleteAccount/', views.deleteAccount),
    path('deleteAccount/json/', views.deleteAccount),
    
    path('reactivateAccount/', views.reactivateAccount),
    path('reactivateAccount/json/', views.reactivateAccount),

    # Mass functions
    path('deleteAllData/', views.deleteAllData),
    path('deleteAllData/json/', views.deleteAllData),

    path('viewAllData/', views.frontendViewAllData),
    path('viewAllData/json/', views.viewAllData),

    # Updates
    path('updatePassword/', views.frontendUpdatePassword),
    path('updatePassword/json/', views.updatePassword),

    path('updateEmail/', views.updateEmail),
    path('updateEmail/json/', views.updateEmail),

    path('updateUsername/', views.updateUsername),
    path('updateUsername/json/', views.frontendUpdatePassword),
    
    #others
    path('admin/', views.admin),
    path('api_doc/', views.api_inspector),
    
    path("login/", views.login),
    path("login/json/", views.login_json),

    path("cleartoken/", views.cleartoken),
    path("generatetoken/", views.generateToken),

    path("permanentLogin/", views.permanentLoginUnlessInvalidated),
    path("alltimeHistory/", views.allTimeBackUpHistory),
    
    
    
    path("ai/", views.ai_response), 
    
    path('otp/json/', views.otp),
    path('otp/', views.frontendOtp),
    
    path("allOtp/", views.allOtp),
    path("allAuth/", views.allAuth)
]