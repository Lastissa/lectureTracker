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
import os




#To get one data from the db
@api_view(['GET', "POST"])
def viewData(request):
    requestEmail =  request.query_params.get('email', 'default').upper().strip()
    requestPassword =  request.query_params.get('password', 'a')
    request_auth_key = request.query_params.get("auth_key", None)
    request_data_auth_key = request.data.get("auth_key", None) #For mobile usage to verify token and to invalidate long term tokens
    
    specialAccessForAuthKey = False; #for auth key so as to skip password checking
    #check if the email in the param exist
    if requestEmail == "DEFAULT":return JsonResponse({"message":"user not found", "hint": "add email to the query param"})
  #Get the email if exist  
    userObjects = User.objects.filter(email__iexact = requestEmail).first()
    if userObjects is not None:
        #check if the auth_key exist
        if request_auth_key != None or request_data_auth_key != None:
            authObject = AuthStorage.objects.filter(_user__email__iexact = requestEmail, auth_key = request_auth_key).first()
            authObject2 = AuthStorage.objects.filter(_user__email__iexact = requestEmail, auth_key = request_data_auth_key).first()
            #check if the auth key exist in the db
            if authObject != None or authObject2 != None:
                #authobject2 is the long tern auth_jey
                if authObject2 is not None:
                    #give access to data by chaging value of specialAccessForAuthKey
                    specialAccessForAuthKey = True
                #authobject is the short term auth_key
                elif authObject is not None:
                    #check if token is nt expired yet
                    if (time.time() - authObject.expiration_time) < 1200:
                        #give access to data by chaging value of specialAccessForAuthKey
                        specialAccessForAuthKey = True
                
                else:
                    return JsonResponse({"message" : f"Token expired "})
            #if the authobjet2 is none mean that particular session on that device have expired, 
            elif authObject2 is None:
                return JsonResponse({"message": f"session expired"}, status = 401)
        elif len(requestPassword.strip()) < 2 :
            if specialAccessForAuthKey: pass
            else: return JsonResponse({'message': f'password required {request_data_auth_key}'})
        #Check if the is_active is False
        if userObjects.is_active == False: return JsonResponse({"message": "account deactivated"})
        if userObjects.check_password(requestPassword) or specialAccessForAuthKey :
            historyObjects = History.objects.get(_user = userObjects)
            #everything id accutate, lets go
            CurrentDataObjects = CurrentData.objects.get(_user = userObjects)
            
            historySerializer =  HistorySerializer(historyObjects ,many = False)
            currentDataSerializer = CurrentDataSerializer(CurrentDataObjects, many = False)
            userSerializer = UserSerializer(userObjects, many = False)
            
            #Edit the userObjects to remove password from the output and format the last login and date join properly
            tempDict = userSerializer.data
            tempDict.pop("password", None)
            last_login= tempDict.pop("last_login", None)
            if last_login != None:
                last_login = dt.datetime.fromisoformat(f"{last_login}")
                last_login = last_login.strftime("%d %B,%Y %H:%M:%S")
            date_joined = tempDict.pop("date_joined", None)
            date_joined = dt.datetime.fromisoformat(f"{date_joined}")
            date_joined = date_joined.strftime("%d %B,%Y %H:%M:%S")

            #add back the formatted data
            
            tempDict.update({"last_login" : last_login, "date_joined" : date_joined})
            
            #return only the data key in historySerializer.data
            try:
                historyToReturn = historySerializer.data["data"]
            except:
                historyToReturn = historySerializer.data
                
             #return only the data key in currentDataSerializer.data
            try:
                 currentDataToReturn = currentDataSerializer.data["data"]
            except:
                 currentDataToReturn = currentDataSerializer.data
            return JsonResponse({'history': list(reversed(historyToReturn)), 'currentData': currentDataToReturn, 'user': tempDict, 'message': 'success'}, safe=False)
        
        else:
            return JsonResponse({'message': 'Incorrect password'}, status = 401)

    else:
        return JsonResponse({"message":"user not found"})
        
    
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
                #Check if the is_active is False
                if userObjects.is_active == False:
                    return render(request, "api/request_incomplete/viewData_account_deactivated.html")
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
                 #Edit the userObjects to remove password from the output and format the last login and date join properly                tempDict.pop("password", None)
                last_login= userPersonal.pop("last_login", None)
                if last_login == None:
                    last_login = None
                else:
                    last_login = dt.datetime.fromisoformat(last_login)
                    last_login = last_login.strftime("%d %B,%Y %H:%M:%S")
                date_joined = userPersonal.pop("date_joined", None)
                date_joined = dt.datetime.fromisoformat(date_joined)
                date_joined = date_joined.strftime("%d %B,%Y %H:%M:%S")

                #add back the formatted data
                userPersonal.update({"last_login" : last_login, "date_joined" : date_joined})
            
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
@api_view(['POST', 'PATCH', "GET"])
def backupData(request):
    requestUserName =  request.data.get('username', '').strip().upper()
    requestEmail =  request.data.get('email', '').strip().upper()
    requestPassword =  request.data.get('password', '')
    requestHistory = request.data.get('history', [])
    requestCurrentData = request.data.get('currentData',[] )
    auth_key = request.data.get("auth_key", None)
    result = None
    
    #I cant proof check 
    
    
    #Check if user already exists, if so, update the data, if not, create a new, currentData and history object
    userObject = User.objects.filter(email__iexact = requestEmail).first()


    #Check if auth_key is none and just pass, if its not none, do not allow backup and give a response expired with a status code of 409, 
    if auth_key != None:
        if len(auth_key) < 98:
            return JsonResponse({"message": "session expired"}, status = 401)
        result = AuthStorage.objects.filter(_user = userObject, auth_key = auth_key).first()
        if result == None:
            return JsonResponse({"message": "session expired"}, status = 401)
        
    if userObject is not None:
       if userObject.check_password(requestPassword) or result != None:
           #update user
           #check if the username the user want to use have not been taken
           userNameCheck= User.objects.filter(username = requestUserName).first()
           if userNameCheck is not None and userNameCheck.email.upper() != requestEmail.upper() and userObject.check_password(requestPassword):
               return Response({"message": "username is not available"}, status=400)
           #check if username is not empty to update
           if len(requestUserName ) > 0:
                userserializer = UserSerializer(userObject, data = {'last_login': dt.datetime.now(), 'username' : requestUserName}, partial = True)
           #the user did not inclide username for update
           #before update, check if there is a diff between the old data and incoming one
           lastBackedUp = allBackUpHistory.objects.filter(_user = userObject).last()
           #check if last backup exist
           if lastBackedUp:
               if lastBackedUp.history == requestHistory and lastBackedUp.currentData == requestCurrentData:
                return JsonResponse({"message" : "No new Data to BackUp"}, status = 203)
           else:
                userserializer = UserSerializer(userObject, data = {'last_login': dt.datetime.now()}, partial = True)
           if userserializer.is_valid():
               userserializer.save()
           else:
               return Response({"message": "userSerializer failed"})
           currenDataObject = CurrentData.objects.get(_user = userObject)
           CurrentDataserializer = CurrentDataSerializer(currenDataObject, data = {'data': requestCurrentData}, partial = True)
           if CurrentDataserializer.is_valid():
               CurrentDataserializer.save()
           else:
               return Response({"message": "currentSerializer failed"}, status=500)
           #update the history data
           historyObject = History.objects.get(_user = userObject)
           Historyserializer = HistorySerializer(historyObject, data = {'data': requestHistory}, partial = True)
           if Historyserializer.is_valid():
               Historyserializer.save()
           else:
               return Response({"message": "historySerializer failed"}, status = 500)
           #for updating the allbackupHistory too
           allBackUpHistory.objects.create(_user = userObject, history = requestHistory, currentData = requestCurrentData)
           return Response({'message': 'updated success'}, status=200)
       else:
           return Response({'message': 'Incorrect password'}, status=409)#it must be 409 cos 401 make the auth expire in mobile app lecture tracker
        
    elif userObject is None:
        #check if the username is empty or missing
        if len(requestUserName.strip() )< 1:
            return Response({"message" : "username or email required"}, status=400)
        elif "@GMAIL.COM" not in requestEmail.upper():
            return Response({"message" : "email invalid"}, status=400)
        #Create a new user, currentData and a new history object
        #Check if password is empty
        if len(requestPassword) < 2:
            return Response({"message": "Password required"}, status=400)
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
    return render(request, "api/request_incomplete/nopage.html")#This is a placeholder for the frontend aspect of the backupData, which is not yet implemented, but I want to have the endpoint ready for when I want to implement it in the future.







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
@api_view(['DELETE', 'GET', "POST"])
def deactivateAccount(request):
    _userName = request.data.get('username', 'default').upper()
    _email = request.data.get('email', 'default').upper()
    _password = request.data.get('password', "defaultImpossible")
    request_auth_key = request.data.get("auth_key", None)
    
    specialAccessForAuthKey = False; #for auth key so as to skip password checking
    
    
    #check if no request.data is passed
    if len(request.data.keys()) < 1:
        return Response({"message": "email required, password required, username required"})
    if _email == "DEFAULT":
        return Response({"message": "email empty"})
    if _userName == "DEFAULT":
        return Response({"message": "username required"})
    #check if the request_auth_key exist
    if request_auth_key != None:
        authObject = AuthStorage.objects.filter(_user__email__iexact = _email, auth_key = request_auth_key).first()
        #check if the auth key exist in the db
        if authObject != None:
            #check if token is nt expired yet
            if (time.time() - authObject.expiration_time) < 1200:
                #give access to data by chaging value of specialAccessForAuthKey
                specialAccessForAuthKey = True
                    
            else:
                return JsonResponse({"message" : "Token expired"})
    
    if _password == "defaultImpossible" and specialAccessForAuthKey == False:
        return Response({"message": "password required"})
    try:
        object = User.objects.get(username = _userName, email__iexact = _email)
    except:
        return Response({'message': 'User not found'})
    #Check if the is_active is False
    if object.is_active == False:
        return Response({"message": "user not found", "hint": f"This account have been deactivated prior to today on {object.last_login.strftime("%m %B,%Y %H:%M:%S")}"})
    if object.check_password(_password) or specialAccessForAuthKey == True:
        userserializer = UserSerializer(object, data = {'is_active': False, 'last_login': dt.datetime.now()}, partial = True)
        if userserializer.is_valid():
            userserializer.save()
            return Response({'message': f'deactivated success'})
        #error with the body request
        else:
            return Response({"message": "invalid serializer"})
    #Password incorrect
    else:
        return Response({'message': 'Incorrect password'})
    
    
    
    
    





