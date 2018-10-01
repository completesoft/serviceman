from django.conf.urls import url
from . import views
from .views import (OrderCreateView, MyOrderListView, OrderDetailView, ActionCreateView, ClientListView, ClientCreateView,
                    ClientDetailView, ClientEditView, OrderArchiveView, ServiceRewardAssessment, CartridgeOrderListView, CartridgeMyOrderListView,
                    CartridgeListView, CartridgeOrderCreateView, cartridge_update, CartridgeCreateView, CartridgeOrderDetailView,
                    CartridgeActionCreateView, MaintenanceOrderCreateView, MaintenanceOrderListView, MaintenanceOrderDetailView,
                    MaintenanceActionCreateView, CartridgeOrderArchiveView, DocOrderHeaderListView, cartridge_add_spare,
                    cartridge_del_spare, cartridge_add_service, cartridge_del_service)


app_name = 'repair'

urlpatterns = [
    url(r'^$', DocOrderHeaderListView.as_view(), name="index"),
    url(r'^myord/$', MyOrderListView.as_view(), name="order_my"),
    url(r'^myord/order_add/$', OrderCreateView.as_view(), name="order_add"),
    url(r'^myord/(?P<order_id>\d+)/$', OrderDetailView.as_view(), name="order_detail"),
    url(r'^myord/(?P<order_id>\d+)/action_add/$', ActionCreateView.as_view(), name="action_add"),
    url(r'^clients/$', ClientListView.as_view(), name="clients"),
    url(r'^clients/clients_add/$', ClientCreateView.as_view(), name="clients_add"),
    url(r'^clients/(?P<client_id>\d+)/$', ClientDetailView.as_view(), name="client_detail"),
    url(r'^clients/(?P<client_id>\d+)/edit$', ClientEditView.as_view(), name="client_edit"),
    url(r'^add/client/?$', views.popupClientView, name="popup_client_add"),
    url(r'^dep-update/(?P<client_id>\d+)/$', views.dep_update, name="dep_update"),
    url(r'^order-archive/$', OrderArchiveView.as_view(), name="order_archive"),
    url(r'^change-pass/$', views.password_change, {"post_change_redirect": "repair:index", "template_name": "repair/password_change_form.html"}, name="change_pass"),
    url(r'^ajax-add-service/(?P<order_id>\d+)/$', views.ajax_add_service, name="ajax_add_service"),
    url(r'^service/$', views.service, name="service"),
    url(r'^ajax-add-spare/(?P<order_id>\d+)/$', views.ajax_add_spare, name="ajax_add_spare"),
    url(r'^spare/$', views.spare, name="spare"),
    url(r'^assessment/$', ServiceRewardAssessment.as_view(), name="assessment"),
    url(r'^cartord_add/$', CartridgeOrderCreateView.as_view(), name="cartridge_order_add"),
    url(r'^cartord/$', CartridgeOrderListView.as_view(), name="cartridge_orders"),
    url(r'^mycartord/$', CartridgeMyOrderListView.as_view(), name="cartridge_my_orders"),
    url(r'^cartridges/$', CartridgeListView.as_view(), name="cartridges"),
    url(r'^cartridge/(?P<order_id>\d+)/$', CartridgeOrderDetailView.as_view(), name="cartridge_order_detail"),
    url(r'^cartridge/(?P<order_id>\d+)/action_add$', CartridgeActionCreateView.as_view(), name="cartridge_action_add"),
    url(r'^cartridge/create$', CartridgeCreateView.as_view(), name="cartridge_create"),
    url(r'^cartridge_update/$', cartridge_update, name="cartridge_update"),
    url(r'^cartridge-add-spare/(?P<order_id>\d+)/$', cartridge_add_spare, name="cartridge_add_spare"),
    url(r'^cartridge-del-spare/$', cartridge_del_spare, name="cartridge_del_spare"),
    url(r'^cartridge-add-service/(?P<order_id>\d+)/$', cartridge_add_service, name="cartridge_add_service"),
    url(r'^cartridge-del-service/$', cartridge_del_service, name="cartridge_del_service"),
    url(r'^cartridge-order-archive/$', CartridgeOrderArchiveView.as_view(), name="cartridge_order_archive"),
    url(r'^maintenance/order_add$', MaintenanceOrderCreateView.as_view(), name='maintenance_order_add'),
    url(r'^maintenance/order_list$', MaintenanceOrderListView.as_view(), name='maintenance_order_list'),
    url(r'^maintenance/(?P<order_id>\d+)/$', MaintenanceOrderDetailView.as_view(), name="maintenance_detail"),
    url(r'^maintenance/(?P<order_id>\d+)/action_add$', MaintenanceActionCreateView.as_view(), name="maintenance_action_add"),
]