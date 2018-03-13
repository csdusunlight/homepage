#coding:utf-8
'''
Created on 2017年7月3日

@author: lch
'''
from rest_framework import permissions
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
#         if request.method in permissions.SAFE_METHODS:
#             return True

        # 写的请求只对对象的创建者开放
        if not request.user.is_authenticated():
            return False
        return request.user.is_staff

    
from rest_framework.authentication import SessionAuthentication 

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
    
class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated():
            return False
        return obj.user == request.user
class IsSelf(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated():
            return False
        return obj == request.user
class IsWxOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.wxuser:
            return obj.wxuser == request.wxuser
        else:
            return False
class IsWXSelf(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.wxuser
    
class IsWXAuthenticated(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        if request.wxuser:
            return True
        else:
            return False