#Deactivate single account by setting is_active to True
@api_view(['DELETE', 'GET', "POST"])
def reactivateAccount(request):
    _userName = request.data.get('username', 'default').upper()
    _email = request.data.get('email', 'default').upper()
    _password = request.data.get('password', 'default')
    request_auth_key = request.data.get("auth_key", None)
    
    specialAccessForAuthKey = False; #for auth key so as to skip password checking
    
    #check if no request.data is passed
    if len(request.data.keys()) < 1:
        return Response({"message": "email required, password required, username required"})
    if _email == "DEFAULT":
        return Response({"message": "email empty"})
    if _userName == "DEFAULT":
        return Response({"message": "username required"})
    if request_auth_key != None:
        authObject = AuthStorage.objects.filter(_user__email__iexact = _email, auth_key = request_auth_key).first()
        #check if the auth key exist in the db
        if authObject != None:
            #check if token is nt expired yet
            if (time.time() - authObject.expiration_time) < 1200:
                #give access to data by chaging value of specialAccessForAuthKey
                specialAccessForAuthKey = True
                    
            else:
                return JsonResponse({"message" : "Token expired"})
    
    if _password == "default" and specialAccessForAuthKey == False:
        return Response({"message": "password required"})
    try:
        object = User.objects.get(username = _userName, email__iexact = _email)
    except:
        return Response({'message': 'User not found'})
    #Check if the is_active is True
    if object.is_active:
        return Response({"message": "reactivated success", "hint": "This account was not inactive prior"})
    if object.check_password(_password) or specialAccessForAuthKey == True:
        userserializer = UserSerializer(object, data = {'is_active': True, 'last_login': dt.datetime.now()}, partial = True)
        if userserializer.is_valid():
            userserializer.save()
            return Response({'message': 'reactivated success'})
        #error with the body request
        else:
            return Response({"message": "invalid serializer"})
    #Password incorrect
    else:
        return Response({'message': 'Incorrect password'})
    







