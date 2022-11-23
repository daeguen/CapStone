import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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
tid="ham" # get.세션(memid) 해줘도 될듯?
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
target_id="ham" # 나중에 유저 아이디로,,?
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
chl1= list(chl)
# for ii in chl1:
#     print(ii)

