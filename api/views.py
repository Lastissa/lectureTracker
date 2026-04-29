import random

from django.shortcuts import render
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from .serializers import *
from .models import History, CurrentData
from django.http import JsonResponse
from django.contrib.auth.models import User
import datetime as dt


#To add and update data(except update username and email) to the db,
@api_view(['POST', 'PATCH'])
def backupView(request):
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
           userserializer = UserSerializer(userObject, data = {'last_login': dt.datetime.now()}, partial = True)
           if userserializer.is_valid():
               userserializer.save()
           currenDataObject = CurrentData.objects.get(_user = userObject)
           CurrentDataserializer = CurrentDataSerializer(currenDataObject, data = {'data': requestCurrentData}, partial = True)
           if CurrentDataserializer.is_valid():
               CurrentDataserializer.save()
           #update the history data
           historyObject = History.objects.get(_user = userObject)
           Historyserializer = HistorySerializer(historyObject, data = {'data': requestHistory}, partial = True)
           if Historyserializer.is_valid():
               Historyserializer.save()

           return Response({'message': 'updated success'}, status=200)
       else:
           return Response({'message': 'Incorrect password'}, status=401)
        
    elif userObject is None:
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
    



#To get one data from the db
@api_view(['GET'])
def viewData(request):
    requestEmail =  request.query_params.get('email', 'default').upper()
    requestPassword =  request.query_params.get('password', 'default')
  #Get the email if exist  
    userObjects = User.objects.filter(email__iexact = requestEmail).first()
    if userObjects is not None:
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
        return Response({'message': 'no user found'})

    
    
    
    
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




@api_view(['PATCH', 'POST'])
def updatePassword(request):
    requestEmail = request.data["email"]
    oldPassword = request.data.get("old_password", 'ImpossiblePassword144')
    newPassword = request.data.get("new_password", '')
    
    #Check if email exist
    object = User.objects.filter(email__iexact = requestEmail ).first()
    if object is None:
        return Response({"message": "invalid email"})
        
    else:
        #Check password validity
        userObject = User.objects.get(email__iexact = requestEmail)
        if userObject.check_password(oldPassword):
            userObject.set_password(newPassword)
            userObject.save()
            return Response({"message": "update password success"})
        else:
            return Response({"message": "invalid password"})
    return Response(f"{object}")






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





#This is for the homepage
@api_view(['GET'])
def home(request):
    return render(request, 'api/homehtml.html')

