#coding:utf-8
from django.shortcuts import render
from .models import App, MyUser
from django.http.response import JsonResponse
from .jwt_session_auth import jwt_login
from weixin_python.client import WXAPPAPI
from django.views.decorators.csrf import csrf_exempt
import json
from xiaochengxu.models import WXUser
from rest_framework import generics, permissions
from public.permissions import CsrfExemptSessionAuthentication, IsWxOwner, IsWXSelf,\
    IsWXAuthenticated
from wafuli.models import InvestLog, SubscribeShip, Project
from restapi.serializers import InvestLogSerializer
import django_filters
from public.Paginations import MyPageNumberPagination
from rest_framework.exceptions import ValidationError
from xiaochengxu.serializers import InvestLogSerializerForXCX, WXUserSerializer
import logging
logger = logging.getLogger('wafuli')

# Create your views here.
def login(request):
    ret = {}
    app_id = request.app_id
    code = request.GET.get('code')
    if not app_id:
        ret = {'msg':u'app_id错误','code':-1}
        return JsonResponse(ret)
    if not code:
        ret = {'msg':u'app_id错误','code':-1}
        return JsonResponse(ret)
    try:
        app = App.objects.get(app_id=app_id)
    except:
        ret = {'msg':u'app_id错误','code':-1}
        return JsonResponse(ret)
    api = WXAPPAPI(appid=app_id, app_secret=app.app_secret)
    code = request.GET.get('code')
    session_info = api.exchange_code_for_session_key(code=code)
    
    # 获取session_info 后
    
    session_key = session_info.get('session_key')
    openid = session_info.get('openid')
    user = app.user
    assert(user == request.user)
    user, created = WXUser.objects.get_or_create(app_id=app_id, openid=openid, 
                                                 defaults = {'user':user})
#     if created:
#         user.set_password('123456')
#         user.save(update_fields=['password'])
    token = jwt_login(user, request)
    ret = {'token':token,'code':0}
    return JsonResponse(ret)
#     crypt = WXBizDataCrypt(app_id, session_key)
    
    # encrypted_data 包括敏感数据在内的完整用户信息的加密数据
    # iv 加密算法的初始向量
    # 这两个参数需要js获取
#     user_info = crypt.decrypt(encrypted_data, iv)

# def update_userinfo(request):
#     user = request.wxuser
#     userinfo = json.loads(request.body)
# #     fields = ['nickName', 'avatarUrl', 'city', 'country', 'gender', 'province','language']
# #     update_dict = dict((k,v) for k, v in userinfo.items() if k in fields)
#     user.nickName = userinfo.get('nickName','')
#     user.avatarUrl = userinfo.get('avatarUrl','')
#     user.city = userinfo.get('city','')
#     user.country = userinfo.get('country','')
#     user.gender = userinfo.get('gender','')
#     user.province = userinfo.get('province','')
#     user.language = userinfo.get('language','')
#     user.save()
#     return JsonResponse({})

def bind_userinfo(request):
    user = request.wxuser
    userinfo = json.loads(request.body)
#     fields = ['nickName', 'avatarUrl', 'city', 'country', 'gender', 'province','language']
#     update_dict = dict((k,v) for k, v in userinfo.items() if k in fields)
    user.nickName = userinfo.get('nickName','')
    user.avatarUrl = userinfo.get('avatarUrl','')
    user.city = userinfo.get('city','')
    user.country = userinfo.get('country','')
    user.gender = userinfo.get('gender','')
    user.province = userinfo.get('province','')
    user.language = userinfo.get('language','')
    user.save()
    return JsonResponse({})

class BaseViewMixin(object):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (IsWXAuthenticated,)
class InvestlogList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        wxuser = self.request.wxuser
        return InvestLog.objects.filter(wxuser=wxuser)
    serializer_class = InvestLogSerializer
    pagination_class = MyPageNumberPagination
    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        is_official = project.is_official
        category = project.category
        invest_mobile = serializer.validated_data['invest_mobile']
        if not project.is_multisub_allowed:
            print project.company
            if project.company is None:
                queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project=project)
            else:
                queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project__company_id=project.company_id)
            if queryset.exclude(audit_state='2').exists():    
                raise ValidationError({'detail':u"投资手机号重复"})
        serializer.save(is_official=is_official, category=category, audit_state='1', user=self.request.user)

class InvestlogDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = InvestLog.objects.all()
    permission_classes = (IsWXSelf,)
    serializer_class = InvestLogSerializerForXCX
    def perform_update(self, serializer):
        project = serializer.validated_data['project']
        id = serializer.validated_data['id']
        invest_mobile = serializer.validated_data['invest_mobile']
        if not project.is_multisub_allowed:
            if project.company is None:
                queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project=project)
            else:
                queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project__company_id=project.company_id)
            if queryset.exclude(audit_state='2').exclude(id=id).exists():    
                raise ValidationError({'detail':u"投资手机号重复"})
        serializer.save()
        
class WXUserList(BaseViewMixin, generics.ListAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return WXUser.objects.all()
        else:
            return WXUser.objects.filter(user=user)
    serializer_class = WXUserSerializer
    pagination_class = MyPageNumberPagination

class WXUserDetail(BaseViewMixin, generics.RetrieveUpdateAPIView):
    queryset = InvestLog.objects.all()
    permission_classes = (IsWXSelf,)
    serializer_class = WXUserSerializer
    def get_object(self):
        return self.request.wxuser

#coding:utf-8
import hashlib
from django.http.response import HttpResponse,Http404, JsonResponse

def handle_message(request):
    if request.method == 'GET':
        token = '1hblsqTsdfsdfsd'
        timestamp = str(request.GET.get('timestamp'))
        nonce = str(request.GET.get('nonce'))
        signature = str(request.GET.get('signature'))
        echostr = str(request.GET.get('echostr'))
        paralist = [token,timestamp,nonce]
        paralist.sort()
        parastr = ''.join(paralist)
        siggen = hashlib.sha1(parastr).hexdigest()
        if siggen==signature:
            return HttpResponse(echostr)
        else:
            raise Http404
    else:
        othercontent = autoreply(request)
        return HttpResponse()
 

import xml.etree.ElementTree as ET
def autoreply(request):
    try:
        webData = request.body
        xmlData = ET.fromstring(webData)

        msg_type = xmlData.find('MsgType').text
        ToUserName = xmlData.find('ToUserName').text
        FromUserName = xmlData.find('FromUserName').text
        CreateTime = xmlData.find('CreateTime').text
        toUser = FromUserName
        fromUser = ToUserName
        openid = toUser
        content = ''
        if msg_type == 'text':
            message = xmlData.find('Content').text
            prolist = list(Project.objects.filter(is_official=True, title__contains=message))
            for pro in prolist:
                content += '\n' if content else ''
                content += pro.title + u'：' + pro.strategy
        elif msg_type == 'user_enter_tempsession':
            sessionfrom = xmlData.find('SessionFrom').text
            if sessionfrom.startswith('project_'):
                project_id = sessionfrom.replace('project_', '')
                project = Project.objects.get(id=project_id)
                content = pro.title + u'：' + pro.strategy
    except Exception, e:
        logger.error(e)
        content = u"客服繁忙，请稍后再试"
    replyMsg = TextMsg(toUser, fromUser, content.encode('utf-8'))
    return replyMsg.send()

class Msg(object):
    def __init__(self, xmlData):
        self.ToUserName = xmlData.find('ToUserName').text
        self.FromUserName = xmlData.find('FromUserName').text
        self.CreateTime = xmlData.find('CreateTime').text
        self.MsgType = xmlData.find('MsgType').text
        self.MsgId = xmlData.find('MsgId').text

import time
class TextMsg(Msg):
    def __init__(self, toUserName, fromUserName, content):
        self.__dict = dict()
        self.__dict['ToUserName'] = toUserName
        self.__dict['FromUserName'] = fromUserName
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['Content'] = content

    def send(self):
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{Content}]]></Content>
        </xml>
        """
        return XmlForm.format(**self.__dict)