from django.urls import path

from . import views

urlpatterns_store = [
    path('goods', views.GoodsView.as_view({'get': 'list'})),
]
