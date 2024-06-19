from rest_framework import serializers
from core.models import CustomUser, MedicalInsurance, FamilyInsurance
from django.shortcuts import get_list_or_404



class CustomUserSerialiser(serializers.ModelSerializer):
    class Meta:
        model= CustomUser
        fields= ['email', "first_name", "last_name"]

class GetInsuranceSerialiser(serializers.ModelSerializer):
    customer= CustomUserSerialiser(read_only= True)

    class Meta:
        model= MedicalInsurance
        fields= "__all__"


class PostInsuranceSerialiser(serializers.ModelSerializer):
    price= serializers.DecimalField(max_digits= 10, decimal_places=2, read_only= True)

    class Meta:
        model= MedicalInsurance
        fields= ["customer", "phone_number", "subscription", "price"]

    def create(self, validated_data):
        '''
        # Set the customer
        request= self.context.get('request')
        if request and hasattr(request, 'data'):
            user_email= request.data.get('email')
            user= get_list_or_404(CustomUser, email= user_email)
            validated_data['customer']= user
        '''

        # Set the price
        if validated_data.get('subscription') == "family":
            validated_data['price'] = 3500
            validated_data['family_policy'] = True
        else:
            validated_data['price'] = 1500
            validated_data['family_policy'] = False

        return super().create(validated_data)