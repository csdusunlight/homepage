#coding:utf-8
from django.shortcuts import render, redirect
from docs.models import Document
from django.contrib.auth.decorators import login_required
from public.tools import login_required_ajax
from django.http.response import JsonResponse, Http404
from django.db.models import F

# Create your views here.

def display_doc(request, id):
    if request.method == 'POST':
        secret = request.POST.get('secret')
        request.session['secret' + str(id)] = secret
        return JsonResponse({})
    else:
        secret = request.session.get('secret' + str(id), '')
        try:
            doc = Document.objects.get(id=id, is_on=True, secret__in = [secret,''])
            view_count = doc.view_count
            doc.view_count = F('view_count')+1
            doc.save(update_fields=['view_count',])
            doc.view_count = view_count + 1
            return render(request, 'display_doc.html', {'doc':doc})
        except:
            return render(request, 'hide_doc.html', )
    
# def get_doc_content(request):
#     secret = request.POST.get('secret', '')
#     doc_id = request.POST.get('id', '')
#     ret = {}
#     try:
#         doc = Document.objects.get(id=doc_id, secret=secret)
#         ret['code'] = 0
#         ret['content'] = doc.content
#     except:
#         ret['code'] = 1
#         ret['msg'] = u"口令输入错误"
#     return JsonResponse(ret)
    