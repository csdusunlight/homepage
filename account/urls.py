from django.conf.urls import url
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', 'account.views.account', name='account_index'),
    url(r'^register/$', 'account.views.register', name='register'),
    url(r'^register_from_gzh/$', 'account.views.register_from_gzh', name='register_from_gzh'),
    url(r'^login/$', 'account.views.login', {'template_name': 'registration/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'registration/logged_out.html', 'next_page':'login'}, name='logout'),
    url(r'^password_change/$', 'account.views.password_change', name='password_change'),
    url(r'^change_pay_password/$', 'account.views.change_pay_password', name='change_pay_password'),
    url(r'^resetpw/$', 'account.forgot_passwd.forgot_passwd', name='forgot_passwd'),

]
