from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.template import loader
from django.http.response import HttpResponse
from shopqna.models import Shopqna
from django.utils.dateformat import DateFormat
from datetime import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from shopcart.models import Shopcart
import logging
from shopreview.models import Shopreview

logger = logging.getLogger('shopqnamove')
# Create your views here.

PAGE_SIZE = 10 # 한페이지에 5개의 글
PAGE_BLOCK = 5  # 넘어가는것 3개

# 글 목록
class Qnalist(View):
    def get(self,request):
        template = loader.get_template("qnalist.html")
        memid = request.session.get( "memid" )
        qnacount = Shopqna.objects.all().count()
        
        pagenum = request.GET.get( "pagenum" ) # 페이지num
        if not pagenum :
            pagenum = "1"
        
        pagenum = int( pagenum ) # 페이지num 을 보겠다
        
        # 한 페이지에 몇개씩 표기하겠다를 정해주어야함
        start = ( pagenum - 1) * int(PAGE_SIZE)        # ( 5 - 1 ) * 10      40
        end = start + int(PAGE_SIZE)                # 41 + 10 - 1            50
        if end > qnacount :
            end = qnacount
            
        dtos = Shopqna.objects.order_by("-qnanum")[start:end] # 글 목록 전체를 다 가지고오며, 역순으로 정렬
        number = qnacount - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * int(PAGE_BLOCK) + 1      # 9 // 10 * 10 + 1    1
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK) # 페이지 고정
        endpage = startpage + int(PAGE_BLOCK) - 1                         # 1 + 10 -1           10
        pagecount = qnacount // int(PAGE_SIZE)
        if qnacount % int(PAGE_SIZE) > 0 :
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
            "qnacount" : qnacount,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "cartcount":cartcount,
            "cartlist":cartlist,
            "totalprice":totalprice,
            }
        if memid :
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :
            pass
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass

# 글 작성
class Qnawrite(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Qnawrite, self ).dispatch( request, *args, **kwargs )
    
    def get(self,request):
        template = loader.get_template("qnawrite.html")
        memid = request.session.get( "memid" )
        qnanum = request.GET.get("qnanum")
        
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
            "qnanum" : qnanum,
            "cartcount":cartcount,
            "cartlist":cartlist,
            "totalprice":totalprice,
            }
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context, request)) # 글작성 페이지 이동
    def post(self,request):
        user_id = request.POST["user_id"]
        dto = Shopqna(
            user_id = request.POST["user_id"],
            qnatitle = request.POST["qnatitle"],
            qnacontent = request.POST["qnacontent"],
            qnareadcount = 0,
            qnaregdate = DateFormat(datetime.now()).format("Ymd")
            )
        dto.save() # 입력한 정보를 받아서 db에 저장함
        logger = logging.getLogger('shopqna')
        logger.info("qnasuccess" + " " + "user_id:" + user_id + " " + "qnanum:" + str(dto.qnanum) + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") ) # 회원 qna 글 작성 성공 로그
        return redirect("qnaboard:qnalist")

# 글 보기
class Qnacontent(View):
    def get(self,request):
        qnanum = request.GET["qnanum"]
        pagenum = request.GET["pagenum"]
        number = request.GET["number"]
        memid = request.session.get( "memid" )
        dto = Shopqna.objects.get(qnanum=qnanum) # 해당글번호가 db의 글번호와 맞는 내용을 보여줌
        if dto.user_id != memid :
            dto.qnareadcount += 1
            dto.save() # 그후 아이디가 다른사람이 보았을 경우 readcount를 1 증가시키며 저장함
            
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
            "qnanum" : qnanum,
            "pagenum" : pagenum,
            "number" : number,
            "dto":dto,
            "totalprice":totalprice,
            "cartcount":cartcount,
            "cartlist":cartlist,
            "totalprice":totalprice,
            }
        if memid :
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :
            pass
        template = loader.get_template("qnacontent.html")
        return HttpResponse(template.render(context,request))
    
    def post(self,request):
        pass

# 글 삭제
class Qnadelete(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Qnadelete,self).dispatch(request, *args, **kwargs)
    
    def get(self,request):
        memid = request.session.get( "memid" )
        qnanum = request.GET["qnanum"]
        pagenum = request.GET["pagenum"]
        template = loader.get_template("qnadeletecheck.html") # 글 번호를 받아와 삭제페이지 전송
        context={
            "qnanum" : qnanum,
            "pagenum" : pagenum,
            }
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context,request))
    def post(self,request):
        memid = request.session.get( "memid" )
        qnanum = request.POST["qnanum"]
        pagenum = request.POST["pagenum"]
        dto = Shopqna.objects.get(qnanum=qnanum)
        dto.delete() # 받아온 글번호와 db의 글번호가 일치하는것을 삭제함
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return redirect("qnaboard:qnalist")
        
# 글 수정 확인
class Qnamodify(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Qnamodify,self).dispatch(request, *args, **kwargs)
    
    def get(self,request):
        memid = request.session.get( "memid" )
        qnanum = request.GET["qnanum"]
        pagenum = request.GET["pagenum"]
        
        context={
            "qnanum" : qnanum,
            "pagenum" : pagenum,
            }
        template = loader.get_template("qnamodifycheck.html")
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        
        return HttpResponse(template.render(context,request))
    
    def post(self,request):
        qnanum = request.POST["qnanum"]
        pagenum = request.POST["pagenum"]
        memid = request.session.get( "memid" )
        dto = Shopqna.objects.get(qnanum = qnanum) # 받아온 번호와 db가 일치하는 번호의 글을 수정페이지로 불러옴
        template = loader.get_template("qnamodifypro.html")
        
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
            "qnanum" : qnanum,
            "pagenum" : pagenum,
            "dto" : dto,
            "cartcount":cartcount,
            "cartlist":cartlist,
            "totalprice":totalprice,
            }
        
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context,request))
    
# 글 수정 하기
class Qnamodifypro(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Qnamodifypro,self).dispatch(request, *args, **kwargs)
    
    def get(self,request):
        pass
        
    def post(self,request):
        memid = request.session.get( "memid" )
        qnanum = request.POST["qnanum"]
        pagenum = request.POST["pagenum"]
        dto = Shopqna.objects.get(qnanum = qnanum)

        dto.qnatitle = request.POST["qnatitle"]
        dto.qnacontent = request.POST["qnacontent"]
        dto.save() # 변경 사항을 저장함
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return redirect("qnaboard:qnalist")

# 내 문의글    
class Myqna(View):
    def get(self,request):
        template = loader.get_template("myqnalist.html")
        memid = request.session.get( "memid" )
        dtos = Shopqna.objects.filter(user_id=memid).order_by("-qnanum") # qnalist 에서 memid와 같은 id를 가진 글을 가져옴
        dtocount = Shopqna.objects.filter(user_id=memid).count()
        
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
            "dtos" : dtos,
            "dtocount" : dtocount,
            "cartcount":cartcount,
            "cartlist":cartlist,
            "totalprice":totalprice,
            }
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context,request))
    
    def post(self,request):
        pass
    