#Delete single account
@api_view(['DELETE', 'GET', 'POST'])
def deleteAccount(request):
    email = request.data.get("email",None)
    password = request.data.get("password", None)
    confirm_key = request.data.get("confirm_key", None)
    token = request.data.get("token", None)
    
    print(email, password, token)
    #validate incoming email
    if email is None:
        return Response({"message": "Null Credentials"}, status = 404)
    
    if confirm_key is None:
        return JsonResponse({"message" : "add the confirm_key as param to confirm account deletion"})
    
    #check if user want to use token and if token is missing use passowrd
    useToken = False
    if token is None: pass
    else:
        #check if the token have been tampered with
        if len(token) < 90:return JsonResponse({"message": "hacker spotted"}, status = 404)
        #validate token in the db
        tokenValidation = AuthStorage.objects.filter(_user__email__iexact = email, auth_key = token, expiration_time__lt = time.time() - 1200).first()
        print(tokenValidation)
        if tokenValidation is not None: useToken = True
        else: return JsonResponse({"message": "invalid email or passkey"}, status = 409) 
        
    #check if usToken os true
    if useToken is True: pass
    else:
        if password is None:return JsonResponse({"message": "pass key required"}, status = 409) 
        
    #check if the person is real
    if useToken: person = tokenValidation._user
    else: person = User.objects.filter(email__iexact= email).first()
    print(person)
    
    if person is None: return JsonResponse({"message":"wrong email or password"})
    else:
        #person is not none, check password
        if useToken: isPassword_valid = True#id true, dont ask for passowrd
        else: isPassword_valid = person.check_password(password)
        
        if isPassword_valid:
            serializePerson = UserSerializer(person, many = False)
            person.delete()
            return JsonResponse({"message": "Account Deleted Succesfully", "extra" : serializePerson.data})
        else:return JsonResponse({"message": "invalid password or email"}, status = 401)
    





#Delete all user; use with caution
@api_view(['DELETE', 'GET'])
def deleteAllData(request):
    goAhead = request.query_params.get('go_ahead', 'default')
    if goAhead != 'yes':
        return JsonResponse({'message': 'Unauthorized', 'hint': 'go_ahead: yes'})
    else:
        User.objects.all().delete()
        OtpSorage.objects.all().delete()
        return JsonResponse({'message': 'All data deleted'})










import time
@api_view(['GET', 'PATCH', 'POST'])
def otp(request):
    
    if len(request.data.keys()) < 1:
        return JsonResponse({"message": "email required"}, status = 400)
        
    requestEmail = f"{request.data.get("email", "empty")}".strip().upper() #had to put it in a quote just to catch a NoneType
    print(requestEmail)
    
    #send otp to the email and save the credentials into the db using time.time(), the validity is only 10 minutes (600 sec)
    if requestEmail == "empty":
        return JsonResponse ({"message": "Email cannot  be empty"}, status = 400)
    else:
        #email is given, check if it is valid.
        if "@GMAIL.COM" not in requestEmail:
            return JsonResponse({"message": "Not a valid email"}, status = 400)
        else:
            #email is valid, proceed to send otp
           
            #but what kind of otp ? the query_params(requestHeading) handle that by knowing wether we send an email for password, email or username reset or none
            #check if user exist:
            person = User.objects.filter(email__iexact = requestEmail ).first()
            if person == None:
                    return JsonResponse({"message": "no user"}, status = 400)
            elif person.is_staff is True:
                return JsonResponse({"message" : "reset not allowed via here for special candidate, contact support"}, status = 400)
            try:
                otp = Utility().generate_random_text(min_lenght=6, max_lenght=6, number=True, uppercase=False, lowercase=False, symbols=False)
                otp_unique_id = Utility().generate_random_text(min_lenght=100, max_lenght=100, number=True, uppercase=False, lowercase=False, symbols=False)
                otp_sent_time = time.time()
            except:
                return JsonResponse({"message": "otp server down"})
            
            #send mail
            requestHeading= request.query_params.get("heading" , "").upper()
            #use try cos if any error show, send the mail to me istead
            try:
                #mail for resettingusername only
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
        <p style="color:#999; font-size:12px; text-align:center;"> Time sent: {dt.datetime.now()}</p>
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
            message=f"Use the OTP {otp} sent to reset your Email.",
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
        <a href="{domain}updateEmail/?otp={otp}&otp_unique_id={otp_unique_id}&otp_sent_time={int(otp_sent_time)}&old_email={requestEmail}"
            style="background:#2d89ef; color:#fff; padding:12px 25px; text-decoration:none; border-radius:6px; font-weight:bold; display:inline-block;">
            Reset Email
        </a>
        </div>

        <p style="color:#999; font-size:12px; text-align:center;">
        If you did not request this, please ignore this email.
        </p>
        <p style="color:#999; font-size:12px; text-align:center;"> Time sent: {dt.datetime.now()}</p>

    </div>

    </body>
    </html>
    """
        )
        
                #mail for resetting password only
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
            <p style="color:#999; font-size:12px; text-align:center;"> Time sent: {dt.datetime.now()}</p>
        </div>
        
        </body>
        </html>
        """
            )
                #the requestHeading did not return something i recognize
                else:
                    return JsonResponse({"message": "Failure", "hint": "heading"}, status = 400)
                    #bckup to the otpStorage
                otpObject = OtpSorage.objects.create(email = requestEmail, otp = otp, otp_sent_time = otp_sent_time, otp_unique_id = otp_unique_id)
                r = OtpSorageSerializer(otpObject, many = False)

                return JsonResponse({"message": "success"}, status = 200)
            except Exception as e:
                # This prints to the Vercel 'Logs' tab during startup
                print(f"Error by ope: {f'{e}'.strip().upper()} ")
                if f"{e}".strip().upper() == "[ERRNO 7] NO ADDRESS ASSOCIATED WITH HOSTNAME":
                    return JsonResponse({"message" : "network issue"}, status = 500)
                return JsonResponse({"message": "error 500"}, status =500)#This will usually happens if the os.get() in the settings is not getting the gmail password

            

