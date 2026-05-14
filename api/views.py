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
import groq 


# from google import genai
# model = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# api_key = os.getenv("GEMINI_API_KEY")
grok_api_key = os.getenv("GROK")



#To get one data from the db
@api_view(['GET'])
def viewData(request):
    requestEmail =  request.query_params.get('email', 'default').upper().strip()
    requestPassword =  request.query_params.get('password', 'a')
    #check if the email in the param exist
    if requestEmail == "DEFAULT":
        return JsonResponse({"message":"user not found", "hint": "add email to the query param"})
  #Get the email if exist  
    userObjects = User.objects.filter(email__iexact = requestEmail).first()
    if userObjects is not None:
        if len(requestPassword.strip()) < 2:
            return JsonResponse({'message': 'password required'})
        #Check if the is_active is False
        if userObjects.is_active == False:
            return JsonResponse({"message": "account deactivated"})
        if userObjects.check_password(requestPassword):
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
                last_login = last_login.strftime("%m %B,%Y %H:%M:%S")
            date_joined = tempDict.pop("date_joined", None)
            date_joined = dt.datetime.fromisoformat(f"{date_joined}")
            date_joined = date_joined.strftime("%m %B,%Y %H:%M:%S")

            #add back the formatted data
            
            tempDict.update({"last_login" : last_login, "date_joined" : date_joined})
            

            return JsonResponse({'history': historySerializer.data, 'currentData': currentDataSerializer.data, 'user': tempDict, 'message': 'success'}, safe=False)
        
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
                    last_login = last_login.strftime("%m %B,%Y %H:%M:%S")
                date_joined = userPersonal.pop("date_joined", None)
                date_joined = dt.datetime.fromisoformat(date_joined)
                date_joined = date_joined.strftime("%m %B,%Y %H:%M:%S")

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
@api_view(['POST', 'PATCH'])
def backupData(request):
    requestUserName =  request.data.get('username', '').strip().upper()
    requestEmail =  request.data.get('email', '').strip().upper()
    requestPassword =  request.data.get('password', '')
    requestHistory = request.data.get('history', [])
    requestCurrentData = request.data.get('currentData',[] )
    print(requestUserName)
    
    #Check if user already exists, if so, update the data, if not, create a new, currentData and history object
    userObject = User.objects.filter(email__iexact = requestEmail).first()

    if userObject is not None:
       if userObject.check_password(requestPassword):
           #update user
           #check if the username the user want to use have not been taken
           userNameCheck= User.objects.filter(username = requestUserName).first()
           if userNameCheck is not None and userNameCheck.email.upper() != requestEmail.upper() and userObject.check_password(requestPassword):
               return Response({"message": "username is not available"}, status=400)
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
               return Response({"message": "currentSerializer failed"}, status=500)
           #update the history data
           historyObject = History.objects.get(_user = userObject)
           Historyserializer = HistorySerializer(historyObject, data = {'data': requestHistory}, partial = True)
           if Historyserializer.is_valid():
               Historyserializer.save()
           else:
               return Response({"message": "historySerializer failed"}, status = 500)
           return Response({'message': 'updated success'}, status=200)
       else:
           return Response({'message': 'Incorrect password'}, status=401)
        
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
    _password = request.data.get('password', 'default')
    #check if no request.data is passed
    if len(request.data.keys()) < 1:
        return Response({"message": "email required"})
    elif _email == "DEFAULT":
        return Response({"message": "email empty"})
    elif _userName == "DEFAULT":
        return Response({"message": "username required"})
    elif _password == "default":
        return Response({"message": "password required"})
    try:
        object = User.objects.get(username = _userName, email__iexact = _email)
    except:
        return Response({'message': 'User not found'})
    #Check if the is_active is False
    if object.is_active == False:
        return Response({"message": "user not found", "hint": f"This account have been deactivated prior to today on {object.last_login.strftime("%m %B,%Y %H:%M:%S")}"})
    if object.check_password(_password):
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
    #check if no request.data is passed
    if len(request.data.keys()) < 1:
        return Response({"message": "email required"})
    elif _email == "DEFAULT":
        return Response({"message": "email empty"})
    elif _userName == "DEFAULT":
        return Response({"message": "username required"})
    elif _password == "default":
        return Response({"message": "password required"})
    try:
        object = User.objects.get(username = _userName, email__iexact = _email)
    except:
        return Response({'message': 'User not found'})
    #Check if the is_active is True
    if object.is_active:
        return Response({"message": "reactivated success", "hint": "This account was not inactive prior"})
    if object.check_password(_password):
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
@api_view(['DELETE', 'GET'])
def deleteAccount(request):
    return Response({"message": "mo actice in asake"})





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
            #but what kind of otp ? the query_params(requestHeading) handle that by knowing wether we send an email for password, email or username reset or none
            #check if user exist:
            if User.objects.filter(email__iexact = requestEmail ).first() == None:
                    return JsonResponse({"message": "no user"})
            
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
                    return JsonResponse({"message": "Failure"})
                    #bckup to the otpStorage
                otpObject = OtpSorage.objects.create(email = requestEmail, otp = otp, otp_sent_time = otp_sent_time, otp_unique_id = otp_unique_id)
                r = OtpSorageSerializer(otpObject, many = False)

                return JsonResponse({"message": "success"})
            except Exception as e:
                # This prints to the Vercel 'Logs' tab during startup
                print(f"Error by ope: {e}")
                return JsonResponse({"message": "error 500"})#This will usually happens if the os.get() in the settings is not getting the gmail password

            
            
        
        
        
        
        
        
        
#Temprorary
@api_view(["GET"])
def temp(request):
    del_all = request.query_params.get("del")#clear the table
    object = OtpSorage.objects.all()
    if del_all is not None:
        object.delete()
        return Response({"message" : "delete all success"})
    serializer = OtpSorageSerializer(object, many = True)
    return Response(serializer.data)
    
    
   
   
   
   
   
   
   
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
            "full_url": f"/{url}",   # 🔥 for redirection
            "doc": API_DOC.get(key)
        })

    return render(request, "api/request_incomplete/api_inspector.html", {
        "endpoints": endpoint_data
    })





@api_view(["GET"])
def ai_response(request):
    question = request.query_params.get("question", "");
    if question.strip() == "":
        return JsonResponse({"message": "empty question"}, status=400)
    #Since question is not empty, return a proper message
    person = User.objects.get
    data = History.objects.get()
    ai_response = groq.Client(api_key=grok_api_key).chat.completions.create(
        model="llama-3.3-70b-versatile",
       messages=[
        {"role": "system", "content": "you are to analyze the question which will be inform of a list and generate insight on area of improment and area of strenght based on the history and the current data, in the history, acomplised 0 stand for lecture missed, 1 stand for lecture attend and 2 stand for lecture nullfied, "},
        {"role": "user", "content": question},
        ], max_tokens=5
       
    )   

    return JsonResponse({"message": ai_response.choices[0].message.content}, status=200)
    
    


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