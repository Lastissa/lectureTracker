import random

from django.shortcuts import render
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from .serializers import *
from .models import *
from django.http import JsonResponse
from django.contrib.auth.models import User
import datetime as dt
from django.core.mail import send_mail
from django.conf import settings



#To get one data from the db
@api_view(['GET'])
def viewData(request):
    requestEmail =  request.query_params.get('email', 'default').upper()
    requestPassword =  request.query_params.get('password', 'a')
  #Get the email if exist  
    userObjects = User.objects.filter(email__iexact = requestEmail).first()
    if userObjects is not None:
        if len(requestPassword.strip()) < 2:
            return JsonResponse({'message': 'password required'})
        if userObjects.check_password(requestPassword):
            historyObjects = History.objects.get(_user = userObjects)
            CurrentDataObjects = CurrentData.objects.get(_user = userObjects)
            
            historySerializer =  HistorySerializer(historyObjects ,many = False)
            currentDataSerializer = CurrentDataSerializer(CurrentDataObjects, many = False)
            userSerializer = UserSerializer(userObjects, many = False)
            
            return JsonResponse({'history': historySerializer.data, 'currentData': currentDataSerializer.data, 'user': userSerializer.data}, safe=False)
        
        else:
            return JsonResponse({'message': 'Incorrect password'})

    else:
        return JsonResponse({"message":"user not found", "hint": "add email to the query param"})
        
    






#for the frontend aspect - GET ONE DATA 
@api_view(['GET', "POST", "PATCH", "PUT"])
def frontendViewData(request):
    #check if the query params is empty , if it is return a sleek UI for them to see
    requestEmail = request.query_params.get('email', 'empty').strip().upper()
    requestPassword = request.query_params.get('password', 'empty').strip()
    if requestEmail == "empty" or requestPassword == "empty":
        return render(request, "api/request_incomplete/viewData_welcome.html" )
    #mean user have typed correctly clicked email
    else:
        #Check if user exist
        userFilter = User.objects.filter(email__iexact = requestEmail).first()
        if userFilter is not None:
            #user exist
            #check password
            userObjects = User.objects.get(email__iexact = requestEmail)
            if userObjects.check_password(requestPassword):
                #correct password
                #return user data 
                historyObjects = History.objects.get(_user = userObjects)
                CurrentDataObjects = CurrentData.objects.get(_user = userObjects)
                
                historySerializer =  HistorySerializer(historyObjects ,many = False)
                currentDataSerializer = CurrentDataSerializer(CurrentDataObjects, many = False)
                userSerializer = UserSerializer(userObjects, many = False)
                #Filter the password and id out
                userPersonal = userSerializer.data
                userPersonal.pop('id', None)
                userPersonal.pop('password', None)
                
                return render(request, "api/request_incomplete/viewData_success.html", {
                    'user': userPersonal,
                    'history': historySerializer.data,
                    'currentData': currentDataSerializer.data
                })
            
                
            else:
                #wrong password
                return render(request, "api/request_incomplete/viewData_wrong_password.html")
        
        else:
            #user does not exist
            return  render(request, "api/request_incomplete/viewData_no_user.html")
        
        







#To add and update data(except update username and email) to the db,
@api_view(['POST', 'PATCH'])
def backupData(request):
    requestUserName =  request.data.get('username', '').strip().upper()
    requestEmail =  request.data.get('email', '').strip().upper()
    requestPassword =  request.data.get('password', '')
    requestHistory = request.data.get('history', [])
    requestCurrentData = request.data.get('currentData',[] )
    
    #Check if user already exists, if so, update the data, if not, create a new, currentData and history object
    userObject = User.objects.filter(email__iexact = requestEmail).first()

    if userObject is not None:
       if userObject.check_password(requestPassword):
           #update user
           #check if the username the user want to use have not been taken
           userNameCheck= User.objects.filter(username = requestUserName).first()
           if userNameCheck is not None:
               return Response({"message": "username is not available"})
           #check if username is not empty to update
           if len(requestUserName ) > 0:
                userserializer = UserSerializer(userObject, data = {'last_login': dt.datetime.now(), 'username' : requestUserName}, partial = True)
           #the user did not inclide username for update
           else:
                userserializer = UserSerializer(userObject, data = {'last_login': dt.datetime.now()}, partial = True)
                print(userserializer)
           if userserializer.is_valid():
               userserializer.save()
           else:
               return Response({"message": "userSerializer failed"})
           currenDataObject = CurrentData.objects.get(_user = userObject)
           CurrentDataserializer = CurrentDataSerializer(currenDataObject, data = {'data': requestCurrentData}, partial = True)
           if CurrentDataserializer.is_valid():
               CurrentDataserializer.save()
           else:
               return Response({"message": "currentSerializer failed"})
           #update the history data
           historyObject = History.objects.get(_user = userObject)
           Historyserializer = HistorySerializer(historyObject, data = {'data': requestHistory}, partial = True)
           if Historyserializer.is_valid():
               Historyserializer.save()
           else:
               return Response({"message": "historySerializer failed"})
           return Response({'message': 'updated success'}, status=200)
       else:
           return Response({'message': 'Incorrect password'}, status=401)
        
    elif userObject is None:
        #check if the username is empty or missing
        if len(requestUserName.strip() )< 1:
            return Response({"message" : "username or email required"})
        #Create a new user, currentData and a new history object
        userObject = User.objects.create_user(username= requestUserName.upper(), password= requestPassword, email= requestEmail) 
        historyObject = History.objects.create(
            data = requestHistory,
            _user = userObject
        )
        currentDataObject = CurrentData.objects.create(
            data = requestCurrentData,
            _user = userObject
        )
        historySerializer = HistorySerializer(historyObject, many = False)
        CurrentDataserializer = CurrentDataSerializer(currentDataObject, many = False)

        return Response('Account Created', status=201)








