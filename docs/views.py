#coding:utf-8
from django.shortcuts import render, redirect
from docs.models import Document
from django.contrib.auth.decorators import login_required
from public.tools import login_required_ajax
from django.http.response import JsonResponse, Http404

# Create your views here.

def display_doc(request, id):
    doc = Document.objects.get(id=id)
    return render(request, 'display_doc.html', {'doc':doc})
