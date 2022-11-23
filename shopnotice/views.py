from django.shortcuts import render
from django.views.generic.base import View
from django.template import loader
from shopnotice.models import Shopnotice
from django.http.response import HttpResponse
from shopcart.models import Shopcart
import logging
from django.utils.dateformat import DateFormat
from datetime import datetime

logger = logging.getLogger('shopnotice')
# Create your views here.
PAGE_SIZE = 10 # 한페이지에 5개의 글
PAGE_BLOCK = 5  # 넘어가는것 3개

# 공지사항 리스트
class Noticelist(View):
    def get(self,request):
        template = loader.get_template("notice.html")
        memid = request.session.get( "memid" )
        noticecount = Shopnotice.objects.all().count() # 글 갯수
        
        pagenum = request.GET.get( "pagenum" ) # 페이지num
        if not pagenum :
            pagenum = "1"
        
        pagenum = int( pagenum ) # 페이지num 을 보겠다
        
        # 한 페이지에 몇개씩 표기하겠다를 정해주어야함
        start = ( pagenum - 1) * int(PAGE_SIZE)        # ( 5 - 1 ) * 10      40
        end = start + int(PAGE_SIZE)                # 41 + 10 - 1            50
        if end > noticecount :
            end = noticecount
            
        dtos = Shopnotice.objects.order_by("-noticenum")[start:end] # 글을 전부 뽑아 온 후 페이징 입힘
        number = noticecount - ( pagenum - 1 ) * int(PAGE_SIZE)
        
        startpage = pagenum // int(PAGE_BLOCK) * int(PAGE_BLOCK) + 1      # 9 // 10 * 10 + 1    1
        if pagenum % int(PAGE_BLOCK) == 0 :
            startpage -= int(PAGE_BLOCK) # 페이지 고정
        endpage = startpage + int(PAGE_BLOCK) - 1                         # 1 + 10 -1           10
        pagecount = noticecount // int(PAGE_SIZE)
        if noticecount % int(PAGE_SIZE) > 0 :
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
            "noticecount" : noticecount,
            "dtos" : dtos,
            "pagenum" : pagenum,
            "number" : number,
            "pages" : pages,
            "startpage" : startpage,
            "endpage" : endpage,
            "pageblock" : PAGE_BLOCK,
            "pagecount" : pagecount,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            }
        if memid :
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :
            pass
        return HttpResponse(template.render(context,request))
    
    def post(self,request):
        pass
    
class Noticedetail(View):
    def get(self,request):
        noticenum = request.GET["noticenum"]
        pagenum = request.GET["pagenum"]
        number = request.GET["number"]
        memid = request.session.get( "memid" )
        dto = Shopnotice.objects.get(noticenum=noticenum) # 내가 누른 글 번호와 db에 저장된 번호가 맞는것을 가져옴
        dto.noticereadcount += 1 # readcount를 +1 시킴
        dto.save() # 그후 저장함
        
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
            "noticenum" : noticenum,
            "pagenum" : pagenum,
            "number" : number,
            "dto":dto,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            }
        template = loader.get_template("noticedetail.html")
        if memid :
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :
            pass
        return HttpResponse(template.render(context,request))
    def post(self,request):
        pass