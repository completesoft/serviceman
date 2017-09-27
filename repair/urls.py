from django.conf.urls import url
from . import views
from .views import OrderCreateView, OrderDetailView, ActionCreateView, ClientListView, ClientCreateView, ClientDetailView, ClientEditView, OrderArchiveView

app_name = 'repair'

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^myord/$', views.my_order, name="my_order"),
    url(r'^myord/order_add$', OrderCreateView.as_view(), name="order_add"),
    url(r'^myord/(?P<order_id>\d+)/$', OrderDetailView.as_view(), name="order_detail"),
    url(r'^myord/(?P<order_id>\d+)/action_add/$', ActionCreateView.as_view(), name="action_add"),
    url(r'^myord/(?P<order_id>\d+)/service_add/$', views.service_add, name="service_add"),
    url(r'^myord/(?P<order_id>\d+)/spares_add/$', views.spares_add, name="spares_add"),
    url(r'^clients/$', ClientListView.as_view(), name="clients"),
    url(r'^clients/clients_add/$', ClientCreateView.as_view(), name="clients_add"),
    url(r'^clients/(?P<client_id>\d+)/$', ClientDetailView.as_view(), name="client_detail"),
    url(r'^clients/(?P<client_id>\d+)/edit$', ClientEditView.as_view(), name="client_edit"),
    url(r'^add/client/?$', views.popupClientView, name="popup_client_add"),
    url(r'^dep-update/(?P<client_id>\d+)/$', views.dep_update, name="dep_update"),
    url(r'^order-archive/$', OrderArchiveView.as_view(), name="order_archive"),
]