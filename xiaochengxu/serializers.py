#coding:utf-8
'''
Created on 2018年1月16日

@author: lch
'''
from rest_framework import serializers
from wafuli.models import InvestLog
from xiaochengxu.models import WXUser

class WXUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = WXUser
        fields = '__all__'
        read_only_fields = ('openid', 'app')

class InvestLogSerializerForXCX(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    audit_state_des = serializers.CharField(source='get_audit_state_display', read_only=True)
    class Meta:
        model = InvestLog
        fields = ('audit_state', 'project_title','submit_time','invest_mobile','invest_name','invest_amount','invest_term',
                             'invest_date', 'zhifubao',)
        read_only_fields = ('submit_time')