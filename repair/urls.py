from django.conf.urls import url
from . import views
from .views import OrderCreate


app_name = 'repair'

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^myord/$', views.my_order, name="my_order"),
    url(r'^myord/order_add$', OrderCreate.as_view(), name="order_add")
]