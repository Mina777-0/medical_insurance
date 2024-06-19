from django.urls import path
from . import views

urlpatterns = [
    path('no_access', views.no_access, name="no_access"),
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('admin_home/', views.admin_home, name="admin_home"),
    path('signout', views.signout, name="signout"),
    path('users/', views.users, name="users"),
    path('groups/', views.groups, name="groups"),
    path('groups/create_group', views.create_group, name="create_group"),
    path('groups/add_permissions/<str:group_name>/', views.add_permissions, name="add_permissions"),
    path('groups/remove_permissions/<str:group_name>/', views.remove_permissions, name="remove_permissions"),
    path('group/<str:group_name>', views.remove_group, name="remove_group"),
    path('add_users_to_groups', views.add_users_to_groups, name="add_to_group"),
    path('remove_user_from_group', views.remove_user_from_group, name="remove_user_from_group"),
    path('new_policy/', views.new_policy, name="new_policy"),
    path('payments/<int:policy_id>/', views.payment_page, name="payment_page"),
    path('payments/create_checkout_session/<int:policy_id>/', views.create_checkout_session, name="create_checkout_session"),
    path('payments/payment_succeed/', views.success_payment, name="success_payment"),
    path('payments/cancel_payment/', views.cancel_payment, name="cancel_payment"),
    path('stripe/webhook/', views.stripe_webhook, name="stripe_webhook"),
]