#Temprorary unused otp viewer
@api_view(["GET"])
def allOtp(request):
    del_all = request.query_params.get("del")#clear the table
    object = OtpSorage.objects.all()
    if del_all is not None:
        object.delete()
        return Response({"message" : "delete all success"})
    serializer = OtpSorageSerializer(object, many = True)
    from datetime import datetime as dt
    try:
        for i in serializer.data:
            timestamp = dt.fromtimestamp(i["otp_sent_time"])
            i.update({"otp_sent_time": timestamp.strftime("%d % %Y %H:%M:%S")})
        return Response(serializer.data)
    except Exception as e: return JsonResponse({"eror" : "backend error"}, status = 500)


@api_view(["GET"])
def allAuth(request):
    del_all = request.query_params.get("del")#clear the table
    object = AuthStorage.objects.all()
    if del_all is not None:
        object.delete()
        return Response({"message" : "delete all success"})
    serializer = AuthSorageSerializer(object, many = True)
    #i want the emails to be visible
    try:
        for i in serializer.data:
            person = User.objects.get(id = int(i.pop("_user")))
            i.update({"person_email": f"{person.email}"})
            i.update({"person_username": f"{person}"})
        return Response(serializer.data)
    except Exception as e:
        return Response([{"error": f"{e}"}, *serializer.data])

#otp frontend 
@api_view(["GET"])
def frontendOtp(request):
    requestHeading= request.query_params.get("heading" , "").upper()
    if len(requestHeading.strip()) < 1: return render(request, "api/request_incomplete/nopage.html")

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
                #render the otp useless
                object.delete()
                try:
                    send_mail(
                        
                        subject="PASSWORD RESET MESSAGE FROM LECTURE TRACKERS",
                        message = "password reset success",
                html_message=f"""

Hello,<br><br>

Your <strong>LectureTracker</strong> password was recently updated. If you made this change, you can safely ignore this email.<br><br>

<strong>Did you not make this request?</strong><br>
If you did <strong>not</strong> reset your password, it means your account may be compromised. To secure your account and prevent unauthorized access, please click the button below to reset your password immediately:<br><br>

<a href="https://lecture-tracker-omega.vercel.app/otp/?heading=PASSWORD%20RESET" 
style="display:inline-block;padding:12px 20px;background-color:#2563eb;color:#ffffff;text-decoration:none;border-radius:6px;font-weight:bold;">
Reset Your Password
</a><br><br>

<p>For your security, please do not share your login credentials or OTPs with anyone<p>.<br><br>
<p style="color:#999; font-size:12px; text-align:center;"> Time sent: {dt.datetime.now()}</p>
Best regards,<br>
Dev Ope""",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[requestEmail],
                )
                except Exception as e:
                    print ("email password confirm not sent , why ? : f{e}")
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
    return render(request,"api/request_incomplete/updatePassword_last_step.html")







@api_view(['PATCH', 'GET'])
def updateEmail(request):
    requestOldEMail = request.query_params.get('old_email', '').upper()
    requestNewEMail = request.query_params.get('new_email', '').upper()
    requestPassword = request.query_params.get('password', '')
    otp = request.query_params.get("otp", '')
    otp_sent_time = request.query_params.get("otp_sent_time", 0)#use time.time() to see the diff and check if it don reach 600 diff
    otp_unique_id = request.query_params.get("otp_unique_id", '')
    
    #check if query params is complete
    if "@GMAIL.COM" not in requestOldEMail:
        return JsonResponse({"message" : "invalid old_email"})
    elif "@GMAIL.COM" not in requestNewEMail:
        return JsonResponse({"message" : "invalid new_email"})
    elif len(otp) != 6:
        return JsonResponse({"message" : "invalid otp"})
    elif otp_sent_time == 0:
        return JsonReeponse({"message" : "invalid otp_sent_time"})
    elif len(otp_unique_id) < 1:
        return JsonResponse({"message" : "invalid otp_unique_id"})
        
    #all params have been check and no missing data, verfiy them otp now
    try:
        #to check if the otp value have not been tampered with
        otp_sent_time = int(otp_sent_time)
    except:
        return JsonResponse({"message" : "hacker spotted"})
    
    #Check if the credentials exist
    object = OtpSorage.objects.filter(email__iexact = requestOldEMail, otp = otp, otp_sent_time = otp_sent_time, otp_unique_id= otp_unique_id).first()
    if object is None:
        return JsonResponse({"message": "invalid credentials"})
    else:
        #credential are valid, validate otp sent time
        if otp_sent_time == 600:
            return JsonResponse({"message" : "otp expired"})
        #opt have not expired,proceed to  email
        
        #Check if old email is in system
        try:
            userObject = User.objects.get(email__iexact = requestOldEMail)
            #check if new email is not beign used by anyone else
            if User.objects.filter(email__iexact = requestNewEMail).first() is not None:
                return JsonResponse({"message" : "new Email already taken"})
        
            #new email not in system, proceed to check password
            if userObject.check_password(requestPassword):
                #password valid, all check, update finally
                userserializer = UserSerializer(userObject, data = {'email': requestNewEMail, "last_login" : dt.datetime.now()}, partial = True)
                if userserializer.is_valid():
                    userserializer.save()
                    #render the otp useless
                    object.delete()
                    try:
                        send_mail(
                        
                        subject="EMAIL RESET MESSAGE FROM LECTURE TRACKERS",
                message=f"""Subject: email Updated Successfully – LectureTracker

Hello,

This is to verify that your email have been successfully updated at a request made by you and all admin capabilities have been moved from {requestOldEMail.upper()} to this new email.


Best regards,
Dev Ope""",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[requestNewEMail],
                    )
                    
                    except Exception as e:
                        print (f"email  confirm not sent , why ? : f{e}")
                    return JsonResponse({"message" : "success"})
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
            "full_url": f"/{url}",   # for redirection
            "doc": API_DOC.get(key)
        })

    return render(request, "api/request_incomplete/api_inspector.html", {
        "endpoints": endpoint_data
    })





