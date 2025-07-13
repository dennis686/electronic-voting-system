from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('login/', views.voter_login, name='login'),
    path('logout/', views.voter_logout, name='logout'),
    path('vote/', views.vote, name='vote'),
    path('results/', views.results, name='results'),
    path('manage-voters/', views.manage_voters, name='manage_voters'),

    # Region API
    path('api/constituencies/<int:county_id>/', views.get_constituencies, name='get_constituencies'),
    path('api/wards/<int:constituency_id>/', views.get_wards, name='get_wards'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='accounts_login'),
]
