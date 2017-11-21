#coding:utf-8
from django.shortcuts import render, redirect
from docs.models import Document
from django.contrib.auth.decorators import login_required
from public.tools import login_required_ajax
from django.http.response import JsonResponse, Http404
from django.db.models import F

# Create your views here.

def display_doc(request, id):
    doc = Document.objects.get(id=id)
    doc.view_count = F('view_count')+1
    doc.save(update_fields=['view_count',])
    return render(request, 'display_doc.html', {'doc':doc})
