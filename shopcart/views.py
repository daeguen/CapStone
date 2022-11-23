from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.template import loader
from django.http.response import HttpResponse
from shopcart.models import Shopcart, Shopcartpay
from shopproduct.models import Shopproduct
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from shoppay.models import Shoppaydetail
from django.utils.dateformat import DateFormat
from datetime import datetime
import logging

logger = logging.getLogger('shopcart')
# Create your views here.

# 장바구니 보기
class Prodcart(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Prodcart, self ).dispatch( request, *args, **kwargs )
    
    def get(self,request):
        template = loader.get_template("prodcartpage.html")
        memid = request.session.get( "memid" )
        cartcount = Shopcart.objects.filter(user_id=memid).count() # user_id의 장바구니에 담긴 상품의 수를 샘
        # cartlist = Shopcart.objects.raw("""
        #     select a.cartnum, a.prodcount, b.prodnum, b.prodname, b.prodprice, b.prodbrand, b.prodmainimg, b.prodprice*a.prodcount prototal,
        #     c.user_id
        #     from Shopcart_Shopcart a inner join Shopproduct_Shopproduct b on(a.prodnum = b.prodnum)
        #         inner join Shopmember_Shopmember c on(a.user_id=%s)
        #         order by a.cartnum desc
        #         group by user_id
        #     """,(memid,))
        cartlist = Shopcart.objects.filter(user_id=memid).order_by("-cartnum") # 카트 번호순대로 정렬함
        
        # 총가격 계산
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
        
        context = {
            "slr":slr,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount":cartcount,
            }
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context,request))
    
    # 장바구니 전체구매
    def post(self,request):
        memid = request.session.get( "memid" )
        cartlist = Shopcart.objects.filter(user_id=memid)
        prodcolor = request.POST["prodcolor"]
        prodsize = request.POST["prodsize"]
        prodcount =request.POST["prodcount"]
        
        # 반복문을 통해 장바구니 전체 구매
        try :
            dto = Shopcartpay.objects.get(user_id=memid) 
        except :
            for i in cartlist :
                dto=Shopcartpay(
                    prodnum = i.prodnum,
                    user_id = i.user_id,
                    prodcolor=i.prodcolor,
                    prodsize=i.prodsize,
                    prodcount=i.prodcount
                    ) # 옵션값도 반복문으로 돌려야함
                dto.save()
                logger = logging.getLogger('shoppagemove')
                logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return redirect("prodcart:cartpaydetail")
        
# 장바구니 삭제
class Cartdelete(View):
    def get(self,request):
        memid = request.session.get( "memid" )
        cartnum = request.GET["cartnum"]
        dto = Shopcart.objects.get(cartnum=cartnum) # cartnum인것을 dto에 저장
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        dto.delete() # 해당하는 cartnum을 삭제함
        return redirect("prodcart:prodcart")
    def post(self,request):
        pass

# 장바구니 ul 에서 삭제
class Baseartdelete(View):
    def get(self,request):
        memid = request.session.get( "memid" )
        cartnum = request.GET["cartnum"]
        dto = Shopcart.objects.get(cartnum=cartnum)
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        dto.delete() # 해당하는 cartnum을 삭제함
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found')) # redirect시 현재 페이지 유지시킴
    
    def post(self,request):
        pass


# 장바구니 수정
class Cartupdate(View):
    def get(self,request):
        memid = request.session.get( "memid" )
        cartnum = request.GET["cartnum"]
        dto = Shopcart.objects.get(cartnum=cartnum) # cartnum이 cartnum인것을 받아와 dto
        dto.prodcount = request.GET["prodcount"]
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        dto.save() # 변경이 되면 해당하는 값을 받아와 저장함
        return redirect("prodcart:prodcart")
    def post(self,request):
        pass

# 장바구니 구매 페이지  
class Cartpaydetail(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Cartpaydetail, self ).dispatch( request, *args, **kwargs )
    
    def get(self,request):
        template = loader.get_template("cartordercheck.html")
        memid = request.session.get( "memid" )
        prodnum = request.GET.get("prodnum")
        cartpaylist = Shopcartpay.objects.filter(user_id=memid) # cartlist에 저장된 정보들중 user_id와 맞는것을 가져옴
        
        dale = 2500 # 배달비
        
        # 상품의 총 가격
        totalprice = 0
        for pricesum in cartpaylist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
        
        # 배달비 포함가격
        total_pay = totalprice + dale
        
        context={
            "memid":memid,
            "prodnum":prodnum,
            "cartpaylist":cartpaylist,
            "totalprice":totalprice,
            "dale":dale,
            "total_pay":total_pay,
            }
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context,request))
    
    def post(self,request):
        memid = request.session.get( "memid" )
        dtos = Shopcartpay.objects.filter(user_id=memid)
        cart = Shopcart.objects.filter(user_id=memid) 
        prodoption = ""
        prodsize = request.POST["prodsize"]
        prodcolor = request.POST["prodcolor"]
        
        # 반복문을 통해 구매한 상품정보들을 저장함 (묶음이 아닌 단일로)
        for i in dtos:
            dto = Shoppaydetail(
                prodnum = i.prodnum.prodnum,
                user_id = memid,
                user_name = request.POST["user_name"],
                user_tel = request.POST["user_tel"],
                addressee = request.POST["addressee"],
                addressee_tel = request.POST["addressee_tel"],
                user_addr = request.POST["user_addr"],
                user_addrt = request.POST["user_addrt"],
                prodmainimg = i.prodnum.prodmainimg,
                prodname = i.prodnum.prodname,
                prodoption = i.prodsize+"/"+i.prodcolor,
                prodprice = i.prodnum.prodprice,
                prodcount = i.prodcount,
                paytype = request.POST["paytype"],
                paycommant = request.POST["paycommant"],
                common_door = request.POST["common_door"],
                total_pay = request.POST["total_pay"],
                payreg_date = DateFormat(datetime.now()).format("Ymd"),
                )
            prodnum = i.prodnum.prodnum
            proddto = Shopproduct.objects.get(prodnum=prodnum)
            proddto.prodquantity = proddto.prodquantity - int(i.prodcount)
            if proddto.prodquantity <= 0: # 재고가 0일 이하 일경우
                proddto.prodstatus ="품절" # 품절로 변경
                proddto.save() # 품절로 변경후 저장시킴
            proddto.save()
            logger = logging.getLogger('shoppay')
            logger.info("cartpaysuccess" + " " + "user_id:" + memid + " " + "paydetailnum:" + str(dto.paydetailnum) + "prodnum:" + str(dto.prodnum) + " " + "prodname:" + dto.prodname + " " + "prodoption:" + dto.prodoption + " " + "prodprice:" + str(dto.prodprice) + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
            dto.save()
        dtos.delete() # 구매 디테일 db를 삭제함
        cart.delete() # 장바구니에 담긴 상품들을 삭제함
        return redirect("pay:ordercomplite")

# 카트 결제 취소
class Cartpaydelete(View):
    def get(self,request):
        memid = request.session.get( "memid" )
        dto = Shopcartpay.objects.filter(user_id = memid)
        dto.delete() # 구매 디테일 db를 삭제함
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return redirect("member:index")
    def post(self,reuqest):
        pass

# 카트 전체 삭제
class Cartpaydeleteall(View):
    def get(self,request):
        memid = request.session.get( "memid" )
        dto = Shopcart.objects.filter(user_id=memid)
        dto.delete() # 카트의 상품 전부를 삭제함
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return redirect("prodcart:prodcart")
    
    def post(self,request):
        pass