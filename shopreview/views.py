from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from shopreview.models import Shopreview
from django.utils.dateformat import DateFormat
from datetime import datetime
from django.template import loader
from django.http.response import HttpResponse
import logging
from shopcart.models import Shopcart
from shoppay.models import Shoppaydetail

logger = logging.getLogger('shopreview')
# Create your views here.
class Review(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Review, self ).dispatch( request, *args, **kwargs )
    
    def get(self,request):
        pass
    def post(self,request):
        memid = request.session.get( "memid" )
        reviewdto = Shopreview(
            prodnum = request.POST["prodnum"],
            user_id = request.POST["user_id"],
            reviewtitle = request.POST["reviewtitle"],
            reviewcontent = request.POST["reviewcontent"],
            reviewimg = request.FILES["reviewimg"],
            reviewrating = request.POST["reviewrating"],
            reviewregdate = DateFormat(datetime.now()).format("Ymd")
            )
        reviewdto.save() # 리뷰 작성시 작성한 내용을 받아와 저장함
        logger.info("reviewsuccess" + " " + "user_id:" + memid + " " + "prodnum:" + reviewdto.prodnum + " " + "reviewnum:" + str(reviewdto.reviewnum) + " " + "reviewrating:" + str(reviewdto.reviewrating) + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


#==============================================================================================================================================================================================
# 모달이용했기에 사용 안함
class Reviewmodify(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Reviewmodify, self ).dispatch( request, *args, **kwargs )
    
    def get(self, request):
        reviewnum = request.GET["reviewnum"]
        prodnum = request.GET["prodnum"]
        memid = request.session.get( "memid" )
        context = {
            "reviewnum" : reviewnum,
            "prodnum": prodnum,
            "memid" : memid,
            }
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        template = loader.get_template( "reviewmodifycheck.html" )
        return HttpResponse(template.render(context, request))
        
    def post(self, request):
        reviewnum = request.POST["reviewnum"]
        prodnum = request.POST["prodnum"]
        memid = request.session.get( "memid" )
        dto = Shopreview.objects.get( reviewnum = reviewnum )
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
        context = {
            "cartlist":cartlist,
            "cartcount":cartcount,
            "totalprice":totalprice,
            "reviewnum" : reviewnum,
            "prodnum": prodnum,
            "memid" : memid,
            "dto" : dto,
            }
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        template = loader.get_template( "reviewmodify.html" )
        return HttpResponse(template.render(context, request)) 
#==============================================================================================================================================================================================


# 리뷰 수정
class Reviewmodifypro(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Reviewmodifypro,self).dispatch(request, *args, **kwargs)
    
    def get(self,request):
        pass
        
    def post(self,request):
        memid = request.session.get( "memid" )
        prodnum = request.POST["prodnum"]
        reviewnum = request.POST["reviewnum"]
        dto = Shopreview.objects.get(reviewnum = reviewnum)
        
        dto.reviewtitle = request.POST["reviewtitle"]
        dto.reviewcontent = request.POST["reviewcontent"]
        dto.reviewimg = request.FILES["reviewimg"]
        dto.reviewrating = request.POST["reviewrating"]
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        dto.save() # 수정된 내용을 받아와 다시 저장함
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found')) # 그후 현재 페이지에 남아있도록함

# 리뷰 삭제
class Reviewdelete(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        
        return super(Reviewdelete, self ).dispatch( request, *args, **kwargs )
    def get(self, request) :
        template = loader.get_template( "reviewdelete.html" )
        reviewnum = request.GET["reviewnum"] # 번호를 받아와 확인하는 페이지를 띄움
        prodnum = request.GET["prodnum"]
        memid = request.session.get( "memid" )
        context={
            "memid" : memid,
            "reviewnum" : reviewnum,
            "prodnum" : prodnum,
            }
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context,request))
    
    def post(self, request):
        memid = request.session.get( "memid" )
        prodnum = request.POST["prodnum"]
        reviewnum = request.POST["reviewnum"]
        dto = Shopreview.objects.get(reviewnum=reviewnum) # 번호가 db에 저장된 번호와 같은것을 바당옴
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        dto.delete() # 삭제함
        return redirect("member:mypage")