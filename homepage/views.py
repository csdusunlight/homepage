#coding:utf-8
from django.shortcuts import render
from wafuli.models import SubscribeShip, Notice, Project, InvestLog
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from public.tools import login_required_ajax
from django.http.response import JsonResponse, Http404
from wafuli.tools import saveImgAndGenerateUrl
import datetime

# Create your views here.
@login_required
def index(request):
    recoms = list(SubscribeShip.objects.filter(user=request.user, is_recommend=True, is_on=True)[0:10])
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
            'term': p.term,
            'range': p.investrange,
            'pic': p.picture_url(),
            'investrange': p.investrange,
            'strategy': p.strategy,
            'state':p.state,
            'is_multisub_allowed':p.is_multisub_allowed,
            'necessary_fields':p.necessary_fields,
        }
        recom_list.append(data)
    notice_list = Notice.objects.filter(user=request.user)
    return render(request, 'my_homepage.html',{'recom_list':recom_list, 'notice_list':notice_list})

@login_required
def m_index(request):
    recoms = list(SubscribeShip.objects.filter(user=request.user, is_recommend=True, is_on=True)[0:10])
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
            'term': p.term,
            'range': p.investrange,
            'pic': p.picture_url(),
            'investrange': p.investrange,
            'strategy': p.strategy,
            'state':p.state,
        }
        recom_list.append(data)
    notice_list = Notice.objects.filter(user=request.user)
    return render(request, 'm_homepage.html',{'recom_list':recom_list, 'notice_list':notice_list})

@login_required
def expsubmit_project(request, id):
    project_title = Project.objects.get(id=id).title
    project = Project.objects.get(id=id,user=request.user)
    sub = SubscribeShip.objects.get(project=id,user=request.user)
    intrest = sub.intrest if sub.intrest else project.intrest
    price = sub.price if sub.price else project.cprice
    return render(request, 'm_expsubmit_project.html',{'id':id, 'project_title':project_title, 'intrest':intrest, 'price':price})

@login_required
def detail_project(request, id):
    project = Project.objects.get(id=id,user=request.user)
    sub = SubscribeShip.objects.get(project=id,user=request.user)
    intrest = sub.intrest if sub.intrest else project.intrest
    price = sub.price if sub.price else project.cprice
    return render(request, 'detail_project.html',{'id':id, 'project':project, 'intrest':intrest, 'price':price})

@csrf_exempt
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
                              is_selfsub=False, audit_state='1')
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
