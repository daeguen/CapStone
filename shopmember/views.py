from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.template import loader
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from shopmember.models import Shopmember, Shopmemberdelete, Shoprecome
from django.core.exceptions import ObjectDoesNotExist
from shopcart.models import Shopcart
from shoppay.models import Shoppaydetail
import urllib.request as req
import urllib.parse as pa
from bs4 import BeautifulSoup as bs
import numpy as np
import pandas as pd
import logging
from django.utils.dateformat import DateFormat
from datetime import datetime, timedelta
from shopreview.models import Shopreview
from shopproduct.models import Shopproduct
import random
import requests

logger = logging.getLogger('shopmember')
# Create your views here.

# 메인페이지
class Index(View):
    def get(self,request):
        memid = request.session.get( "memid" )
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        
        # 추천상품 (무작위)
        if memid : 
            rememberlog = open("log/shopproduct.log", 'r', encoding="utf-8")
            lines = rememberlog.readlines()[::-1]
            remembers=[]
            for line in reversed(lines):
                logs = line.split(":")
                user_id = logs[4].split(" ")[0]
                if user_id != memid:
                    continue
                else :
                    remembers.append(user_id)
                proditems=logs[9].split(" ")[0]
                if proditems not in remembers:
                    remembers.append(proditems)
                
                
                
            if memid not in remembers:
                items = list(Shopproduct.objects.all())
                random_id = random.sample(items, 10)
            else :
                items = list(Shopproduct.objects.filter(proditems=proditems))
            random_id = random.sample(items, 10)
            rememberlog.close()
        else :
            items = list(Shopproduct.objects.all())
            random_id = random.sample(items, 10)
        
        # 최근 본 상품
        productlog = open("log/shopproduct.log", 'r', encoding="utf-8")
        lines = productlog.readlines()[::-1]
        recents = []
        count = 0
        today = datetime.today()

        for line in lines:
            if count >= 4:
                break
            else:
                logs = line.split(" ")
                if datetime.strptime(logs[0][1:], "%Y-%m-%d") < today - timedelta(days=7):
                    break
                user_id = logs[5].split(":")[1]
                if user_id != memid:
                    continue
                prodnum = logs[6].split(":")[1]
                if prodnum not in recents:
                    recents.append(prodnum)
                    count += 1
        recentProducts = [Shopproduct.objects.get(prodnum=recent) for recent in recents]
        productlog.close()
        
        # rss
        url = "http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp"
        values ={
            "stnId":109
            }
        params = pa.urlencode(values)
        url = url+"?"+params
        data = req.urlopen(url).read().decode("utf-8")
        
        # txt 파일 생성 저장
        with open("whether.txt", "w", encoding="utf-8") as f:
            f.write(data)
        
        readings= open("whether.txt","r",encoding="utf-8")
        
        lines = readings.readlines()[38]
        
        #기상예보 정규화
        relines= lines
        relines1= relines.strip()
        relines2= relines1.lstrip('<wf><![CDATA[○')
        relines3 = relines2.replace("○ " ,"")
        relines4 = relines3.replace("<br />○" ,"")
        relines5 = relines4.replace("<br />" ,"")
        relines6 = relines5.replace("<br /><br />*","")
        relines7 = relines6.rstrip("]]></wf>")
        relines8 = relines7.replace("   ","")
        relines9 = relines8.split(" (")
        relines10 = relines9[1]
        
        # ( 아웃터 )추천상품 (브랜드 무작위)
        # items = list(Shopproduct.objects.all().filter(proditems="아우터").filter(proditems="긴바지").filter(proditems="긴팔티"))
        items = list(Shopproduct.objects.raw("""
        select * from shopproduct_shopproduct 
        where proditems = '아우터' or proditems='긴바지' or proditems='긴팔티' or proditems='치마' or proditems='한벌옷' or proditems='신발'
        """))
        random_prod = np.random.choice(items, 10, replace=False)
        
        # sitems = list(Shopproduct.objects.all().filter(proditems="반팔티"))
        sitems = list(Shopproduct.objects.raw("""
        select * from shopproduct_shopproduct 
        where proditems = '반바지' or proditems='반팔티' or proditems='치마' or proditems='신발'
        """))
        srandom_prod = np.random.choice(sitems, 10,replace=False)
        
        # 많이산 상품
        # 구매 db에서 상품 번호들을 쿼리문 sum(prodcount)을 통해 합침
        # 가장 큰 숫자순으로 정렬 후 10개까지 표출
        countmax = Shopproduct.objects.raw("""
        select o.paydetailnum, o.prodnum, o.prodname, o.prodprice, sum(o.prodcount), o.prodmainimg, p.prodbrand, p.proditems
        from shoppay_shoppaydetail o inner join shopproduct_shopproduct p on(p.prodnum = o.prodnum)
        group by o.prodnum
        order by sum(prodcount) DESC LIMIT 10
        """)
        
        source = requests.get('https://www.weather.go.kr/weather/observation/currentweather.jsp')
        soup1 =bs(source.content,"html.parser")
        
        table = soup1.find('table',{'id':'weather_table'})
        data=[]
        
        for tr in table.find_all('tr') :
            tds=list(tr.find_all('td'))
            for td in tds:
                if td.find('a'):
                    point = td.find('a').get_text()
                    temp = tds[5].get_text()
                    humidity = tds[10].get_text()
                    data.append([point,temp,humidity])
                    
        
        with open('gweather.csv','w',encoding="utf-8") as f:
            f.write('지역,온도,습도\n')
            for i in data :
                f.write('{0},{1},{2}\n'.format(i[0],i[1],i[2]))
        
        df =pd.read_csv('gweather.csv', sep=",", encoding='utf-8')
        df.head()
        gion = df['온도']
        maxgion = max(gion) # 전국 최대온도
        # mingion = min(gion) # 전국 최저온도
        # meangion = round(np.mean(gion))
        
        
        # 실시간 검색어
        searchrank = pd.read_csv("search.csv", encoding='utf-8') # 저장한 csv 읽기
        searchrank.rename(columns={'하이힐':'title'}, inplace=True) # 칼럼이 '하이힐'로 먹음 변환해준것
        sl = searchrank.groupby('title')['title'].count().reset_index(name='count') # 그룹으로 묶은것들의 갯수를 샌다음 count라는 칼럼명을 지정해줌
        slh = sl.sort_values(by='count', ascending=False).head(10) # 위부터 10개만 뽑음
        slr = slh.reset_index(drop=True) # 기존의 index 테이블 삭제   
        
        # 장바구니
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
         
        
        
        from sklearn.metrics.pairwise import cosine_similarity
        
        if memid :
            prodlog = open("log/shopreview.log", "r", encoding= "utf-8")
            prods = prodlog.readlines()
            data=[]
            for p in prods:
                logs = p.split(" ")
                user_id = logs[5].split(":")[1]
                prodnum = logs[6].split(":")[1]
                reviewrating = logs[8].split(":")[1]
                data.append([user_id,prodnum,reviewrating])
                
            with open("recomprod.csv","w",encoding="utf-8") as f:    
                f.write("user_id,prodnum,reviewrating\n")
                for i in data:
                    f.write("{0},{1},{2}\n".format(i[0],i[1],i[2]))
                    
            
            
            df = pd.read_csv("recomprod.csv", sep=",", encoding='utf-8')       
            df.head()
            # print()
            raticngs_matrix = df.pivot_table("reviewrating","user_id","prodnum")
            raticngs_matrix.fillna(0,inplace=True)
            
            raticngs_matrix_T= raticngs_matrix.T
            raticngs_matrix_T.head(3)
            
            # print(raticngs_matrix_T) #반전
            item_sim= cosine_similarity(raticngs_matrix_T,raticngs_matrix_T)
            
            item_sim_df= pd.DataFrame(item_sim, index=raticngs_matrix_T.index,columns=raticngs_matrix_T.index)
            # print(item_sim)#유사도
            # print()
            # print("유사도 데이터 프레임화\n",item_sim_df)#유사도 데이터프레임화
            
            rerere=item_sim_df[412].sort_values(ascending=False)[1:11]
            # print()
            # print("412번의 유사도 상품\n",rerere)
            # print(rerere.index[0])
            
            
            
            #영화추천( 최근접 이웃 협업 필터링)
            #함수
            def predict_rating(ratings_arr, item_sim_arr):
                # ratings_arr: u x i, item_sim_arr: i x i
                sum_sr = ratings_arr @ item_sim_arr
                sum_s_abs = np.array([np.abs(item_sim_arr).sum(axis=1)])
                ratings_pred =  sum_sr / sum_s_abs
                return ratings_pred
            
            ratings_pred = predict_rating(raticngs_matrix.values , item_sim_df.values)
            
            ratings_pred_matrix = pd.DataFrame(data=ratings_pred, index= raticngs_matrix.index,
                                               columns = raticngs_matrix.columns)
            ratings_pred_matrix.head(3)
            # print()
            # print(ratings_pred_matrix)
            
            # print("-" *70 ,"\n")
            # 별점이 있는 실제 영화만 추출(별점 없는건 빼고한다)
            #(하지만 지금 별점 데이터만 가지고 생성을 해서 이걸하는 의미가 없다 ) )
            from sklearn.metrics import mean_squared_error
            # 성능평가하는 MSE를 사용
            def get_mse(pred, actual):
                # 평점이 있는 실제 영화만 추출 (1차원 배열로 변환)
                pred = pred[actual.nonzero()].flatten()
                actual = actual[actual.nonzero()].flatten()
                
                return mean_squared_error(pred, actual)
            
            MSE1 = get_mse(ratings_pred, raticngs_matrix.values)
            #평균제곱오차 *값이 0에 가까울수록 ㅊ추측한 값이 원본에 가깝기 때문에 0에 가까울수면 정확도가 올라간다.
            # print(f'아이템 기반 모든 인접 이웃 MSE: {MSE1:.4f}')
            
            # print("-"*80,"\n")
            
            def predict_rating_topsim(ratings_arr, item_sim_arr, N=20):
                # 사용자 - 아이템 별점 행렬 크기만큼 0으로 채운 예측 행렬 초기화
                pred = np.zeros(ratings_arr.shape)
                
                # 사용자 - 아이템 별점 행렬의 열 크기(아이템 갯수) 만큼 반복 (row: 사용자, col:아이템 )
                for col in range(ratings_arr.shape[1]):
                    
                    # 특정 아이템의 유사도 행렬 오르차순 정렬시에 index ..(1)
                    temp = np.argsort(item_sim_arr[:, col])
                    
                    # (1)의 index를 역순으로 나열시 상위 N개의 index = 특정 아이템의 유사도 상위 N개 아이템 index.. (2)
                    top_n_items = [ temp[:-1-N:-1] ]
                    
                    # 개인화 된 예측 별점을 계산: 반복당 특정 아이템의 예측 평점(사용자 전체)
                    for row in range(ratings_arr.shape[0]):
                        # (2)의 유사도 행렬
                        item_sim_arr_topN=item_sim_arr[col, :][top_n_items].T # N x 1
                        # (2)의 실제 별점 행렬
                        ratings_arr_topN =ratings_arr[row, :][top_n_items]
                        
                        # 예측 평점
                        pred[row, col] = ratings_arr_topN @ item_sim_arr_topN
                        pred[row, col] /= np.sum( np.abs(item_sim_arr_topN) )
                
                return pred        
            
            # 사용자별 예측 별점
            ratings_pred = predict_rating_topsim(raticngs_matrix.values, item_sim_df.values, N=20)
            
            #성능평가
            MSE2 = get_mse(ratings_pred, raticngs_matrix.values)
            # print(f'아이템 기반 인텀 TOP-20 이웃 MSE: {MSE2:.4f}')
            # print()
            
            # 예측 별점 데이터 프레임( 즉 사용자별 예측 별점(ratings_pred를 데이터 프레임화 시키는 코드임.)) 
            ratings_pred_matrix= pd.DataFrame(data= ratings_pred, index=raticngs_matrix.index,
                                              columns = raticngs_matrix.columns)
            # print(ratings_pred_matrix)
            # print()
            
            #특정 id가 높은 평점을 준 상품( 실제 별점 )
            tid=memid # get.세션(memid) 해줘도 될듯?
            user_rating_id = raticngs_matrix.loc[tid, :]
            top_user_rating_id=user_rating_id[ user_rating_id > 0 ].sort_values(ascending=False)[:10]
            # print("id: {0}가 높은 별점을 준 상품\n{1}".format(tid,top_user_rating_id))
            # for topdata in top_user_rating_id:
            #     print(topdata)
            
            
            # 특정 id가 아직 별점을 주지 않은 상품추천 (특정 id가 아직 안본 상품의 추천)
            def get_unseen_prod(raticngs_matrix, userId):
                
                # user_rating: userId의 아이템 평점 정보 ( 시리즈 형태: prod번호를 index로 가진다.)
                user_rating = raticngs_matrix.loc[userId,:]
                
                # user_rating = 0인 아직 안본 상품
                unseen_prod_list = user_rating[ user_rating == 0].index.tolist()
                
                # 모든 상품번호를 list객체로 변환
                prod_list = raticngs_matrix.columns.tolist()
                
                # 한줄 for + if문으로 안본 영화 리스트 생성
                unseen_list= [ prod for prod in prod_list if prod in unseen_prod_list ]
                
                return unseen_list
                
            # 보지 않은 영화 중에 예측 높은 순서로 시리즈 반환
            def recomm_prod_by_userid(pred_df, userId, unseen_list, top_n=10):
                recomm_prod = pred_df.loc[userId, unseen_list].sort_values(ascending=False)[:top_n]
                
                return recomm_prod
            
            ######
            # 아직 보지 않은 상품 리스트
            target_id= memid # 나중에 유저 아이디로,,?
            unseen_list = get_unseen_prod(raticngs_matrix, target_id) # 0~9 총10개 뽑아라
            
            # 아이템 기반의 최근접 이웃 협업 필터링으로 상품 추천
            recomm_prods= recomm_prod_by_userid(ratings_pred_matrix, target_id, unseen_list, top_n=10)
                                                # 예측 별점 데이터 프레임    id        안본 리스트    가장위10개
            
            # 데이터 프레임 생성
            df_recomm_prods =pd.DataFrame(data=recomm_prods.values, index=recomm_prods.index, columns=["pred_score"])
            
            # print()
            # print(recomm_prods*100)
            # print("\n 아이템기반의 최근접 이웃 협업 필터링으로 만든 상품추천\n",df_recomm_prods)
            
            # print()
            chl = df_recomm_prods.index
            padlist = Shoprecome.objects.all() # 추천상품 리스트
            padlist.delete() # 새로고침 마다 삭제하고 다시 넣음
            for ii in chl:
                pdlist = Shopproduct.objects.get(prodnum=ii)
                pddto = Shoprecome(
                    prodnum = pdlist
                    )
                pddto.save()
                
            recomelist = Shoprecome.objects.all()
            context = {
            "recomelist":recomelist,
            "maxgion":maxgion,
            "slr":slr,
            "countmax":countmax,
            "gion":gion,
            "random_prod":random_prod,
            "relines10":relines10,
            "srandom_prod":srandom_prod,
            "random_id" : random_id,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "recentProducts" : recentProducts,
            }
            template = loader.get_template( "index.html" )
            return HttpResponse(template.render(context,request))
    
        else :
            items = list(Shopproduct.objects.all())
            randum_id = random.sample(items, 10)

        context = {
            "randum_id":randum_id,
            "maxgion":maxgion,
            "slr":slr,
            "countmax":countmax,
            "gion":gion,
            "random_prod":random_prod,
            "relines10":relines10,
            "srandom_prod":srandom_prod,
            "random_id" : random_id,
            "memid" : memid,
            "cartlist":cartlist,
            "totalprice":totalprice,
            "cartcount" : cartcount,
            "recentProducts" : recentProducts,
            }
        template = loader.get_template( "index.html" )
        if memid :
            logger = logging.getLogger('shoppagemove')
            logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        else :
            pass
        return HttpResponse(template.render(context,request))
    def post(self,request):
        pass

