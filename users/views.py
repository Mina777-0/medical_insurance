from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, get_user_model
from core.models import CustomUser, MedicalInsurance, FamilyInsurance
from .decorators import group_required
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from .serialisers import CustomUserSerialiser, GetInsuranceSerialiser, PostInsuranceSerialiser
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse



stripe.api_key= settings.STRIPE_SECRET_KEY
User= get_user_model()


@login_required(login_url='signin')
@group_required('Editors')
def users_home(request: HttpRequest):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('signin'))
    return render(request, "users/home.html")

@login_required(login_url='signin')
def signout(request: HttpRequest):
    logout(request)
    return HttpResponseRedirect(reverse('signin'))


# Sign in API

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def api_signin(request: Request):
    user= get_object_or_404(CustomUser, email= request.data.get('email'))
    if not user.check_password(request.data.get('password')):
        return Response({'Error': "Invalid Credentials"}, status= status.HTTP_404_NOT_FOUND)
    serialiser= CustomUserSerialiser(instance= user)
    token, created= Token.objects.get_or_create(user= user)

    response= {
        "message": "User is identified",
        'data': serialiser.data,
        "token": token.key,
    }

    return Response(data= response, status= status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAdminUser])
def get_policies(request: Request):
    policies= MedicalInsurance.objects.all()
    seraialiser= GetInsuranceSerialiser(many= True, instance= policies)
    return Response(data= seraialiser.data, status= status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def insurance_policy(request: Request):
    if request.method == "GET":
        user= get_object_or_404(CustomUser, email= request.data.get('email'))
        try:
            policy= MedicalInsurance.objects.get(customer= user.pk)
            serialiser= GetInsuranceSerialiser(instance= policy)

            return Response(data= serialiser.data, status= status.HTTP_200_OK)
        except MedicalInsurance.DoesNotExist:
            return Response({"Error": "Couldn't find any policy insurance"}, status= status.HTTP_404_NOT_FOUND)
        
    
    if request.method == "POST":
        user= get_object_or_404(CustomUser, email= request.data.get('email'))

        data= {
            'customer': user.pk,
            "phone_number": request.data.get('phone_number'),
            "subscription": request.data.get('subscription'),
        }

        policy_serialiser= PostInsuranceSerialiser(data= data)
        if policy_serialiser.is_valid():
            policy= policy_serialiser.save()
            return redirect(reverse('payment_page', args=[policy.pk]))
            '''
                        response= {
                "message": "Your policy insurance is created successfully",
                "data": policy_serialiser.data,
            }

            return Response(data= response, status= status.HTTP_201_CREATED)
            '''

        return Response(data= policy_serialiser.errors, status= status.HTTP_400_BAD_REQUEST)
    

# a4aad5fa655581e2d63094551ac4649289155561 Mina
# 00ea0811f6659a612f5a4efd05994a13de35a7c4 Harry


