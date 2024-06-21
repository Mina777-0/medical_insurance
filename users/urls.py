from django.urls import path
from . import views


urlpatterns= [
    #path('signin', views.signin, name="signin"),
    path('users_home/', views.users_home, name="users_home"),
    path('signout', views.signout, name="signout"),
    path('api_signin', views.api_signin, name= "api_signin"),
    path('insurance_policy', views.insurance_policy, name="insurance_policy"),
    path('get_policies', views.get_policies, name="get_policies"),
    path('add_family_member', views.add_family_member, name="add_family_member"),
    path('get_family_members', views.get_family_members, name="get_family_members"),
]