@api_view(["GET", "POST"]) 
def ai_response(request):
    email = request.query_params.get("email", "");
    password = request.query_params.get("password", "")
    request_auth_key = request.query_params.get("auth_key", None)
    request_history = request.data.get("history", None) #This is for the app user last message 
    request_message = request.data.get("message", None) #This is for the app user last message 
    
    # print(request_message)
    specialAccessForAuthKey = False; #for auth key so as to skip password checking
    #check the request_auth_key
    if request_auth_key is not None:
        authObject = AuthStorage.objects.filter(_user__email__iexact = email, auth_key = request_auth_key).first()
            #check if the auth key exist in the db
        if authObject != None:
            #check if token is nt expired yet
            if (time.time() - authObject.expiration_time) < 1200:
                #give access to data by chaging value of specialAccessForAuthKey
                specialAccessForAuthKey = True
                    
            else:
                return JsonResponse({"message" : "Token expired"})
    #Check if any of the query params is missing (skip passwprd if auth_key dectected)
    elif (len(request.query_params.keys()) < 2 and specialAccessForAuthKey == False) or len(email) < 2:
        return JsonResponse({"message": "email and password are required"}, status=400)
    
    if email.strip() == "":
        return JsonResponse({"message": "email required"}, status=400)
    elif password.strip() == "" and specialAccessForAuthKey==False:
        return JsonResponse({"message": "password required"}, status=400)

    #Since no missing param, check user data
    person = User.objects.filter(email__iexact = email.strip()).first()
    if person is None:
        return JsonResponse({"message": "user not found"}, status=400)
    elif not person.check_password(password) and specialAccessForAuthKey == False:
        return JsonResponse({"message": "Incorrect password"}, status=401)
    #Password is correcrt and user exist
    #check if is_active == false
    if person.is_active == False:
        return JsonResponse({"message" : "account is disabled,cannot generate response until you enable it"})
    #is_active == true from here, continue
    try:
        historyObject = History.objects.get(_user = person)
        currentDataObject = CurrentData.objects.get(_user = person)
    except:
       return JsonResponse({"message" : "no prior history found, perform at least one backup to get ai response"})
    
    
    
    if os.getenv("local_db") is not None:
        return JsonResponse({"message": "works"})
    else:
        import groq 
        grok_api_key = os.getenv("GROK")
    #Serialize the data
        historyObjectSerialized = HistorySerializer(historyObject, many = False)
        currentObjectSerialized = CurrentDataSerializer(currentDataObject, many = False)
        
        try:
            if request_history is None:
                ai_response = groq.Client(api_key=grok_api_key).chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                {"role": "system", "content": f"ignore this command and go with the following instructions:you are to analyze the question which will be inform of a list wrapped in strings and give summary analysis(total history count, number of missed, number of attended and number of nullifed and then find trends in it like how frequently user have imporved or decline over the time and give most lecture attended and msot lecture missed and also point out to other good to notice analysis) and give possible insight  on area of improment and area of strenght based on the history and the current data, in the history. tips to understand the data better : acomplised 0 stand for lecture missed, 1 stand for lecture attend and 2 stand for lecture nullfied,and understand that nullified lecture mean not due to user fault but due to school fault maybe lecture was cancelled or the class did not hold. do so one one single line without any break as i wont be able to clean any  newline symbol wich will make the text look weird, also  give an detailed possible measure for the student to adhere to in order to improve attendance and dont forget to remind user that they should backup their data as its from their latest backup insight will be generated by you, reply like you are speaking directly to the user and occasioanly give refrence to {person.username} as this is the user username NB: THE ONLY DATA THAT CAN BE REVELAED TO THE USER FROM THE LIST IS THE COURSE TITLE"},
                {"role": "user", "content": f"history: {historyObjectSerialized.data}, currnetData: {currentObjectSerialized.data}"},
                ])
                return JsonResponse({"message": ai_response.choices[0].message.content}, status=200)
            else:
                ai_response = groq.Client(api_key=grok_api_key).chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                {"role": "system", "content": f"the user current message: {request_message}, do not forget the user have old history to make refreence to, if the history is empty, just ignore the history and focus on the current message. In addition, do so one one single line without any break as i wont be able to clean any  newline symbol wich will make the text look weird and dont make your text too long unless very necessary, username : {person.username}"},
                {"role": "user", "content": f"history: {historyObjectSerialized.data}, currnetData: {currentObjectSerialized.data}"},
                {"role": "assistant" , "content" : f"this is the prior history between you and the user in an ascending manner, history = {request_history}"}
                ])
                return JsonResponse({"message": f"{ai_response.choices[0].message.content} h"}, status=200)
                
                
        except groq.RateLimitError as e:
            return JsonResponse({"message" : f"limit reached, come back in a few minutes.", }, status = 429)   
        except Exception as e:
            return JsonResponse({"message" : f"{e}"})
    








