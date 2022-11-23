from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.template import loader
from shopproduct.models import Shopproduct
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from shopmember.models import Shopmember
from shopreview.models import Shopreview
from shoppay.models import Shoppay, Shoppaydetail
import logging
from django.utils.dateformat import DateFormat
from datetime import datetime
from shopcart.models import Shopcart
from django.db.models.aggregates import Avg, Sum, Count
import math

logger = logging.getLogger('shopprodmove')
# Create your views here.

PAGE_SIZE = 30
PAGE_BLOCK = 5

# 상품보기 페이지 및 장바구니 저장, 단품 구매
class Prodcontent(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Prodcontent, self ).dispatch( request, *args, **kwargs )
    
    def get(self,request):
        prodnum = request.GET["prodnum"]
        memid = request.session.get( "memid" )
        dto = Shopproduct.objects.get(prodnum=prodnum)
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        reviewcount = Shopreview.objects.all().filter(prodnum=prodnum).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
        
        paycount = Shoppaydetail.objects.filter(user_id=memid).filter(prodnum=prodnum).count()
        reviewdto = Shopreview.objects.order_by("-reviewnum").filter(prodnum=prodnum)
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
        
        # prodavg = Shopreview.objects.raw("""
        # select reviewnum, AVG(reviewrating), prodnum from shopreview_shopreview
        # where prodnum = prodnum
        # """)
        
        # 상품의 대한 별점리뷰 평균
        if reviewcount :
            avg = Shopreview.objects.filter(prodnum=prodnum).aggregate(Sum("reviewrating")) # 리뷰를 합산함
            avgs = list(avg.values()) # 평균값을 계산
            ratingavg = round(avgs[0]/reviewcount,1) # 하나의 대한 상품이 index로 들어가기에 0번으로 지정, 그후 소수점 1자리까지 출력하도록
            ratchar = math.ceil(5-ratingavg) # 빈별을 출력하기위해 최대 5점에서 빼줌
            
            context = {
                "slr" : slr,
                "ratchar":ratchar,
                "ratingavg":ratingavg,
                "dto" : dto,
                "memid" : memid,
                "prodnum" : prodnum,
                "cartlist":cartlist,
                "totalprice":totalprice,
                "cartcount" : cartcount,
                "reviewdto" : reviewdto,
                "paycount" : paycount,
                "reviewcount" : reviewcount,
                }   
            if memid :
                logger = logging.getLogger('shopproduct')
                logger.info("productcontent" + " " + "user_id:" + memid + " " + "prodnum:" + str(dto.prodnum) + " " + "prodname:" + dto.prodname + " " + "prodimg:" + str(dto.prodmainimg) + " " + "prodbrand:" + dto.prodbrand + " " + "proditems:" + dto.proditems + " " + "prodname:" + dto.prodname + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
            else :
                pass    
            template = loader.get_template("productcontent.html")
            return HttpResponse(template.render(context,request))
        else : # 평점이 없을경우에 에러가남 그래서 있을경우 없을경우로 나눠서 보내준것
            context = {
                "slr":slr,
                "dto" : dto,
                "memid" : memid,
                "prodnum" : prodnum,
                "cartlist":cartlist,
                "totalprice":totalprice,
                "cartcount" : cartcount,
                "reviewdto" : reviewdto,
                "paycount" : paycount,
                "reviewcount" : reviewcount,
                }
            if memid :
                logger = logging.getLogger('shopproduct')
                logger.info("productcontent" + " " + "user_id:" + memid + " " + "prodnum:" + str(dto.prodnum) + " " + "prodname:" + dto.prodname + " " + "prodimg:" + str(dto.prodmainimg) + " " + "prodbrand:" + dto.prodbrand + " " + "proditems:" + dto.proditems + " " + "prodname:" + dto.prodname + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
            else :
                pass
            template = loader.get_template("productcontent.html")
            return HttpResponse(template.render(context,request))
        
    def post(self,request):
        prodnum = request.POST["prodnum"]
        memid = request.session.get( "memid" )
        user_id = Shopmember.objects.get(user_id=memid)
        
        # submit을 2개 쓴 것
        if request.method == 'POST': # 상품디테일 method가 post
            if 'add_cart' in request.POST: # 그중 이름이 add_cart인것
                try :
                    Shopcart.objects.get(user_id=memid).filter(prodnum=prodnum)
                except :
                    cart = Shopcart(
                        prodnum = Shopproduct.objects.get(pk=prodnum),
                        user_id = user_id,
                        prodcolor = request.POST["prodcolor"],
                        prodsize = request.POST["prodsize"],
                        prodcount = request.POST["prodcount"],
                        )
                    logger = logging.getLogger('shopcart')
                    logger.info("addcart" + " " + "user_id:" + memid + "prodnum:" + str(cart.prodnum.prodnum) + " " + "prodname:" + cart.prodnum.prodname + " " + "prodcolor:" + cart.prodcolor + " " + "prodsize:" + cart.prodsize + " " + "prodcount:" + str(cart.prodcount) + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
                    cart.save() # 해당 상품을 카트에 저장
                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found')) # 장바구니 추가했을시 현재 페이지 유지시킴
    
        if request.method == 'POST': # 상품디테일 method가 post
            if 'pay' in request.POST: # 그중 이름이 pay 인것을 실행했을경우 -> 이부분은 urls에 하나 추가로 작성 해주어야함
                try :
                    paydto = Shoppay.objects.get(user_id=memid)
                    if Shoppay.user_id :
                        paydto.delete() # 뒤로가기 버튼을 눌렀을때 다시 저장되도록 막아본것.. 더 좋은 방법이 있을거같음
                        paydto = Shoppay(
                            prodnum = request.POST["prodnum"],
                            user_id = user_id,
                            prodsize = request.POST["prodsize"],
                            prodcolor = request.POST["prodcolor"],
                            prodcount = request.POST["prodcount"]
                        )
                        paydto.save() # 해당 하는 정보들을 pay에 덮어씀
                except :
                    paydto = Shoppay(
                        prodnum = Shopproduct.objects.get(pk=prodnum),
                        user_id = user_id,
                        prodsize = request.POST["prodsize"],
                        prodcolor = request.POST["prodcolor"],
                        prodcount = request.POST["prodcount"]
                        )
                    paydto.save() # 해당 하는 정보들을 pay에 저장
                    logger = logging.getLogger('shoppagemove')
                    logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
                return redirect("pay:payment") # 구매상세 페이지 이동

#### 규호 ####
# 노스페이스 
class Northfacepage(View):
    def get(self,request):
        template = loader.get_template("northface.html")
        memid = request.session.get( "memid" )
        prodbrand = request.GET.get("prodbrand")
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        
        # 규호의 장난질 ( 페이지 관련 )
        count = Shopproduct.objects.filter(prodbrand="노스페이스").count()
        
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count
            
        cartlist = Shopcart.objects.filter(user_id=memid)
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
        
        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        pages = range( startpage, endpage+1 )
        
        
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        # 상품 정렬
        sort = request.GET.get("sort", "")
        if sort == 'minprice' : # 최소가격순
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand="노스페이스")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'maxprice': # 최대 가격순
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand="노스페이스")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'name': # 이름순
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand="노스페이스")[start:end] # dtos 이거 리스트임
            
        
        else : # 최신순
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand="노스페이스")[start:end] # dtos 이거 리스트임
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
        
            
        context = {
            "slr":slr,
            "sort":sort,
            "dtos":dtos,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
            }
        if memid :
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :
            pass
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass    

