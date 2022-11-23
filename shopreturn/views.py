from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from shopreturn.models import Prodreturn
from django.http.response import HttpResponse
from django.utils.dateformat import DateFormat
from datetime import datetime
from shoppay.models import Shoppaydetail
import logging
from shopcart.models import Shopcart

logger = logging.getLogger('shopreturn')
# Create your views here.

PAGE_SIZE = 10 # 한페이지에 5개의 글
PAGE_BLOCK = 5  # 넘어가는것 3개

class Returnlist(View):
    def get(self,request):
        template = loader.get_template("returnlist.html")
        memid = request.session.get( "memid" )
        returmcount = Prodreturn.objects.all().count()
        
        pagenum = request.GET.get( "pagenum" ) # 페이지num
        if not pagenum :
            pagenum = "1"
        
        pagenum = int( pagenum ) # 페이지num 을 보겠다
        
        # 한 페이지에 몇개씩 표기하겠다를 정해주어야함
        start = ( pagenum - 1) * int(PAGE_SIZE)        # ( 5 - 1 ) * 10      40
        end = start + int(PAGE_SIZE)                # 41 + 10 - 1            50
        if end > returmcount :
            end = returmcount
            
        dtos = Prodreturn.objects.filter(user_id=memid).order_by("-returnnum")[start:end] # 반품글 목록을 불러옴
        number = returmcount - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * int(PAGE_BLOCK) + 1      # 9 // 10 * 10 + 1    1
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK) # 페이지 고정
        endpage = startpage + int(PAGE_BLOCK) - 1                         # 1 + 10 -1           10
        pagecount = returmcount // int(PAGE_SIZE)
        if returmcount % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount  
        pages = range( startpage, endpage+1 )
        
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        
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
            "dtos" : dtos,
            "returmcount" : returmcount,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "cartcount" : cartcount,
            "cartlist":cartlist,
            "totalprice":totalprice,
            }
        
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass
    
#글쓰기    
class Returnwrite(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Returnwrite, self ).dispatch( request, *args, **kwargs )
    
    def get(self,request):
        template = loader.get_template("returnwrite.html")
        paydetailnum=request.GET["paydetailnum"] # 주문번호를 가져옴
        dto = Shoppaydetail.objects.get(paydetailnum=paydetailnum) # 주문 정보를 가져옴
        memid = request.session.get( "memid" )
        returnnum = request.GET.get("returnnum")
        
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        
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
            "returnnum" : returnnum,
            "dto":dto,
            "cartlist":cartlist,
            "cartcount":cartcount,
            "totalprice":totalprice,
            }
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context, request))
    
    def post(self,request):
        memid = request.session.get( "memid" )
        return_img = request.FILES["return_img"]
        paydetailnum = request.POST["paydetailnum"]
        dto = Shoppaydetail.objects.get(paydetailnum=paydetailnum)
        prodnum = request.POST["prodnum"]
        prodname = request.POST["prodname"]
        returndto = Prodreturn(
            prodnum = prodnum,
            paydetailnum = dto,
            user_id = request.POST["user_id"],
            prodname = request.POST["prodname"],
            return_title = request.POST["return_title"],
            return_content = request.POST["return_content"],
            return_img = return_img,
            return_regdate =DateFormat(datetime.now()).format("Ymd")
            )
        returndto.save() # 작성한 정보를 저장함
        logger.info("returnwritesuccess" + " " + "user_id:" + memid + " " + " returnnum:" + str(returndto.returnnum) + " " + "prodnum:" + returndto.prodnum + " " + "prodname:" + prodname + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return redirect("return:returnlist")
    
#글보기
class Returncontent(View):
    def get(self,request):
        returnnum = request.GET["returnnum"]
        pagenum = request.GET["pagenum"]
        number = request.GET["number"]
        memid = request.session.get( "memid" )
        dto = Prodreturn.objects.get(returnnum=returnnum) # 글번호가 db의 글번호와 일치하는 내용을 가져옴
        
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        
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
            
        context={
            "slr":slr,
            "memid" : memid,
            "returnnum" : returnnum,
            "pagenum" : pagenum,
            "number" : number,
            "dto":dto,
            "cartlist":cartlist,
            "cartcount":cartcount,
            "totalprice":totalprice,
            }
        template = loader.get_template("returncontent.html")
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context,request))
    
    def post(self,request):
        pass    


# 글 삭제
class Returndelete(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Returndelete,self).dispatch(request, *args, **kwargs)
    
    def get(self,request):
        memid = request.session.get( "memid" )
        returnnum = request.GET["returnnum"] # 해당 글 번호를 가져옴
        pagenum = request.GET["pagenum"] 
        template = loader.get_template("returndeletecheck.html")
        context={
            "returnnum" : returnnum,
            "pagenum" : pagenum,
            }
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context,request))
    
    def post(self,request):
        memid = request.session.get( "memid" )
        returnnum = request.POST["returnnum"] # 글번호를 가져옴
        pagenum = request.POST["pagenum"]
        dto = Prodreturn.objects.get(returnnum=returnnum) # 글번호와 맞는것을 삭제함
        dto.delete()
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return redirect("return:returnlist")    

#글수정(확인)    
class Returnmodify(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Returnmodify,self).dispatch(request, *args, **kwargs)
    
    def get(self,request):
        memid = request.session.get( "memid" )
        returnnum = request.GET["returnnum"] # 글번호확인
        pagenum = request.GET["pagenum"]
        
        context={
            "returnnum" : returnnum,
            "pagenum" : pagenum,
            }
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        template = loader.get_template("returnmodifycheck.html")
        return HttpResponse(template.render(context,request))
    
    def post(self,request):
        returnnum = request.POST["returnnum"]
        pagenum = request.POST["pagenum"]
        memid = request.session.get( "memid" )
        dto = Prodreturn.objects.get(returnnum = returnnum) # 글 번호가 맞는것을 가져와 html에 뿌림
        template = loader.get_template("returnmodifypro.html")
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        
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
            "returnnum" : returnnum,
            "pagenum" : pagenum,
            "dto" : dto,
            "cartlist":cartlist,
            "cartcount":cartcount,
            "totalprice":totalprice,
            }
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context,request))    
    
# 글 수정 하기
class Returnmodifypro(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Returnmodifypro,self).dispatch(request, *args, **kwargs)
    
    def get(self,request):
        pass
    
    def post(self,request):
        memid = request.session.get( "memid" )
        returnnum = request.POST["returnnum"]
        pagenum = request.POST["pagenum"]
        dto = Prodreturn.objects.get(returnnum = returnnum)
        
        dto.return_title = request.POST["return_title"]
        dto.return_content = request.POST["return_content"]
        dto.return_img = request.FILES["return_img"]
        dto.save() # 수정한 정보를 받아와 다시 저장함
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return redirect("return:returnlist")    
    