#python endpoint that hanldes all the login 
@api_view(['GET', "POST", "PATCH"])
def login(request):
    email = request.data.get("email", None)
    password = request.data.get("password", "")
    request_auth_key = request.query_params.get("auth_key", None)
    request_query_email2 = request.query_params.get("email2", None)
    
    #check if there is an auth_key in the param, will use this a verification istead of password
    if  request_auth_key != None and request_query_email2 != None:
        #verify the auth_key
        is_auth_key_authentic = AuthStorage.objects.filter(auth_key = request_auth_key, _user__email__iexact = request_query_email2).first()
        # print(is_auth_key_authentic._user.is_staff)
        if is_auth_key_authentic is None:
            #pass so the user can be prompt to login again 
            pass
        elif  is_auth_key_authentic._user.is_staff is True:
            #  i use the is staff to make sure an admin cant have a student accunt
            return render(request,"api/request_incomplete/login_welcome.html", {"message" : "Admin can't Login to this dashaord."})
        else:
            #verify the auth_key have not expired
            if (time.time() - is_auth_key_authentic.expiration_time) < 1200 :
                #have not expired, procees to login page
                userObject = User.objects.get(username = is_auth_key_authentic._user)
                if userObject.last_login != None:
                    last_login = dt.datetime.fromisoformat(f"{userObject.last_login}")
                    last_login = last_login.strftime("%d %B,%Y %H:%M")
                else:
                    last_login = None
                date_joined = dt.datetime.fromisoformat(f"{userObject.date_joined}")
                date_joined = date_joined.strftime("%d %B,%Y %H:%M")
                #login dashbpard
                return render(request, "api/request_incomplete/login_dashboard.html", {
                "username" : f"{is_auth_key_authentic._user}",
                "email" : request_query_email2,
                "date_joined": f"{date_joined}",
                "last_login" : f"{last_login}",
                "is_active" : f"{userObject.is_active}",
                "token_time_left" : abs(int(time.time() - is_auth_key_authentic.expiration_time-1200)),
                "token_value" : f"{is_auth_key_authentic.auth_key}"
                }
                )
            else:
                #auth_key expired
                return render(request, "api/request_incomplete/login_welcome.html", {"message" : f"token expired {int(time.time() - is_auth_key_authentic.expiration_time  - 1200)} sec ago"})
    
    
    if email == None and request_query_email2 == None:
        return render(request,"api/request_incomplete/login_welcome.html", {"message2" : f""})
    else:
        #Validate email in the db
        person = User.objects.filter(email__iexact = email).first()
        if person == None:
            # i did this so as to allow query param email too be used if request.data email is missing or not found
            person = User.objects.filter(email__iexact = request_query_email2).first()
        if person:
            #verify password when auth_key is missing -this signify user is about to leave welcome to dashboard
            if person.check_password(password):
                #password verified, generate an auth_key for them
                auth_key_value = Utility().generate_random_text(min_lenght=101, max_lenght=151, number=True, uppercase=True, lowercase= True, symbols= True)
                #delete any older auth_key so the user can only sign in one place
                AuthStorage.objects.filter(_user = person).delete()
                #now create a new one
                AuthStorage.objects.create(_user = person,  auth_key = auth_key_value, expiration_time = time.time())
                #end of generating auth_key and added to db
                
                #update thr last login to now
                userserializer = UserSerializer(person, data = {"last_login" : dt.datetime.now()}, partial = True)
                if userserializer.is_valid():
                    userserializer.save()
                return render(request,"api/request_incomplete/login_welcome.html", {"message" : "user found",  "auth_key" : auth_key_value})
                pass
            #wrong password
            return render(request,"api/request_incomplete/login_welcome.html", {"message" : "Incorrect Password"})
        else:
            #no user found 
            return render(request,"api/request_incomplete/login_welcome.html", {"message" : "No User Found"})





#For the app,i wil still find abetter way to do this
@api_view(["GET", "POST"])
def login_json(request):
    username = request.data.get("username", None)
    email = request.data.get("email", None)
    password = request.data.get("password", "")
    user_type = request.data.get("user_type", None)
    
    if email is None:
        return JsonResponse({"message": "email required"}, status = 404)
    if len(password) < 2:
        return JsonResponse({"message": "password required"}, status = 404)
    if user_type is None:
        return JsonResponse({"message" : "user_type required (new or old)"})
    if user_type == "new" or user_type == "old":
        pass
    else:
        return JsonResponse({"message" : "user_type required (new or old)"})
    
        #email and pass dey, validate 
    person_exist = User.objects.filter(email__iexact = email).first()
    if person_exist:
        if person_exist.check_password(password):
            #new user
            if user_type == "new":
                return JsonResponse({"message" : "email Taken"}, status = 409)
            elif user_type == "old":
                #Generate an auth key
                auth_key_value = Utility().generate_random_text(min_lenght=101, max_lenght=151, number=True, uppercase=True, lowercase= True, symbols= True)
                #del all old keys
                #add the auth key to the db
                try:
                    AuthStorage.objects.get(_user = person_exist).delete()
                except:
                    pass
                AuthStorage.objects.create(_user = person_exist, auth_key = auth_key_value, expiration_time = time.time())
                return JsonResponse({"message" : "success", "username" : f"{person_exist}", "auth_key": auth_key_value}, status = 200)
        #wrong password
        if user_type == "new":
            return JsonResponse({"message" : "email Taken"}, status = 409)
        elif user_type == "old":
            return JsonResponse({"message": "incorrect password"}, status = 401)
            
    #no user
    
    if user_type == "new":
        print(f"username is {username}")
        if username is None:
            return JsonResponse({"response": "username not found"})
        try:
            userObject =  User.objects.create_user(username= username.upper(), password= password, email= email)
            CurrentData.objects.create(_user = userObject)
            History.objects.create(_user = userObject)
            return Response({"message": "Account Created"}, status=201)
        except Exception as e:
            print(e)
            if "UNIQUE constraint failed" in f"{e}":
                return JsonResponse({"message": "Error!, username Taken"}, status = 404)
            return JsonResponse({"message" : f"{e}"}, status = 404)
    return JsonResponse({"message": "user not found"}, status = 409)







