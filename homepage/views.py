#coding:utf-8
from django.shortcuts import render
from wafuli.models import SubscribeShip, Notice, Project, InvestLog
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from public.tools import login_required_ajax
from django.http.response import JsonResponse, Http404
from wafuli.tools import saveImgAndGenerateUrl
import datetime
from django.db import transaction
from django.db.models import F
from activity.views import on_submit
from collections import OrderedDict

# Create your views here.
@login_required
def index(request):
    recoms = list(SubscribeShip.objects.filter(user=request.user, is_recommend=True, is_on=True)[0:12])
    if len(recoms)==0:
        recoms = list(SubscribeShip.objects.filter(user=request.user, is_on=True)[0:4])
    recom_list = []
    for r in recoms:
        p = r.project
        data = {
            'id':p.id,
            'title' : p.title,
            'intrest': r.intrest if r.intrest else p.intrest,
            'price': r.price if r.price else p.cprice,
            'shortprice': r.shortprice if r.shortprice else p.shortprice,
            'term': p.term,
            'is_book':p.is_book,
            'range': p.investrange,
            'pic': p.picture_url(),
            'investrange': p.investrange,
            'strategy': p.strategy,
            'state':p.state,
            'is_multisub_allowed':p.is_multisub_allowed,
            'necessary_fields':p.necessary_fields,
            'marks':','.join([ x.name for x in r.marks.all()])
        }
        recom_list.append(data)
    notice_list = Notice.objects.filter(user=request.user)
    template = 'm_homepage.html' if request.mobile else 'homepage.html' 
    return render(request, template,{'recom_list':recom_list, 'notice_list':notice_list})



@login_required
def detail_project(request, id):
    project = Project.objects.get(id=id)
    sub = SubscribeShip.objects.get(project=id,user=request.user)
    intrest = sub.intrest if sub.intrest else project.intrest
    price = sub.price if sub.price else project.cprice
    template = 'm_detail_project.html' if request.mobile else 'detail_project.html' 
    return render(request, template ,{'id':id, 'project':project, 'intrest':intrest, 'price':price})

@csrf_exempt
@transaction.atomic
@login_required_ajax
def submitOrder(request):
    result = {}
    project_id = request.POST.get('project')
    invest_amount = request.POST.get('invest_amount')
    invest_term = request.POST.get('invest_term')
    invest_date = request.POST.get('invest_date')
    zhifubao = request.POST.get('zhifubao', '')
    qq_number = request.POST.get('qq_number', '')
    expect_amount = request.POST.get('expect_amount', '')
    invest_name = request.POST.get('invest_name', '')
    invest_mobile = request.POST.get('invest_mobile')
    remark = request.POST.get('remark', '')
    invest_amount = None if invest_amount=='' else invest_amount
    invest_term = None if invest_term=='' else invest_term
    invest_date = datetime.date.today() if invest_date=='' else invest_date
    submit_type = request.POST.get('submit_type', '1')
    project = Project.objects.get(id=project_id)
#     fields = re.split(r'[\s,]+', project.necessary_fields)
    if not ( project_id and invest_mobile ):
        result['code'] = 0
        result['msg'] = u"请提交投资手机号"
        return JsonResponse(result)
    if invest_date:
        invest_date = datetime.datetime.strptime(invest_date, "%Y-%m-%d")
    if not project.is_multisub_allowed or submit_type=='1':
        if project.company is None:
            queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project=project)
        else:
            queryset=InvestLog.objects.filter(invest_mobile=invest_mobile, project__company_id=project.company_id)
        if queryset.exclude(audit_state='2').exists():
            result['code'] = 1
            result['msg'] = u"该手机号（首投）已提交过，请勿重复提交"
            return JsonResponse(result)

    investlog=InvestLog.objects.create(user=request.user,project_id=project_id, invest_mobile=invest_mobile, invest_date=invest_date,
                             invest_name=invest_name, remark=remark, qq_number=qq_number, expect_amount=expect_amount,
                             zhifubao=zhifubao, invest_amount=invest_amount, submit_type=submit_type,
                              invest_term=invest_term, is_official=project.is_official,
                              submit_way='1', is_selfsub=False, audit_state='1')
    #活动插入
    on_submit(request, request.user, investlog)
    #活动插入结束
    project.points = F('points') + 1
    project.save(update_fields=['points',])
    imgurl_list = []
    if len(request.FILES)>6:
        result = {'code':-2, 'msg':u"上传图片数量不能超过6张"}
        return JsonResponse(result)
    for key in request.FILES:
        block = request.FILES[key]
        if block.size > 100*1024:
            result = {'code':-1, 'msg':u"每张图片大小不能超过100k，请重新上传"}
            return JsonResponse(result)
    for key in request.FILES:
        block = request.FILES[key]
        imgurl = saveImgAndGenerateUrl(key, block, 'screenshot')
        imgurl_list.append(imgurl)
    if imgurl_list:
        invest_image = ';'.join(imgurl_list)
        investlog.invest_image = invest_image
        investlog.save(update_fields=['invest_image',])
    result['code'] = 0
    return JsonResponse(result)

@login_required
def search(request):
    template = 'search.html'
    return render(request, template, {})


@login_required
def quick_sumbit(request):
    user = request.user
    subs = SubscribeShip.objects.filter(user=user).select_related('project').order_by('project__szm')
    dic = OrderedDict()
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
        param = {}
        param.update(id=id, title=title, logo=logo, szm=szm, pinyin=pinyin, necessary_fields=necessary_fields,
                     is_multisub_allowed = is_multisub_allowed)
        prolist = dic.get(key, [])
        if not prolist:
            dic[key] = prolist
        prolist.append(param)
    template = 'm_quicksub.html' if request.mobile else 'quicksub.html' 
    return render(request, template, {'projects':dic})