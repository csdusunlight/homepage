
from django.conf.urls import url,include
from django.views.generic.base import TemplateView
import homepage.views
# url_about = [
#     url(r'^aboutus/$', 'wafuli.views.aboutus', name="about"),
#     url(r'^report/$', 'wafuli.views.report'),
#     url(r'^coop/$', 'wafuli.views.coop'),
#     url(r'^notice/$', 'wafuli.views.notice'),
#     url(r'^contact/$', 'wafuli.views.contact'),
#     url(r'^statement/$', 'wafuli.views.statement'),
# ]
urlpatterns = [
    url(r'^$', homepage.views.index, name='hm_index'),
    url(r'^mobile$', homepage.views.index),
    url(r'^detail/project/(?P<id>[0-9]+)/$', homepage.views.detail_project, name='detail_project'),
    url(r'^submitOrder/$', homepage.views.submitOrder, name='submitOrder'),
    url(r'^search/$', homepage.views.search, name='search'),
]
