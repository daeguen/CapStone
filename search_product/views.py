from django.shortcuts import render
from shopproduct.models import Shopproduct
from django.db.models import Q
import logging
from django.utils.dateformat import DateFormat
from datetime import datetime, timedelta
from shopcart.models import Shopcart
import numpy as np
import pandas as pd
import csv

logger = logging.getLogger('search_product')
# Create your views here.
def searchResult(request):
    memid = request.session.get( "memid" )
    if 'product' in request.GET:
        query = request.GET.get('product')
        products = Shopproduct.objects.order_by("-prodnum").filter(Q(prodname__contains=query) | 
                                                                   Q(prodbrand__contains=query)|
                                                                   Q(proditems__contains=query))
        
        productcount = Shopproduct.objects.order_by("-prodnum").filter(Q(prodname__contains=query) | 
                                                                   Q(prodbrand__contains=query)|
                                                                   Q(proditems__contains=query)).count()
        
        # 실시간 검색어 로그
        searchlog = open("log/search_product.log", "r", encoding="utf-8") # 로그 읽기
        lines = csv.reader(searchlog)
        count = 0
        f = open("search.csv", "w", encoding="utf-8") # csv에 작성하기
        for line in lines :
            searchlog = line[3].split(",")[0]
            searchtitle = searchlog.split(":")[1]
            f.write(searchtitle)
            f.write("\r") # 줄바꿈
        f.close()
        
        # 실시간 검색어 출력
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제
        
        # 장바구니
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
        
        # 최근 본 상품                                                        
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
        
    if memid :
        logger.info("search" + "," + "user_id:" + memid + "," + "search_title:" + query + "," + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
    else :
        pass
    return render(request, 'search.html', {'slr':slr,
                                           'query':query, 
                                           'products':products, 
                                           'memid':memid,
                                           'productcount':productcount,
                                           'recentProducts':recentProducts,
                                           'cartcount':cartcount,
                                           'cartlist':cartlist,
                                           'totalprice':totalprice,
                                           }
                                        )