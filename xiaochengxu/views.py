#coding:utf-8
from .models import App
from django.http.response import JsonResponse
from .jwt_session_auth import jwt_login
from weixin_python.client import WXAPPAPI
from django.views.decorators.csrf import csrf_exempt
import json
from xiaochengxu.models import WXUser
from rest_framework import generics
from public.permissions import CsrfExemptSessionAuthentication, IsWxOwner, IsWXSelf,\
    IsWXAuthenticated
from wafuli.models import InvestLog, SubscribeShip, Project
from public.Paginations import MyPageNumberPagination
from rest_framework.exceptions import ValidationError
from xiaochengxu.serializers import InvestLogSerializerForXCX, WXUserSerializer
import logging
from wafuli.tools import saveImgAndGenerateUrl
from django.db.models import Q
from django.shortcuts import render
from django.core.urlresolvers import reverse
from dragon.settings import FANSHU_DOMAIN
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
#     assert(user == request.user or request.user is None)
    user, created = WXUser.objects.get_or_create(app_id=app_id, openid=openid, 
                                                 defaults = {'user':user})
#     if created:
#         user.set_password('123456')
#         user.save(update_fields=['password'])
    token = jwt_login(user, request)
    ret = {'token':token,'code':0, 'zhifubao':user.zhifubao, 'mobile':user.mobile,
           'qq_number':user.qq_number, 'qq_name':user.qq_name}
    return JsonResponse(ret)
#     crypt = WXBizDataCrypt(app_id, session_key)
    
    # encrypted_data 包括敏感数据在内的完整用户信息的加密数据
    # iv 加密算法的初始向量
    # 这两个参数需要js获取
#     user_info = crypt.decrypt(encrypted_data, iv)

def update_userinfo(request):
    user = request.wxuser
    userinfo = json.loads(request.body)
    for k, v in userinfo.items():
        if v and hasattr(user, k):
            setattr(user, k, v)
    user.save()
    return JsonResponse({'code':0})
def get_userinfo(request):
    user = request.wxuser
    userinfo = json.loads(request.body)
    for k, v in userinfo.items():
        if v and hasattr(user, k):
            setattr(user, k, v)
    user.save()
    return JsonResponse({'code':0})

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
    serializer_class = InvestLogSerializerForXCX
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
    permission_classes = (IsWxOwner,)
    serializer_class = InvestLogSerializerForXCX
    def perform_update(self, serializer):
        project = serializer.instance.project
        id = serializer.instance.id
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
import hashlib, urllib, requests
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
        jsonres = autoreply(request)
        touser = jsonres['touser']
        access_token = WXUser.objects.get(openid=touser).app.access_token
#         logger.info('openid:'+str(jsonres))
#         access_token = Dict.objects.get(key='access_token_xcx').value
        url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token='+access_token
#         headers = {"Content-Type": "application/json"} 
        ret = requests.post(url, data=json.dumps(jsonres,ensure_ascii=False).encode('utf-8'))
        logger.info(ret.text)
        return HttpResponse('')
 