# 노스페이스 상세
class Nfc(View):
    def get (self,request):
        template=loader.get_template("nfc.html")
        
        memid = request.session.get( "memid" )
        prodbrand= request.GET['prodbrand']
        proditems= request.GET['proditems']
        
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
            
        count = Shopproduct.objects.filter( prodbrand="노스페이스",proditems=proditems).count()
        
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count
              
        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        pages = range( startpage, endpage+1 )
        
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        
        # dtos=Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] 
        
        sort = request.GET.get("sort", "")
        if sort == 'minprice' :
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'maxprice':
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'name':
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        else :
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        if memid:
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :    
            pass
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
        
        context={
            "slr":slr,
            "sort":sort,
            "prodbrand":prodbrand,
            "proditems":proditems,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
        }
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass


# 캉골
class Kangpage(View):
    def get(self,request):
        template = loader.get_template("kang.html")
        memid = request.session.get( "memid" )
        prodbrand = request.GET.get("prodbrand")
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        
        # 규호의 장난질 ( 페이지 관련 )
        count = Shopproduct.objects.filter(prodbrand="캉골").count()
        
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count
        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        pages = range( startpage, endpage+1 )
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
        
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        
        sort = request.GET.get("sort", "")
        if sort == 'minprice' :
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand="캉골")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'maxprice':
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand="캉골")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'name':
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand="캉골")[start:end] # dtos 이거 리스트임
            
        
        else :
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand="캉골")[start:end] # dtos 이거 리스트임
        
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
        
        
        context = {
            "slr":slr,
            "sort":sort,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
            }
        if memid :
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :
            pass
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass


# 캉골 상세
class Kangc(View):
    def get (self,request):
        memid = request.session.get( "memid" )
        prodbrand= request.GET['prodbrand']
        proditems= request.GET['proditems']
        
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
            
        count = Shopproduct.objects.filter( prodbrand="캉골",proditems=proditems).count()
        
        template=loader.get_template("kangc.html")
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count
        dtos=Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] 
        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        pages = range( startpage, endpage+1 )
        
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        sort = request.GET.get("sort", "")
        if sort == 'minprice' :
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'maxprice':
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'name':
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        else :
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
            
        if memid:
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :    
            pass
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
        
        context={
            "slr":slr,
            "sort":sort,
            "prodbrand":prodbrand,
            "proditems":proditems,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
        }
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass
    
# Hmm   
class Hmpage(View):
    def get(self,request):
        template = loader.get_template("hm.html")
        memid = request.session.get( "memid" )
        # dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand="H&M")
        
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
            
        # 규호의 장난질 ( 페이지 관련 )
        count = Shopproduct.objects.filter(prodbrand="HnM").count()
        
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count

        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        pages = range( startpage, endpage+1 )
        
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        sort = request.GET.get("sort", "")
        if sort == 'minprice' :
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand="HnM")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'maxprice':
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand="HnM")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'name':
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand="HnM")[start:end] # dtos 이거 리스트임
            
        
        else :
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand="HnM")[start:end] # dtos 이거 리스트임
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
        
        context = {
            "slr":slr,
            "sort":sort,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
            }
        if memid :
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :
            pass
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass
    
# H&M 상세    
class Hmc(View):
    def get (self,request):
        memid = request.session.get( "memid" )
        prodbrand= request.GET['prodbrand']
        proditems= request.GET['proditems']
        
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
            
        count = Shopproduct.objects.filter( prodbrand="HnM",proditems=proditems).count()
        
        template=loader.get_template("hmc.html")
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count
        dtos=Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] 
        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        pages = range( startpage, endpage+1 )
        
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        sort = request.GET.get("sort", "")
        if sort == 'minprice' :
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'maxprice':
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'name':
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        else :
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
            
        if memid:
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :    
            pass
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
        
        context={
            "slr":slr,
            "sort":sort,
            "prodbrand":prodbrand,
            "proditems":proditems,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
        }
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass

# 스파오   
class Spaopage(View):
    def get(self,request):
        template = loader.get_template("spao.html")
        memid = request.session.get( "memid" )
        # dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand="스파오")
        
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
            
        # 규호의 장난질 ( 페이지 관련 )
        count = Shopproduct.objects.filter(prodbrand="스파오").count()
        
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count
        
        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        pages = range( startpage, endpage+1 )
        
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        sort = request.GET.get("sort", "")
        if sort == 'minprice' :
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand="스파오")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'maxprice':
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand="스파오")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'name':
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand="스파오")[start:end] # dtos 이거 리스트임
            
        else :
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand="스파오")[start:end] # dtos 이거 리스트임
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
        
        context = {
            "slr":slr,
            "sort":sort,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
            }
        if memid :
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :
            pass
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass

