from django.conf.urls import url
from docs import views

urlpatterns = [
    url(r'^(?P<id>[0-9a-zA-Z]+)/$', views.display_doc, name='display_doc'),
]