# 가입
class MemberSignup(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super( MemberSignup, self ).dispatch( request, *args, **kwargs )

    def get(self,request):
        template = loader.get_template("signup.html")
        context={}
        return HttpResponse(template.render(context,request))
    
    def post(self,request): 
        user_tel=""
        user_tel1 = request.POST["user_tel1"]
        user_tel2 = request.POST["user_tel2"]
        user_tel3 = request.POST["user_tel3"]
        if user_tel1 and user_tel2 and user_tel3 :
            user_tel = user_tel1 + "-" + user_tel2 + "-" + user_tel3
            
        user_email = ""
        user_email1 = request.POST["user_email1"]
        user_email2 = request.POST["user_email2"]
        if user_email1 and user_email2 :
            user_email = user_email1 + "@" + user_email2
        
        user_id=request.POST["user_id"] # 로그에 저장용
        dto = Shopmember(
            user_id = request.POST["user_id"],
            user_passwd = request.POST["user_passwd"],
            user_name = request.POST["user_name"],
            user_tel = user_tel,
            user_email = user_email,
            user_addr = request.POST["user_addr"],
            user_addrt = request.POST["user_addrt"],
            user_gender = request.POST["user_gender"],
            user_brand = request.POST.getlist('user_brand[]')
            )
        dto.save() # 회원가입 성공
        logger = logging.getLogger('shopmember')
        logger.info("signup_user" + " " + "user_id:" + user_id + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") ) # 회원가입 로그
        logger = logging.getLogger('shopreview')
        logger.info("reviewsuccess" + " " + "user_id:" + user_id + " " + "prodnum:" + "1" + " " + "reviewnum:" + "asd" + " " + "reviewrating:" + "5" + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return redirect("member:login")

# 중복확인 / Ajax 이용
class MemberConfirm(View):
    def get(self,request):
        user_id = request.GET["user_id"]
        result = 0
        try :
            Shopmember.objects.get(user_id=user_id) # db확인
            result = 1 # 있으면 1 
        except ObjectDoesNotExist :
            result = 0 # 없으면 0
        context = {
            "result" : result,
            "user_id" : user_id,
            }
        logger.info("user_idcheck" + " " + "user_id:" + user_id + " " + "date : " + DateFormat(datetime.now()).format("Y-m-d H:i:s") ) # 중복확인로그
        template = loader.get_template("confirm.html")
        return HttpResponse(template.render(context,request))
    def post(self,request):
        pass
    
# 로그인
class MemberLogin(View):
    @method_decorator( csrf_exempt )
    def dispatch( self, request, *args, **kwargs ) :
        return super( MemberLogin, self ).dispatch( request, *args, **kwargs )
    
    def get(self,request):
        template = loader.get_template("login.html")
        context={}
        return HttpResponse(template.render(context,request))
    
    def post(self,request): 
        user_id = request.POST["user_id"]
        user_passwd = request.POST["user_passwd"]
        try :
            dto = Shopmember.objects.get(user_id=user_id) # member DB에서 아이디 를 체크함
            if user_passwd == dto.user_passwd :  # 입력한 passwd와 db의 passwd 가 같으면 성ㄱ공
                request.session["memid"] = user_id
                logger.info("login" + " " + "user_id:" + user_id + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") ) # 로그인 로그
                return redirect( "member:index" )
            else : # 비밀번호 불일치
                message = "입력하신 비밀번호가 일치하지 않습니다"
                logger.info("passwderror" + " " + "user_id:" + user_id + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        except ObjectDoesNotExist : # 아이디가 db에 없음
            message = "입력하신 아이디가 없습니다."
            logger.info("iderror" + " " + "user_id:" + user_id + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        template = loader.get_template( "login.html" )
        context = {
            "message" : message,
            }   
        return HttpResponse( template.render( context, request ) )
    

# 로그아웃
class MemberLogout(View):
    def get(self,request):
        memid = request.session["memid"] # 로그 저장용
        logger.info("logout" + " " + "user_id:" + memid + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") ) # 로그아웃 로그
        del(request.session["memid"]) # 세션을 지워줌
        return redirect("member:index")
    
    def post(self,request):
        pass
    
# 탈퇴
class MemberDelete(View):
    @method_decorator( csrf_exempt )
    def dispatch( self, request, *args, **kwargs ) :
        return super( MemberDelete, self ).dispatch( request, *args, **kwargs )
    
    def get(self,request):
        template=loader.get_template("delete.html")
        user_id = request.session.get("memid")
        context = {}
        logger.info("deletecheck" + " " + "user_id:" + user_id + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s"))
        return HttpResponse(template.render(context,request))
    
    def post(self,request):
        user_id = request.session.get("memid")
        user_passwd = request.POST["user_passwd"]
        dto = Shopmember.objects.get(user_id=user_id)
        if user_passwd == dto.user_passwd : # 비밀번호를 확인함
            deletedto = Shopmemberdelete(
                user_id = dto.user_id,
                user_passwd = dto.user_passwd,
                user_name = dto.user_name,
                user_email = dto.user_email,
                user_tel = dto.user_tel,
                user_addr = dto.user_addr,
                user_addrt = dto.user_addrt,
                user_gender = dto.user_gender,
                user_brand = dto.user_brand,
            )
            deletedto.save() # 탈퇴회원이 저장되는 db에 저장
            logger.info("delete" + " " + "user_id:" + user_id + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") ) # 탈퇴 로그
            dto.delete() # 그 후 기존 db테이블을 지움
            del(request.session["memid"])
            return redirect("member:index")
        else : # 비밀번호 불일치시 다시 원래 페이지로 돌림
            template = loader.get_template("delete.html")
            context = {
                "message" : "비밀번호가 일치하지 않습니다."
                }
            logger.info("deletepasswderror" + " " + "user_id:" + user_id + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") ) # 탈퇴 로그
            return HttpResponse(template.render(context,request))

# 수정 비밀번호 확인
class MemberModify(View):
    @method_decorator( csrf_exempt )
    def dispatch( self, request, *args, **kwargs ) :
        return super( MemberModify, self ).dispatch( request, *args, **kwargs )
    
    def get(self,request):
        template = loader.get_template("modify.html")
        user_id = request.session.get("memid")
        context = {}
        logger.info("modifycheck" + " " + "user_id:" + user_id + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context,request))
    
    def post(self,request):
        user_id = request.session.get("memid")
        user_passwd = request.POST["user_passwd"]
        dto = Shopmember.objects.get(user_id=user_id)
        if user_passwd == dto.user_passwd: # 비밀번호 체크페이지
            template = loader.get_template("modifypro.html")
            
            if dto.user_tel and dto.user_email :
                t = dto.user_tel.split("-") # 붙어있는 것을 - 로 쪼갬
                e = dto.user_email.split("@") # 붙어있는 것을 @ 로 쪼갬
                context = {
                    "dto" : dto,
                    "t" : t,
                    "e":e,
                    }
            logger.info("modifychecksucces" + " " + "user_id:" + user_id + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") ) # 수정확인 로그
        else : # 비밀번호 불일치
            template = loader.get_template("modify.html")
            logger.info("passwderror" + " " + "user_id:" + user_id + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
            context={
                "message" : "비밀번호가 일치하지 않습니다."
                }
        return HttpResponse(template.render(context, request))

# 수정 실행     
class MemberModifypro(View):
    @method_decorator( csrf_exempt )
    def dispatch( self, request, *args, **kwargs ) :
        return super( MemberModifypro, self ).dispatch( request, *args, **kwargs )
    
    def get(self,request):
        pass
    
    def post(self,request):
        user_id = request.session.get("memid")
        dto = Shopmember.objects.get(user_id=user_id)
        dto.user_passwd = request.POST["user_passwd"]
        user_tel1 = request.POST["user_tel1"]
        user_tel2 = request.POST["user_tel2"]
        user_tel3 = request.POST["user_tel3"]
        if user_tel1 and user_tel2 and user_tel3:
            user_tel = user_tel1 + "-" + user_tel2 + "-" + user_tel3
        
        user_email = ""
        user_email1 = request.POST["user_email1"]
        user_email2 = request.POST["user_email2"]
        if user_email1 and user_email2 :
            user_email = user_email1 + "@" + user_email2
        
        dto.user_tel = user_tel
        dto.user_email = user_email
        dto.user_addr = request.POST["user_addr"]
        dto.user_addrt = request.POST["user_addrt"]
        dto.user_brand = request.POST.getlist('user_brand[]')
        dto.save() # 정보들을 다시 받아와 덮어씀
        logger.info("modifysuccess" + " " + "user_id:" + user_id + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") ) # 수정 로그
        return redirect("member:index")
    
    
# 마이페이지
class Membermypage(View):
    def get(self,request):
        template = loader.get_template("mypage.html")
        memid = request.session.get( "memid" )
        
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        paylist = Shoppaydetail.objects.all().filter(user_id=memid).order_by("-paydetailnum") # 내가 구매한 품목들을 뽑아서 정렬함
        paycount = Shoppaydetail.objects.all().filter(user_id=memid).count() # 구매 갯수
        reviewcount = Shopreview.objects.all().filter(user_id=memid).count() # 내가 작성한 리뷰 갯수
        # reviewcheck = Shopreview.objects.all().filter(prodnum=prodnum).filter(user_id=memid)
        
        cartlist = Shopcart.objects.filter(user_id=memid)
        
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
            
        memberdto = Shopmember.objects.get(user_id=memid)
        
        # 실시간 검색어
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
            "cartcount" : cartcount,
            "memberdto":memberdto,
            "paylist":paylist,
            "paycount":paycount,
            "reviewcount":reviewcount,
            }
        logger = logging.getLogger('shoppagemove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context, request))
    def post(self,request):
        pass    

# 내가 작성한 리뷰
class Myreview(View):
    def get(self,request):
        template = loader.get_template("myreview.html")
        memid = request.session.get( "memid" )
        
        dtos = Shopreview.objects.raw("""
            select a.reviewnum, a.prodnum, a.user_id, a.reviewtitle, a.reviewrating, a.reviewcontent, a.reviewimg, a.reviewregdate,
            b.prodname, b.prodmainimg, b.prodoption
            from Shopreview_Shopreview a inner join Shoppay_Shoppaydetail b on (a.prodnum = b.prodnum)
            where a.user_id = %s
            group by reviewnum
            order by a.reviewnum desc
        """,(memid,)) # 내가 작성한 리뷰
        
        dtocount = Shopreview.objects.filter(user_id=memid).count() # 리뷰 갯수
        
        # 로그인시 보이는 장바구니 호버
        cartcount = Shopcart.objects.all().filter(user_id=memid).count()
        cartlist = Shopcart.objects.filter(user_id=memid)
        totalprice = 0
        for pricesum in cartlist:
            totalprice += pricesum.prodnum.prodprice * pricesum.prodcount
        
        # 실시간 검색어
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
        logger = logging.getLogger('shopmove')
        logger.info("move" + " " + "user_id:" + memid + " " + "page:" + request.path  + " " + "date:" + DateFormat(datetime.now()).format("Y-m-d H:i:s") )
        return HttpResponse(template.render(context,request))
    
    def post(self,request):
        pass
    
# 팝업인데 이거 안먹힘
class Fitpapup(View):
    def get(self,request):
        context = {}
        template = loader.get_template("fitpap.html")
        return HttpResponse(template.render(context,request))
    def post(self,request):
        pass