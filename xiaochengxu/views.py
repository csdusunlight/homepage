#coding:utf-8
from django.shortcuts import render
from .models import App, MyUser
from django.http.response import JsonResponse
from .jwt_session_auth import jwt_login
from weixin_python.client import WXAPPAPI
from django.views.decorators.csrf import csrf_exempt
import json
from xiaochengxu.models import WXUser

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
    user, created = WXUser.objects.get_or_create(app_id=app_id, openid=openid)
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

@csrf_exempt
def update_userinfo(request):
    user = request.jwt_user
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