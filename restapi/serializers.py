#coding:utf-8
'''
Created on 2017年8月10日

@author: lch
'''
from rest_framework import serializers
from wafuli.models import Project, InvestLog, TransList, Notice, SubscribeShip,\
    Announcement, WithdrawLog, Mark, BookLog
from account.models import MyUser, ApplyLog
from wafuli_admin.models import DayStatis
from wafuli.models import Company

class UserSerializer(serializers.ModelSerializer):
    real_name = serializers.CharField(source="user_bankcard.first.real_name")
    bank = serializers.CharField(source="user_bankcard.first.get_bank_display")
    card_number = serializers.CharField(source="user_bankcard.first.card_number")
    class Meta:
        model = MyUser
        fields = ('id', 'mobile', 'username', 'qq_number', 'qq_name', 'date_joined', 'with_total','accu_income',
                  'level', 'picture', 'profile', 'balance', 'is_active', 'color', 'real_name', 'bank', 'card_number',
                  'domain_name', 'cs_qq')
        read_only_fields = ('id', 'mobile', 'balance', 'is_active', 'level',)
        
class ProjectSerializer(serializers.ModelSerializer):
#     subscribers = UserSerializer(many=True)
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('user', 'pub_date', 'state', 'is_official', 'category')
        
class InvestLogSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    invest_mobile = serializers.CharField(source='get_encrypt_mobile', read_only=True)
    class Meta:
        model = InvestLog
        fields = ('submit_time', 'invest_mobile', 'invest_amount', 'audit_state', 'project_title', 'audit_time', 
                  'invest_term', 'preaudit_state')
class TransListSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(source='user.mobile', read_only=True)
    user_balance = serializers.CharField(source='balance', read_only=True)
    username = serializers.CharField(source='user.qq_number', read_only=True)
    class Meta:
        model = TransList
        fields = '__all__'
        
class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'
        read_only_fields = ('user', 'time')

class ApplyLogSerializer(serializers.ModelSerializer):
    admin_mobile = serializers.CharField(source='admin_user.mobile')
    class Meta:
        model = ApplyLog
#         fields = '__all__'
        exclude = ('password',)
# SubscribeShip
class SubscribeShipSerializer(serializers.ModelSerializer):
    project_category = serializers.CharField(source='project.category', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)
    project_intro = serializers.CharField(source='project.introduction', read_only=True)
    project_price = serializers.CharField(source='get_project_price', read_only=True)
    project_cprice = serializers.CharField(source='project.cprice', read_only=True)
    project_shortprice = serializers.CharField(source='project.shortprice', read_only=True)
    project_investrange = serializers.CharField(source='project.investrange', read_only=True)
    project_intrest = serializers.CharField(source='project.intrest', read_only=True)
    project_term = serializers.CharField(source='project.term', read_only=True)
    project_state = serializers.CharField(source='project.state', read_only=True)
    project_strategy = serializers.CharField(source='project.strategy', read_only=True)
    project_introduction = serializers.CharField(source='project.introduction', read_only=True)
    project_picture = serializers.CharField(source='project.picture_url', read_only=True)
    project_marks = serializers.CharField(source='project.marks_list', read_only=True)
    project_is_official = serializers.CharField(source='project.is_official', read_only=True)
    project_is_book = serializers.BooleanField(source='project.is_book', read_only=True)
    submit_num = serializers.IntegerField(source='project.points', read_only=True)
    necessary_fields = serializers.CharField(source='project.necessary_fields', read_only=True)
    optional_fields = serializers.CharField(source='project.optional_fields', read_only=True)
    project_is_multisub_allowed = serializers.BooleanField(source='project.is_multisub_allowed', read_only=True)
    marks = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = SubscribeShip
        fields = '__all__'
        read_only_fields = ('user', 'project', 'myprice')
        
class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'
        read_only_fields = ('time',)
        
class DayStatisSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayStatis
        fields = '__all__'
class WithdrawLogSerializer(serializers.ModelSerializer):
    real_name = serializers.CharField(source="user.user_bankcard.first.real_name")
    bank = serializers.CharField(source="user.user_bankcard.first.get_bank_display")
    card_number = serializers.CharField(source="user.user_bankcard.first.card_number")
    username = serializers.CharField(source='user.username', read_only=True)
    mobile = serializers.CharField(source='user.mobile', read_only=True)
    admin_mobile = serializers.CharField(source='admin_user.mobile', read_only=True)
    qq_number = serializers.CharField(source='user.qq_number', read_only=True)
#     balance = serializers.CharField(source='user.banlance', read_only=True)
#     username = serializers.CharField(source='user.username', read_only=True)
#     username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = WithdrawLog
        fields = '__all__'
#         read_only_fields = ('audit_time','submit_time','user','audit_state',
#                              'settle_amount','return_amount', "admin_user", "is_official"), 'time', 'content_type', 'object_id', 'user', 'username', 'project')

class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = '__all__'
        
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        
class BookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookLog
        fields = '__all__'