# 스파오 상세
class Spaoc(View):
    def get (self,request):
        memid = request.session.get( "memid" )
        prodbrand= request.GET['prodbrand']
        proditems= request.GET['proditems']
        
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
            
        count = Shopproduct.objects.filter( prodbrand="스파오",proditems=proditems).count()
        
        template=loader.get_template("spaoc.html")
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count
        dtos=Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] 
        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        pages = range( startpage, endpage+1 )
        
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        sort = request.GET.get("sort", "")
        if sort == 'minprice' :
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'maxprice':
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'name':
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        else :
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
            
        if memid:
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :    
            pass
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
        
        context={
            "slr":slr,
            "sort":sort,
            "prodbrand":prodbrand,
            "proditems":proditems,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
        }
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass  

#### 정국 ####
# 뉴발란스
class Nbpage(View):
    def get(self,request):
        template = loader.get_template("nb.html")
        memid = request.session.get( "memid" )
        prodbrand = request.GET.get("prodbrand")
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        
        # 규호의 장난질 ( 페이지 관련 )
        count = Shopproduct.objects.filter(prodbrand="뉴발란스").count()
        
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count
        
        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        pages = range( startpage, endpage+1 )
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
        
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        sort = request.GET.get("sort", "")
        if sort == 'minprice' :
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand="뉴발란스")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'maxprice':
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand="뉴발란스")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'name':
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand="뉴발란스")[start:end] # dtos 이거 리스트임
            
        else :
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand="뉴발란스")[start:end] # dtos 이거 리스트임
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
         
        context = {
            "slr":slr,
            "sort":sort,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
            }
        if memid :
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :
            pass
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass

# 뉴발란스 상세
class Nbc(View):
    def get (self,request):
        memid = request.session.get( "memid" )
        prodbrand= request.GET['prodbrand']
        proditems= request.GET['proditems']
        
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
            
        count = Shopproduct.objects.filter( prodbrand="뉴발란스",proditems=proditems).count()
        
        template=loader.get_template("nbc.html")
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count
        dtos=Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] 
        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        pages = range( startpage, endpage+1 )
        
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        sort = request.GET.get("sort", "")
        if sort == 'minprice' :
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'maxprice':
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'name':
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        else :
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
            
        if memid:
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :    
            pass
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
        
        context={
            "slr":slr,
            "sort":sort,
            "prodbrand":prodbrand,
            "proditems":proditems,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
        }
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass 


# 무지
class Mujipage(View):
    def get(self,request):
        template = loader.get_template("muji.html")
        memid = request.session.get( "memid" )
        prodbrand = request.GET.get("prodbrand")
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        
        # 규호의 장난질 ( 페이지 관련 )
        count = Shopproduct.objects.filter(prodbrand="무지").count()
        
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count
        
        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        pages = range( startpage, endpage+1 )
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
        
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        sort = request.GET.get("sort", "")
        if sort == 'minprice' :
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand="무지")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'maxprice':
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand="무지")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'name':
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand="무지")[start:end] # dtos 이거 리스트임
            
        else :
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand="무지")[start:end] # dtos 이거 리스트임
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
         
        context = {
            "slr":slr,
            "sort":sort,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
            }
        if memid :
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :
            pass
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass    

# 무지 상세
class Mujic(View):
    def get (self,request):
        memid = request.session.get( "memid" )
        prodbrand= request.GET['prodbrand']
        proditems= request.GET['proditems']
        
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
            
        count = Shopproduct.objects.filter( prodbrand="무지",proditems=proditems).count()
        
        template=loader.get_template("mujic.html")
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count
        dtos=Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] 
        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        
        pages = range( startpage, endpage+1 )
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        sort = request.GET.get("sort", "")
        if sort == 'minprice' :
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'maxprice':
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'name':
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        else :
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
            
        if memid:
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :    
            pass
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
            
        context={
            "slr":slr,
            "sort":sort,
            "prodbrand":prodbrand,
            "proditems":proditems,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
        }
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass   
  
