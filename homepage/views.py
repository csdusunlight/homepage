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
    return render(request, 'm_expsubmit_project.html',{'id':id, 'project_title':project_title})

@csrf_exempt
@login_required_ajax
def submitOrder(request):
    result = {}
    project_id = request.POST.get('invest_amount', None)
    invest_amount = request.POST.get('invest_amount', None)
    invest_term = request.POST.get('invest_term', '')
    invest_date = request.POST.get('invest_date', datetime.date.today())
    zhifubao = request.POST.get('zhifubao', '')
    zhifubao_name = request.POST.get('zhifubao_name', '')
    qq_number = request.POST.get('qq_number', '')
    expect_amount = request.POST.get('expect_amount', None)
    invest_name = request.POST.get('invest_name', '')
    invest_mobile = request.POST.get('invest_mobile', None)
    remark = request.POST.get('remark', '')
    if not invest_mobile or not project_id:
        result['code'] = 0
        result['msg'] = u""
        return JsonResponse(result)
    investlog=InvestLog.objects.create(user=request.user,project_id=project_id, invest_mobile=invest_mobile, invest_date=invest_date,
                             invest_name=invest_name, remark=remark, qq_number=qq_number, expect_amount=expect_amount,
                             zhifubao=zhifubao, zhifubao_name=zhifubao_name, invest_amount=invest_amount,
                              invest_term=invest_term)
    imgurl_list = []
    if len(request.FILES)>6:
        result = {'code':-2, 'msg':u"�ϴ�ͼƬ�������ܳ���3��"}
        return JsonResponse(result)
    for key in request.FILES:
        block = request.FILES[key]
        if block.size > 100*1024:
            result = {'code':-1, 'msg':u"ÿ��ͼƬ��С���ܳ���100k���������ϴ�"}
            return JsonResponse(result)
    for key in request.FILES:
        block = request.FILES[key]
        imgurl = saveImgAndGenerateUrl(key, block, 'screenshot')
        imgurl_list.append(imgurl)
    invest_image = ';'.join(imgurl_list)
    investlog.invest_image = invest_image
    investlog.save(update_fields=['invest_image',])
    result['code'] = 0
    return JsonResponse(result)