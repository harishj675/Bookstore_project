from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordChangeDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('', views.profile, name='profile'),
    path('login/', views.login_user, name='login'),
    path('create/', views.create_user, name='create_user'),
    path('logout/', views.logout_user, name='logout'),
    path('update/', views.update_user, name='update_user'),

    path('staff/', views.staff_home, name='staff_home'),
    path('manger/', views.manger_home, name='manger_home'),

    # password_changes
    path('change-password/',
         PasswordChangeView.as_view(template_name='user/password_change.html',
                                    success_url='/users/password_change/done/'), name="password-change"),
    path('password_change/done/',
         PasswordChangeView.as_view(template_name='user/password_change_done.html'),
         name="password_change_done"),

    # password reset
    path('password_reset/', PasswordResetView.as_view(template_name='registration/password_reset_form.html'),
         name='password_reset'),
    path('password_reset/done', PasswordChangeDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name="password_reset_complete"),
]