# 나이키
class Nikepage(View):
    def get(self,request):
        template = loader.get_template("nike.html")
        memid = request.session.get( "memid" )
        prodbrand = request.GET.get("prodbrand")
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        
        # 규호의 장난질 ( 페이지 관련 )
        count = Shopproduct.objects.filter(prodbrand="나이키").count()
        
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count
        
        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        pages = range( startpage, endpage+1 )
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
        
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        sort = request.GET.get("sort", "")
        if sort == 'minprice' :
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand="나이키")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'maxprice':
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand="나이키")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'name':
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand="나이키")[start:end] # dtos 이거 리스트임
            
        else :
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand="나이키")[start:end] # dtos 이거 리스트임
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
            
        context = {
            "slr":slr,
            "sort":sort,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
            }
        if memid :
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :
            pass
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass

# 나이키 상세 
class Nikec(View):
    def get (self,request):
        memid = request.session.get( "memid" )
        prodbrand= request.GET['prodbrand']
        proditems= request.GET['proditems']
        
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
            
        count = Shopproduct.objects.filter( prodbrand="나이키",proditems=proditems).count()
        
        template=loader.get_template("nikec.html")
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count
        dtos=Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] 
        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        pages = range( startpage, endpage+1 )
        
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        sort = request.GET.get("sort", "")
        if sort == 'minprice' :
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'maxprice':
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'name':
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        else :
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
            
        if memid:
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :    
            pass
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
            
        context={
            "slr":slr,
            "sort":sort,
            "prodbrand":prodbrand,
            "proditems":proditems,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
        }
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass 
        
# 아디다스
class Adpage(View):
    def get(self,request):
        template = loader.get_template("adidaspage.html")
        memid = request.session.get( "memid" )
        prodbrand = request.GET.get("prodbrand")
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        
        # 규호의 장난질 ( 페이지 관련 )
        count = Shopproduct.objects.filter(prodbrand="아디다스").count()
        
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count
        
        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        pages = range( startpage, endpage+1 )
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
        
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        sort = request.GET.get("sort", "")
        if sort == 'minprice' :
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand="아디다스")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'maxprice':
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand="아디다스")[start:end] # dtos 이거 리스트임
            
        
        elif sort == 'name':
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand="아디다스")[start:end] # dtos 이거 리스트임
            
        else :
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand="아디다스")[start:end] # dtos 이거 리스트임
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
            
        context = {
            "slr":slr,
            "sort":sort,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
            }
        if memid :
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :
            pass
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass    

# 아디다스 상세
class Adc(View):
    def get (self,request):
        memid = request.session.get( "memid" )
        prodbrand= request.GET['prodbrand']
        proditems= request.GET['proditems']
        
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
            
        count = Shopproduct.objects.filter( prodbrand="아디다스",proditems=proditems).count()
        
        template=loader.get_template("adidasc.html")
        pagenum = request.GET.get( "pagenum" )
        if not pagenum :
            pagenum = "1"
        pagenum = int( pagenum )
        
        start = ( pagenum - 1 ) * int(PAGE_SIZE)            
        end = start + int(PAGE_SIZE)                   
        if end > count :
            end = count
        dtos=Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] 
        number = count - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * PAGE_BLOCK + 1      
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK)
        endpage = startpage + int(PAGE_BLOCK) - 1                   
        pagecount = count // int(PAGE_SIZE)
        if count % int(PAGE_SIZE) > 0 :
            pagecount += 1
        if endpage > pagecount :
            endpage = pagecount
        pages = range( startpage, endpage+1 )
        
        if memid:
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :    
            pass
        
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        sort = request.GET.get("sort", "")
        if sort == 'minprice' :
            dtos = Shopproduct.objects.order_by("prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'maxprice':
            dtos = Shopproduct.objects.order_by("-prodprice").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        
        elif sort == 'name':
            dtos = Shopproduct.objects.order_by("prodname").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        else :
            dtos = Shopproduct.objects.order_by("-prodnum").filter(prodbrand=prodbrand).filter(proditems=proditems)[start:end] # dtos 이거 리스트임
        
        # 실시간 검색어
        import pandas as pd
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
            
        context={
            "slr":slr,
            "sort":sort,
            "prodbrand":prodbrand,
            "proditems":proditems,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "number" : number,
            "pages" : pages,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "recentProducts":recentProducts,
        }
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass