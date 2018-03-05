from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    
    url(r'^login/$', views.login, name='login'),
#     url(r'^update_userinfo/$', views.update_userinfo, name='update_userinfo'),
    url(r'^investlogs/$', views.InvestlogList.as_view()),
    url(r'^investlogs/(?P<pk>[0-9]+)/$', views.InvestlogDetail.as_view(), kwargs={'partial':True}),
    url(r'^wxusers/$', views.WXUserList.as_view()),
    url(r'^update_userinfo/$', views.WXUserDetail.as_view(), kwargs={'partial':True}),
]
