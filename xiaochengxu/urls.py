from django.conf.urls import url
from . import views

urlpatterns = [
    
    url(r'^login/$', views.login, name='login'),
#     url(r'^update_userinfo/$', views.update_userinfo, name='update_userinfo'),
    url(r'^investlogs/$', views.InvestlogList.as_view()),
    url(r'^investlogs/(?P<pk>[0-9]+)/$', views.InvestlogDetail.as_view(), kwargs={'partial':True}),
    url(r'^wxusers/$', views.WXUserList.as_view()),
    url(r'^update_userinfo/$', views.update_userinfo),
    url(r'^handle_message/$', views.handle_message, name='handle_message'),
    url(r'^get_project_list/$', views.get_project_list, name='get_project_list'),
    url(r'^submit_screenshot/$', views.submit_screenshot, name='submit_screenshot'),
]