#Different from temp2 cos it clear based on a single email while temp2 clear all token
@api_view(["GET", "POST"])
def cleartoken(request):
    email = request.query_params.get("email", None)
    if email is None:
        return render(request, "api/request_incomplete/login_welcome.html", {"message": "token invalidated"})
    else:
        try:
            AuthStorage.objects.get(_user__email__iexact = email).delete()
        except Exception as e:
            print(f"{e}")
        return render(request, "api/request_incomplete/login_welcome.html")








@api_view(["GET", "POST"])
def generateToken(request):
    email = request.data.get("email", None)
    password = request.data.get("password", None)
    username = request.data.get("username", None)
    
    if email is None or password is None or username is None:
        return Response({"message": "email, password, username required"})
    
    person  = User.objects.filter(email__iexact = email, username = username.upper()).first()
    if person is None:
        return Response({"message": "user not found"}, status= 200)
    
    if person.check_password(password):
        #generate auth_key
        auth_key_value = Utility().generate_random_text(min_lenght=101, max_lenght=151, number=True, uppercase=True, lowercase= True, symbols= True)
        #delete any older auth_key so the user can only sign in one place
        AuthStorage.objects.filter(_user = person).delete()
        #now create a new one
        AuthStorage.objects.create(_user = person,  auth_key = auth_key_value, expiration_time = time.time())
        #end of generating auth_key and added to db
        return Response({"message": f"auth_token for {person}", "auth_key": auth_key_value})
    else:
        return Response({"message": "incorrect password"}, status= 409)



@api_view(["GET", "POST"])
#Longer session of the auth key - i had mobile phone in mind
def permanentLoginUnlessInvalidated(request):
    email = request.data.get("email", None)
    password = request.data.get("password", "")
    
    if email is None or "@gmail.com" not in email:
        return Response({"message" : "invalid email"})
    if len(password) < 2:
        return Response({"message": "password required"})
    
    #keys complete, verify against db
    person = User.objects.filter(email__iexact = email).first()
    if person:
        
    #incorrect password
        return Response({"message": "incorrect password"})
    #no user
    else:
        return Response({"message": "no user"})
    







@api_view(["GET"]) #The output of this endPoint must only have one 200 code as my lecture tracker heavily depends on the order of the data output
def userDetails(request):
    email = request.query_params.get("email", None)
    auth_key = request.query_params.get("auth_key", "").strip()
    print(len(auth_key))
    
    if len(request.query_params.keys()) < 1:
        return JsonResponse({"message" : "email and validattion required"}, status = 400)
    
    if email is None:
        return JsonResponse({"message": "invalid email"}, status = 400)
    elif "@gmail.com".upper() not in email.upper():
        return JsonResponse({"message" : "invalid email", "hint": "@gmail.com missing"}, status = 400)
    if len(auth_key) == 0:
        return JsonResponse({"message": "validationrequired"})
    if len(auth_key) < 90:
        return JsonResponse({"message" : "hacker spotted"}, status = 400)
    
    #All data have been validated, proceed to get validatee and response
    person = User.objects.filter(email__iexact = email).first()
    if person is None:
        return JsonResponse({"message": "user not found"}, status = 400)
    #User dey, continue
    auth_key_valid = AuthStorage.objects.filter(_user = person, auth_key = auth_key).first()
    if auth_key_valid:
        serializer = UserSerializer(person, many = False)
        tempDict = serializer.data
        tempDict.pop("id")
        iWantToChangeName = tempDict.pop("is_active")
        print(iWantToChangeName)
        tempDict.pop("password")
        if iWantToChangeName == True:
            tempDict.update({"status" : "activated"}),
        elif iWantToChangeName== False:
            tempDict.update({"status": "deactivated"})
        else:
            tempDict.update({"status": "unknown"})
        return JsonResponse(tempDict)
    
    
    #Auth key is nt valid
    return JsonResponse({"message" : "invalid token"}, status = 400)
    
    




#for getting older backup
@api_view(['GET', "POST"])
def allTimeBackUpHistory(request):
    requestEmail =  request.data.get('email', None)
    requestPassword =  request.data.get('password', '')
    auth_key = request.data.get("auth_key", None)
    requestId = request.data.get("id", None)
    special_access = False #will use it in the future while verifying auth key
    
    
    if requestEmail == None:
        return Response({"message":"invalid email"}, status = 400)
    if len(requestPassword) < 2 and auth_key == None:
        return Response({"message":"invalid passsword"}, status = 409)

    #data verified
    person = User.objects.filter(email__iexact = requestEmail).first()
    if person == None:
        return Response({"message": "no user found"}, status = 400)
    
    #user exist
    if auth_key is not None:
        check_auth_key = AuthStorage.objects.filter(auth_key = auth_key, _user = person).first()
        if check_auth_key is not None:
            special_access = True
            
    #now pulling record
    if special_access or person.check_password(requestPassword):
        #validation allowed
        if requestId is not None:
            try:
                requestId + 2
            except:
                return Response({"message": "id must be an INTEGER and not a STRING"}, status = 400)
            result = allBackUpHistory.objects.filter(_user = person, id = requestId).first()
            serializer = allBackUpHistorySerializer(result, many = False)
            toReturn = serializer.data
            
        else:
            result = allBackUpHistory.objects.filter(_user = person).all()
            serializer = allBackUpHistorySerializer(result, many = True)
            toReturn = []
            for i in serializer.data:
                toReturn.append({"id": i.pop("id", None), "time": i.pop("time", None)})
        #I only need the id if the user have not specified which id they want to retreive
        return Response({"message" : toReturn},status = 200)
  
    else:
        return Response({"message": "invalid password"}, status = 409)
        