@api_view(["GET"])
def frontendbackupData(request):
    return render(request, "api/request_incomplete/nopage.html")







#View all data at once
@api_view(['GET'])
def viewAllData(request):
    historyObjects = History.objects.all()
    CurrentDataObjects = CurrentData.objects.all()
    userObjects = User.objects.all()
    historySerializer =  HistorySerializer(historyObjects ,many = True)
    currentDataSerializer = CurrentDataSerializer(CurrentDataObjects, many = True)
    userSerializer = UserSerializer(userObjects, many = True)
    
    
    return JsonResponse({'history': historySerializer.data, 'currentData': currentDataSerializer.data, 'users': userSerializer.data}, safe=False)







#for the frontend aspect -VIEW ALL DATA
@api_view(["GET"])
def frontendViewAllData(request):
    historyObjects = History.objects.all()
    CurrentDataObjects = CurrentData.objects.all()
    userObjects = User.objects.all()
    historySerializer =  HistorySerializer(historyObjects ,many = True)
    currentDataSerializer = CurrentDataSerializer(CurrentDataObjects, many = True)
    userSerializer = UserSerializer(userObjects, many = True)
    
    
    return render(request, "api/request_incomplete/viewAllData_welcome.html", {'history': historySerializer.data, 'currentData': currentDataSerializer.data, 'users': userSerializer.data})









#Deactivate single account by setting is_active to false
@api_view(['DELETE', 'GET'])
def deactivateAccount(request):
    _userName = request.query_params.get('username', 'default')
    _email = request.query_params.get('email', 'default')
    _password = request.query_params.get('password', 'default')
    
    try:
        object = User.objects.get(username = _userName, email = _email)
    except:
        return JsonResponse({'message': 'User not found'})
    if object.check_password(_password):
        userserializer = UserSerializer(object, data = {'is_active': False}, partial = True)
        if userserializer.is_valid():
            userserializer.save()
        return JsonResponse({'message': f'{_userName} deactivated'})
    else:
        return JsonResponse({'message': 'Incorrect password'})
    
    return JsonResponse({'message': f'{request.query_params.get("username", "default")} deleted'})
    
    
    
    


#Delete all user; use with caution
@api_view(['DELETE', 'GET'])
def deleteAllData(request):
    goAhead = request.query_params.get('go_ahead', 'default')
    if goAhead != 'yes':
        return JsonResponse({'message': 'Unauthorized', 'hint': 'go_ahead: yes'})
    else:
        User.objects.all().delete()
        return JsonResponse({'message': 'All data deleted'})




#@api_view(['DELETE', 'GET'])
#def deleteAllData(request):
#    _auth = request.query_params.get('user', 'default')
#    password = request.query_params.get('password', 'default')
#    if 1 != 1:
#        return JsonResponse({'message': 'Unauthorized', 'hint': 'user: admin\nPassword: my main password'})
#    User.objects.all().delete()
#    return JsonResponse({'message': 'All data deleted'})







