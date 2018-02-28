from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    
    url(r'^login/$', views.login, name='login'),
    url(r'^update_userinfo/$', views.update_userinfo, name='update_userinfo'),
#     url(r'^logout/$', auth_views.logout, {'template_name': 'registration/logged_out.html', 'next_page':'login'}, name='logout'),

]
