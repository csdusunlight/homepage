#coding:utf-8
from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions
import django_filters
from public.Paginations import MyPageNumberPagination
from wafuli.models import Project, InvestLog, TransList, Notice, SubscribeShip,\
    Announcement, WithdrawLog, Mark, BookLog
from public.permissions import CsrfExemptSessionAuthentication, IsAdmin
from restapi.serializers import UserSerializer, InvestLogSerializer,\
    TransListSerializer, NoticeSerializer, ProjectSerializer,\
    SubscribeShipSerializer, AnnouncementSerializer, DayStatisSerializer,\
    MarkSerializer, BookLogSerializer
from account.models import MyUser
from rest_framework.filters import SearchFilter,OrderingFilter
from public.permissions import IsOwner
from restapi.Filters import InvestLogFilter, SubscribeShipFilter, UserFilter,\
    TranslistFilter, WithdrawLogFilter
from django.db.models import Q
from wafuli_admin.models import DayStatis
from rest_framework.exceptions import ValidationError
from weixin.tasks import sendWeixinNotify
import logging
logger = logging.getLogger('wafuli')
# from django.core.mail import send_mail
# from wafuli.Filters import UserEventFilter
class BaseViewMixin(object):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    

    
class InvestlogList(BaseViewMixin, generics.ListCreateAPIView):
#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff:
#             return InvestLog.objects.all()
#         else:
#             return InvestLog.objects.filter(user=user)
    queryset = InvestLog.objects.all()
    serializer_class = InvestLogSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    ordering_fields = ('submit_time',)
    filter_class = InvestLogFilter
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

    
class TranslistList(BaseViewMixin, generics.ListAPIView):
    queryset = TransList.objects.all()
    permission_classes = (IsOwner,)
    serializer_class = TransListSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
    filter_class = TranslistFilter
    
class NoticeList(BaseViewMixin, generics.ListAPIView):
    def get_queryset(self):
        user = self.request.user
        return Notice.objects.filter(user=user)
    serializer_class = NoticeSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    ordering_fields = ('state', 'priority')
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
class NoticeDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = (IsOwner,)
    
class SubscribeShipList(BaseViewMixin, generics.ListAPIView):
    queryset = SubscribeShip.objects.all()
    def get_queryset(self):
        user = self.request.user
        return SubscribeShip.objects.filter(user=user)
    serializer_class = SubscribeShipSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    ordering_fields = ('id','project__priority','project__state', 'project__points')
    filter_class = SubscribeShipFilter
    pagination_class = MyPageNumberPagination

class SubscribeShipDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscribeShip.objects.all()
    serializer_class = SubscribeShipSerializer
    permission_classes = (IsOwner,)
    
class AnnouncementList(BaseViewMixin, generics.ListAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    pagination_class = MyPageNumberPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    ordering_fields = ('state', 'priority')
    


class MarkList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        return Mark.objects.filter(user=self.request.user)
    serializer_class = MarkSerializer
    pagination_class = MyPageNumberPagination
class BookLogList(BaseViewMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        return BookLog.objects.filter(user=self.request.user)
    serializer_class = BookLogSerializer
    pagination_class = MyPageNumberPagination
    def perform_create(self, serializer):
        generics.ListCreateAPIView.perform_create(self, serializer)
#         sendWeixinNotify([(self.request.user, serializer.instance)], 'book')
        try:
            sendWeixinNotify.delay([(self.request.user, serializer.instance),], 'book')
        except Exception, e:
            logger.error(e)
#         if self.request.user.is_book_email_notice:
#             qq_address = self.request.user.qq_number + '@qq.com'
#             instance = serializer.instance
#             pname = instance.project.title
#             subject = u'个人主页项目预约-' + pname
#             content = u"项目：" + instance.project.title + '\n' \
#                 + u"QQ：" + instance.qq_number + '\n' \
#                 + u"预约金额：" + instance.book_content + '\n' \
#                 + u"预约标期：" + instance.book_term + '\n' \
#                 + u"预约日期：" + str(instance.book_date) + '\n' \
#                 + u"留言：" + instance.remark or u"无"
#             content = content + '\n' + u"请到个人中心-预约管理中查看并处理。"
#             send_book_email(qq_address, subject, content)
# #         send_mail(subject, content, u'hunanjinyezi@126.com', ['690501772@qq.com',], auth_user='lvchunhui7@126.com',
# #                    auth_password='95123120290')
    
class ProjectList(BaseViewMixin, generics.ListAPIView):
    def get_queryset(self):
        user = self.request.user
        queryset = Project.objects.filter(state__in=['10','20'], )
        if user.is_staff:
            return queryset
        else:
            return queryset.filter(Q(is_official=True) | Q(user__id=user.id))
        
    serializer_class = ProjectSerializer
    filter_backends = (SearchFilter, django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    filter_fields = ['state','type','is_multisub_allowed','is_official']
    ordering_fields = ('state','pub_date','pinyin')
    search_fields = ('title', 'introduction')
    pagination_class = MyPageNumberPagination
    def perform_create(self, serializer):
        obj = serializer.save(is_official=False, user=self.request.user, state='10')
        SubscribeShip.objects.create(project=obj, user=self.request.user)

class ProjectDetail(BaseViewMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer