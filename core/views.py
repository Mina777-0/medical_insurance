from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse, HttpResponse
from .forms import Signup, NewPolicy, NewFamilyMemeber
from .models import CustomUser, MedicalInsurance, FamilyInsurance
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt


stripe.api_key= settings.STRIPE_SECRET_KEY
User = get_user_model()

# No acces permission
def no_access(request:HttpRequest):
    return JsonResponse({"Error": "You have no access to this page"}, status= 403)

# Add a new user
@login_required(login_url='signin')
def signup(request:HttpRequest):
    if request.method == "POST":
        form = Signup(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('home')
        else:
            return render(request, "core/signup.html", {"message": "This user already exists"}, status= 400)
    else:
        form= Signup()
    return render(request, "core/signup.html", {'form': form})

# Users page
@login_required(login_url='signin')
def users(request: HttpRequest):
    return render(request, "core/users.html", {
        'users': CustomUser.objects.all(),
        'groups': Group.objects.all(),
        'permissions': Permission.objects.all(),
    })


# Signin page for Admins
def signin(request:HttpRequest):
    if request.method == "POST":
        email= request.POST.get('email')
        password= request.POST.get('password')

        user= authenticate(request, email= email, password= password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return HttpResponseRedirect('admin_home')
            else:
                return redirect(reverse('users_home'))
        else:
            return JsonResponse({'Error': "Invalid Credentials"}, status= 400)
    return render(request, "core/core.html")


@login_required(login_url='signin')
def signout(request:HttpRequest):
    logout(request)
    return HttpResponseRedirect(reverse('signin'))


# Home page for Admins
@login_required(login_url='signin')
def admin_home(request:HttpRequest):
    if not request.user.is_authenticated and not request.user.is_superuser:
        return redirect(reverse('no_access'))
    return render(request, "core/home.html",{
        'customers': MedicalInsurance.objects.all(),
    })


# Groups page
@login_required(login_url='signin')
def groups(request: HttpRequest):
    return render(request, "core/groups.html",{
        'users': CustomUser.objects.all(),
        'groups': Group.objects.all(),
        'permissions': Permission.objects.all(),
    })


# Create groups
@login_required(login_url='signin')
def create_group(request:HttpRequest):
    if request.method == "POST":
        name = request.POST.get('name')
        group, created= Group.objects.get_or_create(name= name)
        if created:
            return JsonResponse({'message': 'group is created successfully'}, status= 201)
        else:
            return JsonResponse({'message': "This group already exists"}, status= 400)
    return render(request, "core/groups.html")

@login_required(login_url='signin')
def add_permissions(request: HttpRequest, group_name:str):
    group= get_object_or_404(Group, name= group_name)

    # Select the models
    content_type= ContentType.objects.get_for_models(CustomUser, MedicalInsurance)
    custom_user_ct= content_type[CustomUser]
    medical_policy_ct= content_type[MedicalInsurance]

    # Add premissions to users
    customuser_add, created1= Permission.objects.get_or_create(codename= "add_customuser", content_type= custom_user_ct)
    customuser_change, created2= Permission.objects.get_or_create(codename= "change_customuser", content_type= custom_user_ct)
    customuser_delete, created3= Permission.objects.get_or_create(codename= "delete_customuser", content_type= custom_user_ct)
    customuser_view, created4= Permission.objects.get_or_create(codename= "view_customuser", content_type= custom_user_ct)

    # Add permissions to Medical policy
    medical_policy_add, created5= Permission.objects.get_or_create(codename= "add_medicalinsurance", content_type= medical_policy_ct)
    medical_policy_change, created6= Permission.objects.get_or_create(codename= "change_medicalinsurance", content_type= medical_policy_ct)
    medical_policy_delete, created7= Permission.objects.get_or_create(codename= "delete_medicalinsurance", content_type= medical_policy_ct)
    medical_policy_view, created8= Permission.objects.get_or_create(codename= "view_medicalinsurance", content_type= medical_policy_ct)
        
    if request.method == "POST":
        perm_ids= request.POST.getlist('permissions')

        for perm_id in perm_ids:
            permission= Permission.objects.get(id= perm_id)
            group.permissions.add(permission)
        return JsonResponse({
            'message': 'permssions are added'
        }, status= 201)
    
    return render(request, "core/permissions.html", {
        'group': group,
        'permissions': group.permissions.all(),
        'customuser_add': customuser_add,
        'customuser_change': customuser_change,
        'customuser_delete': customuser_delete,
        'customuser_view': customuser_view,
        'medical_policy_add': medical_policy_add,
        'medical_policy_change': medical_policy_change,
        'medical_policy_delete': medical_policy_delete,
        'medical_policy_view': medical_policy_view,
    })

@login_required(login_url='sigin')
def remove_permissions(request:HttpRequest, group_name:str):
    group= get_object_or_404(Group, name= group_name)
    group.permissions.clear()
    return redirect(reverse('add_permissions', args=[group.name]))


# Remove groups
@login_required(login_url='signin')
def remove_group(request: HttpRequest, group_name):
    group = get_object_or_404(Group, name= group_name)
    group.delete()
    return HttpResponseRedirect(reverse('groups'))


# Add users to groups to give some permissions
@login_required(login_url='signin')
def add_users_to_groups(request: HttpRequest):
    if request.method == 'POST':
        user_email = request.POST.get('user')
        group_name = request.POST.get('group')

        user = get_object_or_404(CustomUser, email= user_email)
        group = get_object_or_404(Group, name= group_name)

        user.groups.add(group)
        return JsonResponse({
            'message': 'User is added successfully',
            'user_name': user.first_name,
            'group_name': group.name,
        }, status= 200)
    return HttpResponseRedirect(reverse('home'))


# Remove users from groups
@login_required(login_url='signin')   
def remove_user_from_group(request: HttpRequest):
    if request.method == "POST":
        user_email= request.POST.get('email')

        user = get_object_or_404(CustomUser, email= user_email)
        user.groups.clear()
        return JsonResponse({
            'message': 'User is removed',
            'user_name': user.first_name,
        })
    return HttpResponseRedirect(reverse('users'))

@login_required(login_url='signin')
def new_policy(request:HttpRequest):
    if request.method == 'POST':
        form = NewPolicy(request.POST)
        if form.is_valid():
            policy= form.save()
            return redirect(reverse('payment_page', args=[policy.pk]))  
        else:
            print(form.errors)   
    else:
        form= NewPolicy()
    return render(request, "core/new_policy.html", {'form': form})

def family_member(request:HttpRequest):
    if request.method == "POST":
        family_form= NewFamilyMemeber(request.POST)
        if family_form.is_valid():
            family_form.save()
    else:
        family_form= NewFamilyMemeber()
    return render(request, "core/family_members.html", {'form': family_form})
    

def payment_page(request, policy_id):
    return render(request, 'core/payment_page.html', {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'policy_id': policy_id,
    })

@csrf_exempt
def create_checkout_session(request:HttpRequest, policy_id):
        if request.method == "POST":
            policy= get_object_or_404(MedicalInsurance, pk= policy_id)
            try:
                if policy.subscription == "single":
                    session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[{
                            'quantity': 1,
                            'price_data': {
                                'currency': 'usd',
                                'product_data': {
                                    'name': policy,
                                },
                                'unit_amount': int(policy.price),  
                            },
                        }],
                        mode='payment',
                        success_url= request.build_absolute_uri(reverse('success_payment')),
                        cancel_url= request.build_absolute_uri(reverse('cancel_payment')),
                    )
                    return JsonResponse({'id': session.id})
                elif policy.subscription == "family":
                    session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[{
                            'quantity': 1,
                            'price_data': {
                                'currency': 'usd',
                                'product_data': {
                                    'name': policy,
                                },
                                'unit_amount': int(policy.price),
                            },
                        }],
                        mode='payment',
                        success_url= request.build_absolute_uri(reverse('success_payment')),
                        cancel_url= request.build_absolute_uri(reverse('cancel_payment')),
                    )
                    return JsonResponse({'id': session.id})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status= 400)
            
def success_payment(request:HttpRequest):
    return JsonResponse({
        'message': 'Your payment process has succeeded'
    })

def cancel_payment(request:HttpRequest):
    return JsonResponse({
        'message': 'Your payment process is cancelled'
    })


@csrf_exempt
def stripe_webhook(request:HttpRequest):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        policy_id= session['metadata']['policy_id']

        handle_checkout_session(session)
        fulfill_order(policy_id)
    elif event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        policy_id= session['metadata']['policy_id']

        handle_payment_intent(payment_intent)
        fulfill_order(policy_id)
    # Add other event types you want to handle here

    return HttpResponse(status=200)

def handle_checkout_session(session):
    # implement your business logic
    print(f"Checkout Session was successful: {session}")

def handle_payment_intent(payment_intent):
    # implement your business logic
    print(f"Payment Intent was successful: {payment_intent}")

def fulfill_order(policy_id):
    policy= MedicalInsurance.objects.get(id= policy_id)
    policy.payment= "paid"
    policy.save()