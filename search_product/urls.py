from django.urls.conf import path
from search_product import views

app_name = 'search_product'

urlpatterns = [
    path('searchReuslt', views.searchResult, name='searchResult'),
]