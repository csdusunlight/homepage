'''
Created on 20170919

@author: lch
'''
from django.http.response import Http404
from account.models import MyUser
class SubdomainMiddleware(object):
    def process_request(self, request):
        domain_parts = request.get_host().split('.')
        if len(domain_parts) == 3:
            qq_number = domain_parts[0]
            if qq_number == "test":
                qq_number = '690501772'
            try:
                request.user = MyUser.objects.get(qq_number=qq_number)
            except:
                raise Http404
        request.prehost= 'm'
        return None