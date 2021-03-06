'''
Created on 20170919

@author: lch
'''

import logging
logger=logging.getLogger('wafuli')
from django.http.response import Http404
from account.models import MyUser
class SubdomainMiddleware(object):
    def process_request(self, request):
        logger.info( request.META.keys())
        domain_parts = request.get_host().split('.')
        if len(domain_parts) == 3:
            domain_name = domain_parts[0]
            if domain_name == "test":
                request.user = MyUser.objects.get(id=1)
            else:
                try:
                    request.user = MyUser.objects.get(domain_name=domain_name)
                except:
                    raise Http404
        return None