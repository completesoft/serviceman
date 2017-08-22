from django.conf.urls import url
from . import views
from .views import OrderCreateView, OrderDetailView


app_name = 'repair'

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^myord/$', views.my_order, name="my_order"),
    url(r'^myord/order_add$', OrderCreateView.as_view(), name="order_add"),
    url(r'^myord/(?P<order_id>\d+)/$', OrderDetailView.as_view(), name="order_detail"),
    url(r'^myord/(?P<order_id>\d+)/change/$', views.action_add, name="order_change")
]