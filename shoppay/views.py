from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.template import loader
from django.http.response import HttpResponse
from shoppay.models import Shoppay, Shoppaydetail, Paydata
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateformat import DateFormat
from datetime import datetime
import logging
from shopproduct.models import Shopproduct
from shopmember.models import Shopmember

logger = logging.getLogger('shoppaymove')
# Create your views here.

# 구매 확인 페이지
class Payment(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super( Payment, self ).dispatch( request, *args, **kwargs )
    
    def get(self,request):
        template = loader.get_template("ordercheck.html")
        memid = request.session.get( "memid" )
        prodnum = request.GET.get("prodnum")
        paylist = Shoppay.objects.get(user_id=memid) # prodcontent 에서 구매를 눌렀을때 상품 정보를 저장하는데 그정보를 불러옴
        
        # paylist = Shoppay.objects.raw("""select a.paynum, a.prodcount, a.prodcolor, a.prodsize
        #         b.prodnum, b.prodname, b.prodprice, b.prodbrand, b.prodmainimg, b.prodprice*a.prodcount paytotal
        #         c.user_id, c.user_name, c.user_addr, c.user_addrt
        #         from Shoppay_Shoppay a inner join Shopproduct_Shopproduct b on(b.prodnum = a.prodnum)
        #         inner join Shopmember_Shopmember c on(a.user_id = %s)
        # """,(memid,))
        
        
        dale = 2500
        
        prodpay = paylist.prodnum.prodprice * paylist.prodcount # 구매 가격 계산
        total_pay = prodpay + dale   # 배달비 계산
        context = {
            "memid":memid,
            "prodnum":prodnum,
            "paylist":paylist,
            "dale":dale,
            "prodpay":prodpay,
            "total_pay":total_pay,
            }
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context,request))
    
    # 구매진행
    def post(self,request):
        memid = request.session.get( "memid" )
        user_id = Shopmember.objects.get(user_id = memid)
        dtos = Shoppay.objects.get(user_id=memid)
        prodoption = ""
        prodsize = request.POST["prodsize"]
        prodcolor = request.POST["prodcolor"]
        if prodsize and prodcolor:
            prodoption = prodsize + "/" + prodcolor 
        
        prodnum = request.POST["prodnum"]
        proddto = Shopproduct.objects.get(prodnum=prodnum)
        
        # 구매 최종
        dto = Shoppaydetail(
            prodnum = dtos.prodnum.prodnum,
            user_id = memid,
            user_name = request.POST["user_name"],
            user_tel = request.POST["user_tel"],
            addressee = request.POST["addressee"],
            addressee_tel = request.POST["addressee_tel"],
            user_addr = request.POST["user_addr"],
            user_addrt = request.POST["user_addrt"],
            prodmainimg = dtos.prodnum.prodmainimg,
            prodname = request.POST["prodname"],
            prodoption = prodoption,
            prodprice = request.POST["prodprice"],
            prodcount = request.POST["prodcount"],
            paytype = request.POST["paytype"],
            paycommant = request.POST["paycommant"],
            common_door = request.POST["common_door"],
            total_pay = request.POST["total_pay"],
            payreg_date = DateFormat(datetime.now()).format("Ymd"),
            )
        proddto.prodquantity = proddto.prodquantity - int(dto.prodcount) # 상품 제고 빼기
        
        if proddto.prodquantity <= 0: # 재고가 0일 경우 
            proddto.prodstatus ="품절" # 상품 상태를 품절로 바꿈
            proddto.save() # 그후 저장
        proddto.save() # 상품 재고 빠진것 저장
        dto.save() # 구매 정보 저장
        logger = logging.getLogger('shoppay')
        logger.info("paymentsuccess" + " " + "user_id:" + memid + " " + "gender:" + user_id.user_gender + " " + "paydetailnum:" + str(dto.paydetailnum) + " " + "prodnum:" + str(dto.prodnum)
                    + " " + "prodname:" + dto.prodname + " " + "prodoption:" + dto.prodoption + " " + "prodcount:" + str(dto.prodcount) + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        # 구매정보 저장
        data = Paydata(
            prodnum = dtos.prodnum,
            user_id = dtos.user_id,
            prodsize = dtos.prodsize,
            prodcolor = dtos.prodcolor,
            prodcount = dtos.prodcount,
            )
        data.save()
        # 상품페이지에서 넘아갈때 저장된부분 삭제
        dtos.delete()
        return redirect("pay:ordercomplite")

# 주문 취소
class Paydelete(View):
    def get(self,request):
        memid = request.session.get( "memid" )
        dto = Shoppay.objects.filter(user_id = memid) # pay에 들어간 것을받아옴
        dto.delete() # 그것을 지움
        return redirect("member:index")
    def post(self,reuqest):
        pass

# 주문 수정 체크
class Ordermodify(View):
    @method_decorator( csrf_exempt )
    def dispatch( self, request, *args, **kwargs ) :
        return super( Ordermodify, self ).dispatch( request, *args, **kwargs )
    
    def get(self,request):
        memid = request.session.get( "memid" )
        paydetailnum = request.GET["paydetailnum"] # 내가 주문수정을 누른 상품의 번호를 받아옴
        context={
            "memid":memid,
            "paydetailnum":paydetailnum,
            }
        template = loader.get_template("ordermodify.html")
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context,request))
    
    def post(self,request):
        memid = request.session.get( "memid" )
        paydetailnum = request.POST["paydetailnum"]
        paylist = Shoppaydetail.objects.get(paydetailnum=paydetailnum) # 구매 테이블에서 최종적으로 저장된 테이블에서 받아온 상품번호와 맞는것을 가져옴
        template = loader.get_template("ordermodifypro.html")
        
        dale = 2500
        
        prodpay = paylist.prodprice * paylist.prodcount # 재연산
        total_pay = prodpay + dale   
        
        context = {
            "memid":memid,
            "paydetailnum":paydetailnum,
            "paylist":paylist,
            "prodpay":prodpay,
            "dale":dale,
            "total_pay":total_pay,
            }
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context,request))
    
# 주문 수정 확인
class Ordermodifypro(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super( Ordermodifypro, self ).dispatch( request, *args, **kwargs )
    
    def get(self,request):
        pass
    def post(self,request):
        paydetailnum = request.POST["paydetailnum"]
        memid = request.session.get("memid")
        paylist = Shoppaydetail.objects.get(paydetailnum=paydetailnum) # 구매 테이블에서 최종적으로 저장된 테이블에서 받아온 상품번호와 맞는것을 가져옴
        
        paylist.addressee = request.POST["addressee"]
        paylist.addressee_tel = request.POST["addressee_tel"]
        paylist.user_addr = request.POST["user_addr"]
        paylist.user_addrt = request.POST["user_addrt"]
        paylist.paycommant = request.POST["paycommant"]
        paylist.common_door = request.POST["common_door"]
        paylist.paytype = request.POST["paytype"]
        paylist.save() # 변경된 정보를 다시 저장함
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return redirect("member:mypage")


# 주문 취소 이건 뺍시다
class Ordercancel(View):
    def get(self,request):
        pass
    def post(self,request):
        pass


# 구매 성공후 보여지는 페이지 -> 마이페이지로 이동
class Ordercomplite(View):
    def get(self,request):
        template = loader.get_template("ordercomplite.html")
        memid = request.session.get("memid")
        context = {
            "memid" : memid,
            }
        return HttpResponse(template.render(context,request))
    def post(self,request):
        pass
    