import random
import time
@api_view(['GET', 'PATCH', 'POST'])
def otp(request):
    if len(request.data.keys()) < 1:
        return JsonResponse({"message": "email required"})
        
    requestEmail = request.data.get("email", "empty").strip().upper()
    
    #send otp to the email and save the credentials into the db using time.time(), the validity is only 10 minutes (600 sec)
    if requestEmail == "empty":
        return JsonResponse ({"message": "Email cannot  be empty"})
    else:
        #email is given, check if it is valid.
        if "@GMAIL.COM" not in requestEmail:
            return JsonResponse({"message": "Not a valid email"})
        else:
            #email is valid, proceed to send otp
            #but what kind of otp ? the query_params handle that
            
            numbers = "0123456789"
            otp = ""
            otp_unique_id = ""
            for i in range(100):
                otp_unique_id += str(random.choice(numbers))
            for i in range(6):
                otp +=str(random.choice(numbers))
            otp_sent_time = time.time()

            #send mail
            requestHeading= request.query_params.get("heading" , "").upper()
            
            #mail for reseting username only
            if requestHeading == "USERNAME RESET":
                domain = request.build_absolute_uri('/')
                send_mail(
            subject="Username Reset OTP",
            message=f"Use the OTP {otp} sent to reset your Username.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[requestEmail],
            html_message=f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>OTP Verification</title>
    </head>
    <body style="margin:0; padding:0; background-color:#f4f6f8; font-family:Arial, sans-serif;">
    
      <div style="max-width:500px; margin:40px auto; background:#ffffff; border-radius:12px; padding:30px; box-shadow:0 4px 20px rgba(0,0,0,0.05);">
        
        <h2 style="text-align:center; color:#333;">Username Reset</h2>
    
        <p style="color:#555;">Hello,</p>
    
        <p style="color:#555;">
          You requested to reset your Username. Use the OTP below to proceed.
        </p>
    
        <!-- OTP BOXES -->
        <div style="text-align:center; margin:30px 0;">
          {"".join([
            f'<span style="display:inline-block; width:45px; height:55px; line-height:55px; margin:5px; font-size:22px; font-weight:bold; color:#2d89ef; border:1px solid #ddd; border-radius:8px; background:#f9fbff;">{digit}</span>'
            for digit in otp
          ])}
        </div>
    
        <p style="text-align:center; color:#888;">
          This OTP expires in <b>10 minutes</b>.
        </p>
    
        <!-- BUTTON -->
        <div style="text-align:center; margin:30px 0;">
          <a href="{domain}updateUsername/?otp={otp}&otp_unique_id={otp_unique_id}&otp_sent_time={int(otp_sent_time)}&email={requestEmail}"
             style="background:#2d89ef; color:#fff; padding:12px 25px; text-decoration:none; border-radius:6px; font-weight:bold; display:inline-block;">
             Reset Username
          </a>
        </div>
    
        <p style="color:#999; font-size:12px; text-align:center;">
          If you did not request this, please ignore this email.
        </p>
    
      </div>
    
    </body>
    </html>
    """
        )
        
            #mail for resetting email only
            elif requestHeading == "EMAIL RESET":
                domain = request.build_absolute_uri('/')
                send_mail(
        subject="Email Reset OTP",
        message=f"Use the OTP {otp} sent to reset your password.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[requestEmail],
        html_message=f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>OTP Verification</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f6f8; font-family:Arial, sans-serif;">

  <div style="max-width:500px; margin:40px auto; background:#ffffff; border-radius:12px; padding:30px; box-shadow:0 4px 20px rgba(0,0,0,0.05);">
    
    <h2 style="text-align:center; color:#333;">Email Reset</h2>

    <p style="color:#555;">Hello,</p>

    <p style="color:#555;">
      You requested to reset your email. Use the OTP below to proceed.
    </p>

    <!-- OTP BOXES -->
    <div style="text-align:center; margin:30px 0;">
      {"".join([
        f'<span style="display:inline-block; width:45px; height:55px; line-height:55px; margin:5px; font-size:22px; font-weight:bold; color:#2d89ef; border:1px solid #ddd; border-radius:8px; background:#f9fbff;">{digit}</span>'
        for digit in otp
      ])}
    </div>

    <p style="text-align:center; color:#888;">
      This OTP expires in <b>10 minutes</b>.
    </p>

    <!-- BUTTON -->
    <div style="text-align:center; margin:30px 0;">
      <a href="{domain}updateEmail/?otp={otp}&otp_unique_id={otp_unique_id}&otp_sent_time={int(otp_sent_time)}&email={requestEmail}"
         style="background:#2d89ef; color:#fff; padding:12px 25px; text-decoration:none; border-radius:6px; font-weight:bold; display:inline-block;">
         Reset Email
      </a>
    </div>

    <p style="color:#999; font-size:12px; text-align:center;">
      If you did not request this, please ignore this email.
    </p>

  </div>

</body>
</html>
"""
    )
    
            #email for paswore reset only
            elif requestHeading == "PASSWORD RESET":
                domain = request.build_absolute_uri('/')
                send_mail(
            subject="Password Reset OTP",
            message=f"Use the OTP {otp} sent to reset your password.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[requestEmail],
            html_message=f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>OTP Verification</title>
    </head>
    <body style="margin:0; padding:0; background-color:#f4f6f8; font-family:Arial, sans-serif;">
    
      <div style="max-width:500px; margin:40px auto; background:#ffffff; border-radius:12px; padding:30px; box-shadow:0 4px 20px rgba(0,0,0,0.05);">
        
        <h2 style="text-align:center; color:#333;">Password Reset</h2>
    
        <p style="color:#555;">Hello,</p>
    
        <p style="color:#555;">
          You requested to reset your password. Use the OTP below to proceed.
        </p>
    
        <!-- OTP BOXES -->
        <div style="text-align:center; margin:30px 0;">
          {"".join([
            f'<span style="display:inline-block; width:45px; height:55px; line-height:55px; margin:5px; font-size:22px; font-weight:bold; color:#2d89ef; border:1px solid #ddd; border-radius:8px; background:#f9fbff;">{digit}</span>'
            for digit in otp
          ])}
        </div>
    
        <p style="text-align:center; color:#888;">
          This OTP expires in <b>10 minutes</b>.
        </p>
    
        <!-- BUTTON -->
        <div style="text-align:center; margin:30px 0;">
          <a href="{domain}updatePassword/?otp={otp}&otp_unique_id={otp_unique_id}&otp_sent_time={int(otp_sent_time)}&email={requestEmail}"
             style="background:#2d89ef; color:#fff; padding:12px 25px; text-decoration:none; border-radius:6px; font-weight:bold; display:inline-block;">
             Reset Password
          </a>
        </div>
    
        <p style="color:#999; font-size:12px; text-align:center;">
          If you did not request this, please ignore this email.
        </p>
    
      </div>
    
    </body>
    </html>
    """
        )
            #the requestHeading did not return something i recognize
            else:
                return JsonResponse({"message": "Failure"})
                
    #bckup to the otpStorage
            otpObject = OtpSorage.objects.create(email = requestEmail, otp = otp, otp_sent_time = otp_sent_time, otp_unique_id = otp_unique_id)
            serializer = OtpSorageSerializer(otpObject, many = False)
            #no nees to return the unique_id and the otp cos the link reset button will do the righr thing
            #return JsonResponse(serializer.data)
            
            return JsonResponse({"message": "success"})
        
        
        
    
    
    
    
   
#otp frontend 
@api_view(["GET"])
def frontendOtp(request):
    requestHeading= request.query_params.get("heading" , "").upper()
    return render(request, "api/request_incomplete/otp_welcome.html", {"heading" : requestHeading})







@api_view(['PATCH', 'POST', 'GET'])
def updatePassword(request):
    if len(request.query_params.keys()) ==0:
        return Response({"message": "email required!!!"}) 
        
    requestEmail = request.query_params.get("email" , "empty").strip().upper()
    otp = request.query_params.get("otp", '')
    otp_sent_time = request.query_params.get("otp_sent_time", 0)#use time.time() to see the diff and check if it don reach 600 diff
    otp_unique_id = request.query_params.get("otp_unique_id", '')
    new_password = request.query_params.get("new_password", '').strip()
    
    #Check if email exist
    if requestEmail == "UPPER":
        return Response({"message": "email missing"})
    elif otp_sent_time == 0:
        return Response({"message": "otp_sent_time is missing"})
    elif len(otp_unique_id) < 1:
        return Response({"message": "otp_unique_id is missing"})
    elif otp == "":
        return Response({"message": "otp  is missing"})
    else:
        #Check if the credentials exist
        object = OtpSorage.objects.filter(email__iexact = requestEmail, otp = otp, otp_sent_time = otp_sent_time, otp_unique_id= otp_unique_id).first()
    if object is None:
        return Response({"message": "invalid credentials"})
    else:
        #credentials is valid, check if time never expire
        if time.time() - int(otp_sent_time) > 600:
            return Response({"message": "otp expired"} )
        else:
            #time never expire , check new password validity.
            if len(new_password) < 2:
                return Response({"message" : "new password too short"})
            else:
                #road clear
                userObject = User.objects.get(email__iexact = requestEmail )
                userObject.set_password(new_password)
                userObject.save()
                return Response({"message" : "success"})
            






@api_view(['PATCH', 'POST', 'GET'])
def  frontendUpdatePassword(request):
    
    requestEmail = request.query_params.get("email" , "empty").strip().upper()
    otp = request.query_params.get("otp", '')
    otp_sent_time = request.query_params.get("otp_sent_time", 0)#use time.time() to see the diff and check if it don reach 600 diff
    otp_unique_id = request.query_params.get("otp_unique_id", '')
    
    #if any data missing, return a page not allowed UI 
    if requestEmail == "EMPTY" or len(otp) < 2 or otp_sent_time == 0 or len(otp_unique_id) < 2 :
        return render(request, "api/request_incomplete/updatePassword_acces_not_allowed.html")
    #do a quick validity check with the otp_sent_time and see of the otp never expire, it it has, return "link expired" 
    else:
      if (time.time() - int(otp_sent_time)) > 600:
          return render(request, "api/request_incomplete/updatePassword_link_expired.html")
      
    #if no data is missing and the otp still valid, return a html where the user input the otp and new password and valodate it against db
    return Response("g")







@api_view(['PATCH', 'GET'])
def updateEmail(request):
    requestOldEMail = request.query_params.get('old_email', '').upper()
    requestNewEMail = request.query_params.get('new_email', '').upper()
    requestPassword = request.query_params.get('password', '')
    
    #Check if email is in system
    try:
        userObject = User.objects.get(email = requestOldEMail)
        if userObject.check_password(requestPassword):
            userserializer = UserSerializer(data = {'email': requestNewEMail}, partial = True)
            if userserializer.is_valid():
                userserializer.save()
                return JsonResponse({'message': 'Email updated successfully'})
        else:
            return JsonResponse({'message': 'Incorrect password'})
    except User.DoesNotExist:
        return JsonResponse({'message': 'User not found'})
    
    except Exception as e:
        return JsonResponse({'message': 'An error occurred', 'error': str(e)}, status=500)
        




@api_view(['PATCH', 'POST'])
def updateUsername(request):
    pass




# swagger ui clone
from django.urls import get_resolver
from django.shortcuts import render

def api_inspector(request):
    resolver = get_resolver()
    urls = []

    def extract(patterns, prefix=""):
        for p in patterns:
            if hasattr(p, 'url_patterns'):
                extract(p.url_patterns, prefix + str(p.pattern))
            else:
                full_path = prefix + str(p.pattern).strip("/")
                full_path = full_path.replace("^", "").replace("$", "")

                # ❌ remove admin
                if full_path.startswith("admin"):
                    continue

                # ❌ ONLY KEEP JSON ENDPOINTS
                if not full_path.endswith("json"):
                    continue

                urls.append(full_path)

    extract(resolver.url_patterns)

    endpoint_data = []

    for url in urls:
        key = url.split("/")[0]

        endpoint_data.append({
            "url": url,
            "full_url": f"/{url}",   # 🔥 for redirection
            "doc": API_DOC.get(key)
        })

    return render(request, "api/request_incomplete/api_inspector.html", {
        "endpoints": endpoint_data
    })




#This is for the homepage
@api_view(['GET'])
def home(request):
    return render(request, 'api/homehtml.html')


API_DOC = {
    "viewData": {
        "input": "query",
        "query_params": ["email(string)", "password(string)"],
        "body": None,
        "description": "Fetch a single user with history and current data"
    },

    "backupData": {
        "method": ["POST", "PATCH"],
        "input": "body",
        "query_params": None,
        "body": ["username(string)", "email(string)", "password(string)", "history(List(dict))", "currentDatahistory(List(dict))"],
        "description": "Create or update user data, history, and current data"
    },

    "updatePassword": {
        "method": ["PATCH", "POST"],
        "input": "body",
        "body": ["email", "old_password", "new_password"],
        "description": "Change user password securely"
    },

    "updateEmail": {
        "method": ["PATCH", "GET"],
        "input": "query",
        "query_params": ["old_email", "new_email", "password"],
        "body": None,
        "description": "Update user email address"
    },

    "updateUsername": {
        "method": ["PATCH", "POST"],
        "input": "body",
        "body": None,
        "description": "Update username (not implemented yet)"
    },

    "viewAllData": {
        "method": "GET",
        "input": "none",
        "query_params": None,
        "body": None,
        "description": "Returns all users, history, and current data"
    },

    "deactivateAccount": {
        "method": ["DELETE", "GET"],
        "input": "query",
        "query_params": ["username", "email", "password"],
        "body": None,
        "description": "Deactivate a user account"
    },

    "deleteAllData": {
        "method": ["DELETE", "GET"],
        "input": "query",
        "query_params": ["go_ahead"],
        "body": None,
        "description": "Danger: deletes all users"
    }
}