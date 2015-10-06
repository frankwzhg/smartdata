from django.conf.urls import patterns, url
from accounts import views


## create account application url list

urlpatterns = patterns('',
                       url(r'^registrate/$', views.user_registration_view, name='user_registrate'),
                       url(r'^confirm/(?P<activation_key>\w+)/', views.user_active_view, name='user_active'),
                       url(r'^login/$', views.user_login_view, name='user_login'),
                       url(r'^logout/$', views.user_logout, name='user_logout'),
                       url(r'^resetpassword/$', views.reset_password_view, name='user_resetpassword'),
                       url(r'^changepassword/$', views.change_passwd_view, name='user_changepassword'),
                       url(r'^updateprofile/$', views.update_profile_view, name='user_updateprofile'),
                       )