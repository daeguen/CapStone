"""Fitvely URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from django.conf.urls.static import static
from Fitvely import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("shopmember/", include("shopmember.urls")),
    path("shopnotice/", include("shopnotice.urls")),
    path("shopqna/", include("shopqna.urls")),
    path("shopproduct/", include("shopproduct.urls")),
    path("shopcart/", include("shopcart.urls")),
    path("shopreview/", include("shopreview.urls")),
    path("shoppay/", include(("shoppay.urls","pay"), namespace="pay")),
    path("shopreturn/", include("shopreturn.urls")),
    path('search/', include('search_product.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)