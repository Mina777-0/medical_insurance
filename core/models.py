from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password, **extra_fields):
        if not email:
            raise ValueError("Email Address should be provided")
        user = self.model(email= self.normalize_email(email), first_name= first_name, last_name= last_name, **extra_fields)
        user.set_password(password)
        user.save(using= self._db) # In case of custom user. It helps saving the user to the db
        return user

    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Supeuser is_staff should be true")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Supeuser is_superuser should be true")
        
        return self.create_user(email, first_name, last_name, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique= True, verbose_name= "Email Address", max_length= 255)
    first_name = models.CharField(max_length= 255)
    last_name = models.CharField(max_length= 255)
    is_staff = models.BooleanField(default= False)
    is_active = models.BooleanField(default= True)
    date_joined = models.DateTimeField(default= timezone.now)

    objects= CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    


class MedicalInsurance(models.Model):
    SUBSCRIPTION_STATUS = (
        ('single', 'S'),
        ('family', 'F'),
    )

    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    )

    INSURANCE_STATUS = (
        ('active', 'A'),
        ('inactive', 'I'),
        ('cancelled', 'C'),
    )

    customer= models.OneToOneField(CustomUser, on_delete= models.CASCADE, related_name= 'customer')
    phone_number_regex= RegexValidator(r'\+?\d{9,15}$', message="Phone number format should be +111222333444")
    phone_number= models.CharField(validators=[phone_number_regex], max_length= 17)
    subscription= models.CharField(max_length= 6, choices= SUBSCRIPTION_STATUS)
    family_policy= models.BooleanField(default= False)
    payment= models.CharField(max_length= 7, choices= PAYMENT_STATUS, default= "pending")
    price= models.DecimalField(max_digits= 10, decimal_places= 2, editable= False)
    insurance_status= models.CharField(max_length= 9, choices= INSURANCE_STATUS, default= "inactive")
    created_at= models.DateTimeField(auto_now_add= True)
    updated_at= models.DateTimeField(auto_now= True)

    def __str__(self):
        return f"{self.customer.first_name} {self.customer.last_name} - {self.subscription}"
    
    class Meta:
        indexes= [
            models.Index(fields=["customer"]),
            models.Index(fields= ["subscription"]),
            models.Index(fields= ["insurance_status"]),
        ]
        unique_together= (('customer','subscription'),)


    def save(self, *args, **kwargs):
        if self.pk:
            # Check for status changes and send the appropriate email
            if self.insurance_status == "cancelled":
                email= EmailMessage(
                    f"Insurance policy cancellation",
                    "Your Medical insurance policy is cancelled successfully. Please contact us for further assistance",
                    from_email= settings.EMAIL_HOST_USER,
                    to= [self.customer.email,],
                )
                email.send(fail_silently= False)
                # Check if there is a related instance and update it accordingally
                if hasattr(self, 'family_members'):
                    self.family_policy= True
                    self.family_members.status= "inactive"
                    self.family_members.save()

            # Set the price according to the type of subscription
            if self.subscription == "family":
                self.family_policy = True
                self.price= 3500.00
            else:
                self.family_policy = False
                self.price= 1500.00
            
            # Check if it's paid or not and determine the status of the policy accordingly
            if self.payment == "pending":
                self.insurance_status = "inactive"

            elif self.payment == "paid":
                email= EmailMessage(
                    "Insurance policy activation",
                    "Your medical insurance policy is activated successfully. Please contanct us for further assistance",
                    from_email= settings.EMAIL_HOST_USER,
                    to= [self.customer.email]
                )
                email.send(fail_silently= False)
                self.insurance_status = "active"

        super(MedicalInsurance, self).save(*args, **kwargs)

            


class FamilyInsurance(models.Model):
    STATUS= (
        ('active', 'A'),
        ('inactive', 'I'),
    )

    RELATIONSHIP= (
        ('spouse', "Spouse"),
        ('son', 'Son'),
        ('daughter', 'Daughter'),
    )

    insurance= models.ForeignKey(MedicalInsurance, on_delete= models.CASCADE, related_name="family_members")
    first_name= models.CharField(max_length= 64)
    last_name= models.CharField(max_length= 64)
    relation= models.CharField(max_length= 8, choices= RELATIONSHIP)
    age= models.PositiveIntegerField()
    status= models.CharField(max_length= 8, choices= STATUS, default= "active")
    created_at= models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.insurance.customer.first_name}"
    
    class Meta:
        indexes= [
            models.Index(fields= ["first_name", "last_name", "age"]),
            models.Index(fields= ["insurance"]),
        ]

        unique_together= (("first_name", "insurance", "relation"),)





