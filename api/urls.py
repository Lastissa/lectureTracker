from django.urls import path
from . import views
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', cache_page(60*60)(views.home)),

    # Single function
    path('viewData/', views.frontendViewData),
    path('viewData/json/', views.viewData),

    path('signup/', cache_page(60*60)(views.frontendbackupData)),
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
    path('batch_email/', views.batch_email),

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
    path("allAuth/", views.allAuth),
    path("allUser/", views.all_users),
    path("allActiveUser/", views.all_active_users),
    
    path("userDetails/", views.userDetails),
    
    #admin
     path('admin/', views.admin),
     path("admin/logout/", views.adminLogout),
     path("createAdminAccount/", views.createAdminAccount),
     path("createAdminAccountLogic/", views.createAdminAccountLogic),
     path("adminTokenGenerator/", views.adminTokenGenerator),
     
     #test
     path("test/", views.testing)
]