import xml.etree.ElementTree as ET
import re
def autoreply(request):
    openid = ''
    try:
        webData = request.body
        xmlData = ET.fromstring(webData)

        msg_type = xmlData.find('MsgType').text
        ToUserName = xmlData.find('ToUserName').text
        FromUserName = xmlData.find('FromUserName').text
        CreateTime = xmlData.find('CreateTime').text
        openid = FromUserName
        content = ''
        wxuser = WXUser.objects.get(openid=openid)
        if msg_type == 'text':
            message = xmlData.find('Content').text
            user = wxuser.user
            prolist = list(Project.objects.filter(Q(is_official=True)|Q(user=user)).filter(state='10', 
                            title__contains=message))
            for pro in prolist:
                content += '\n' if content else ''
                content += pro.title + u'：' + pro.strategy
        elif msg_type == 'event' :
            event = xmlData.find('Event').text
            if event == 'user_enter_tempsession':
                sessionfrom = xmlData.find('SessionFrom').text
                if sessionfrom.startswith('project_'):
                    project_id = sessionfrom.replace('project_', '')
                    project = Project.objects.get(id=project_id)
                    content = project.title + u'：' + project.strategy
                else:
                    weixin = wxuser.app.cs_weixin
                    content = u"很高兴为您服务，查询攻略请回复平台名称，其他问题请询问人工客服，客服微信号：" + weixin
    except Exception, e:
        logger.error(e)
        content = u"客服繁忙，请稍后再试"
    if content=='':
        app = wxuser.app
        app_id = app.app_id
        response = {
            "touser":openid,
            "msgtype":"link",
            "link": {
                "title": "欢迎光临" + app.app_name,
                "description": "暂时没有您要查找的平台，请点击本条消息加微信，随时找我聊天",
                "url": 'http://' + FANSHU_DOMAIN + reverse('xcx:get_contact_brcode',kwargs={'app_id':app_id}),
                "thumb_url": ('http://' + FANSHU_DOMAIN + app.contact_brcode.url) if app.contact_brcode else ''
            }
        }
#     content = content.encode('utf-8')
    else:
        response = {
            "touser":openid,
            "msgtype":"text",
            "text":
            {
                "content":content,
            }
        }
#     response = json.dumps(response)
#     response=re.sub('test',u"人工",response)
# #     response = response.encode('utf-8')
    return response

def get_project_list(request):
    user = request.user
    if not user.is_authenticated():
        return JsonResponse([], safe=False)
    subs = SubscribeShip.objects.filter(user=user, is_on=True).select_related('project').order_by('project__szm')
    projectNameList = []
    group_key = ''
    group_dic = {}
    for sub in subs:
        project = sub.project
        id = project.id
        title = project.title
        logo = project.picture_url()
        szm = project.szm
        pinyin = project.pinyin
        necessary_fields = project.necessary_fields
        is_multisub_allowed = project.is_multisub_allowed
        key = szm[0:1]
        key = key.upper()
        param = {}
        param.update(id=id, name=title, logo=logo, key=key, necessary_fields=necessary_fields,
                     is_multisub_allowed = is_multisub_allowed)
        if key != group_key:
            if group_dic:
                projectNameList.append(group_dic)
            group_dic = {'title':key,'item':[]}
            group_key = key
        group_dic['item'].append(param)
    if group_dic:
        projectNameList.append(group_dic)
    return JsonResponse(projectNameList, safe=False)


@csrf_exempt
def submit_screenshot(request):
    print 'code1'  #jzy
    imgurl_list = []
    result = {}
    id = request.POST.get('id')
    investlog = InvestLog.objects.get(id=id)
    invest_image = investlog.invest_image + ';'
    if len(request.FILES)>6:
        result = {'code':-2, 'msg':u"上传图片数量不能超过3张"}
        return JsonResponse(result)
    for key in request.FILES:
        block = request.FILES[key]
        print block.size
        if block.size > 300*1024:
            result = {'code':-1, 'msg':u"每张图片大小不能超过100k，请重新上传"}
            return JsonResponse(result)
    print request.FILES
    for key in request.FILES:
        block = request.FILES[key]
#         if key.find('.') == -1 and block.content_type.startswith('image/'):
#             key += '.' + block.content_type.split('/')[1]
        imgurl = saveImgAndGenerateUrl(key, block, 'screenshot')
        imgurl_list.append(imgurl)
    invest_image += ';'.join(imgurl_list)
    investlog.invest_image = invest_image
    investlog.save(update_fields=['invest_image',])
    result['code'] = 0
    print result['code']  #jzy
    print 'code'  #jzy
    return JsonResponse(result)

def get_contact_brcode(request, app_id):
    app = App.objects.get(app_id=app_id)
    brcode = ''
    if app.contact_brcode:
        brcode = app.contact_brcode.url
    return render(request, 'contact.html', {'brcode':brcode})
    