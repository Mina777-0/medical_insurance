from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from .models import CustomUser, MedicalInsurance, FamilyInsurance

class CustomCreationForm(forms.ModelForm):
    password1= forms.CharField(label= "Password", widget= forms.PasswordInput)
    password2= forms.CharField(label= "Confirm Password", widget= forms.PasswordInput)

    class Meta:
        model= CustomUser
        fields= ["email", "first_name", "last_name"]
    
    def __init__(self, *args, **kwargs):
            super(CustomCreationForm, self).__init__(*args, **kwargs)
            self.fields["email"].widget.attrs["placeholder"]= "Email Address"
            self.fields["first_name"].widget.attrs["placeholder"]= "First name"
            self.fields["last_name"].widget.attrs["placeholder"]= "Last name"
            self.fields["password1"].widget.attrs["placeholder"]= "Password"
            self.fields["password2"].widget.attrs["placeholder"]= "Confirm Password"

    def clean_password(self):
        password1= self.cleaned_data.get('password1')
        password2= self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    def save(self, commit= True):
        user= super().save(commit= False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user
    

# Allows an admin in admin interface to change data about the user without messing with password
class CustomChangeForm(forms.ModelForm):

    password= ReadOnlyPasswordHashField()

    class Meta:
        model= CustomUser
        fields= ["email", "first_name", "last_name", "password", "is_active", "is_staff"]
    
    def clean_password(self):
        # Return the initial value of the password field
        return self.initial['password']
    

class Signup(CustomCreationForm):
    class Meta:
        model= CustomUser
        fields= ["email", "first_name", "last_name", "password1", "password2"]


class NewPolicy(forms.ModelForm):

    class Meta:
        model= MedicalInsurance
        fields= ["customer", "phone_number", "subscription"]
    
    
    def save(self, commit= True):
        instance= super().save(commit= False)

        if self.cleaned_data.get("subscription") == "family":
            instance.price= 3500.00
            instance.family_policy= True
        else:
            instance.price= 1500.00
            instance.family_policy= False
        
        if commit:
            instance.save()
            return instance


    

class NewFamilyMemeber(forms.ModelForm):
    class Meta:
        model= FamilyInsurance
        fields= "__all__"

        