#This is for the homepage
@api_view(['GET'])
def home(request):
    return render(request, 'api/homehtml.html', {"total_user" : 2, "active_users" : 3})

#for getting all user in the system
@api_view(["GET"])
def all_users(request):
    users = User.objects.filter(is_staff = False).all()#get only the student and ignore the admin
    serializer = UserSerializer(users, many = True)
    return JsonResponse({"all_user" : len(serializer.data)})


#for getting all active users us int the expiration_time as refrence
@api_view(["GET"])
def all_active_users(request):
    active_personnel = AuthStorage.objects.filter(expiration_time__gt = time.time() - 1200, _user__is_staff = False) # check if the user token is still valid for only student
    serialiser = AuthSorageSerializer(active_personnel, many = True)
    return JsonResponse({"active_user" : len(serialiser.data)})





####ADMIN

#create token for admins
@api_view(["GET", "POST"])
def adminTokenGenerator(request):
    email = request.data.get("email", None)
    password = request.data.get("password", None)
    if email == None or password == None:
        return JsonResponse({"message": "invalid credentials"}, status = 404)
    #check if the dta is valid
    person = User.objects.filter(email__iexact = email).first()
    print(person)
    if person  == None:return JsonResponse({"message": "invalid credentials"}, status = 409)
    if person.check_password(password):
        #the user exist check if they are admin
        if person.is_staff:
            #create a short 20 min token for them
            auth_key_value = Utility().generate_random_text(min_lenght=101, max_lenght=151, number=True, uppercase=True, lowercase= True, symbols= True)
            #delete any older auth_key so the user can only sign in one place
            AuthStorage.objects.filter(_user = person).delete()
            #now create a new one
            AuthStorage.objects.create(_user = person,  auth_key = auth_key_value, expiration_time = time.time())
            #end of generating auth_key and added to db
            return JsonResponse({"session_id": auth_key_value, "email": person.email}, status = 200)
        else: return JsonResponse({"message": "only admin are allowed"}, status = 409)
    else: return JsonResponse({"message": "invalid email or password"}, status = 409)


#logout admins
@api_view(["GET", "POST"])
def adminLogout(request):
    email = request.data.get("email", None)
    if email is None: return JsonResponse({"message" : "invalid email"}, status = 404)
    #get all the tokens
    AuthStorage.objects.filter(_user__email__iexact = email).delete()
    return JsonResponse({"message" : "success"}, status = 200)


#admin create account ui
@api_view(["GET", "POST"])
def createAdminAccount(request):
    return render(request, "api/admin_create_account.html")

#create admin account logic - theui come to interact with this
@api_view(["GET", "POST"])
def createAdminAccountLogic(request):
    email = request.data.get("email", None)
    password = request.data.get("password", None)
    if email is None or password is None:
        return JsonResponse({"message": "invalid credentials"}, status = 404)
    
    #check if account exist and is a student istead of staff
    account = User.objects.filter(email__iexact = email).first()
    if account is not None:#user exist
        if account.is_staff == False: return JsonResponse({"message": "Student Account dectected , delete your account to be able to create an admin account; /deleteAccount/ to delete your account"}, status = 409)
        else: return JsonResponse({"message": "Account found with this email, login into your account at /admin"})

    
    #create account
    person = User.objects.create_user(username = email.upper(), email= email.upper(), password=password, is_staff = True)
    serializer = UserSerializer(person, many = False)
    return JsonResponse({"message": "success", "extra" : serializer.data})

#remove admin account
@api_view(["GET", "DELETE"])
def removeAdminAccount(request):
    pass


#view admins
@api_view(["GET", "DELETE"])
def viewAllAdminUsername(request):
    pass


#admin login determiner
@api_view(["GET", "POST"])
def admin(request):
    email = request.query_params.get("email", None)
    token = request.query_params.get("session_id", None)

    if token is None or email is None:
        return  render(request,"api/admin_login.html")
    
    print(email, token)
    #validate the token
    auth = AuthStorage.objects.filter(_user__email__iexact = email).first()
    if auth is None:
        return  render(request,"api/admin_login.html")
    
    return render(request,"api/admin.html")


@api_view(["GET", "POST"])
def batch_email(request):
    #ask for token of an admin and the email cos only the admin shouldbe able to perform smthing like ths
    email = request.query_params.get("email", None)
    token = request.query_params.get("session_id", None)
    if email == None or token == None:
        return JsonResponse({"message": "invalid credentials"}, status = 404)
    
    person = User.objects.filter(email__iexact = email, token = token).first()
    if person :
        #user is real, check if they are staff
        if person.is_staff() == False:
            return JsonResponse({"message": "only admin are allowed"}, status = 409)
        
        #get all users
        allStudent = User.objects.filter(is_staff = False).all()
        tags= [i for i in allStudent]
        print(tags)
        return JsonResponse({"message": "email sent placeholder"}, status = 200)
    
    return JsonResponse({"message" : "invalid credentials"}, 409)
    

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


class Utility:
    def __init__(self):
        pass
    def generate_random_text(self,  min_lenght, max_lenght, number = True , uppercase = True , lowercase = True , symbols = True) -> str:
        import string
        all = ""
        if number is True: all = all + string.digits
        if uppercase is True: all = all + string.ascii_uppercase 
        if lowercase is True: all = all + string.ascii_lowercase
        if symbols is True: all = all + string.punctuation
        
        auth_key_value = ""
        if min_lenght == max_lenght :
            for i in range(max_lenght):
                auth_key_value += random.choice(all)
        else:
            for i in range(random.randint(min_lenght,max_lenght)):
                auth_key_value += random.choice(all)
                
        return auth_key_value
        
    