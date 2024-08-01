from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('<int:user_id>/', views.profile, name='profile'),
    path('login/', views.login_user, name='login'),
    path('create/', views.create_user, name='create_user'),
    path('logout/', views.logout_user, name='logout'),
    path('update/', views.update_user, name='update_user'),

    path('staff/', views.staff_home, name='staff_home'),
    path('manger/', views.manger_home, name='manger_home')
]
