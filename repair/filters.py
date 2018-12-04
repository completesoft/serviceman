import django_filters
from .models import DocOrderHeader, CartridgeOrder, CartridgeActionStatus, Clients, MaintenanceOrder, Cartridge
from django.utils.timezone import is_aware, now
from datetime import timedelta
from django.contrib.admin.widgets import AdminDateWidget
from django.forms import HiddenInput, ModelChoiceField, CharField, IntegerField, DateField
from django.forms import Form
from datetime import datetime, timedelta
from django.utils import timezone
from django.forms.widgets import RadioSelect


def clients(request):
    if request.user.groups.filter(name='outsource').exists():
        return Clients.objects.none()
    return Clients.objects.all()


class DocOrderHeaderFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='order_datetime', lookup_expr='date__gte', widget=HiddenInput)
    date_to = django_filters.DateFilter(field_name='order_datetime', lookup_expr='date__lte', widget=HiddenInput)
    client = django_filters.ModelChoiceFilter(field_name='client', queryset=clients, label='Клиент')

    class Meta:
        model = DocOrderHeader
        fields = ['client', 'order_barcode']

    def filter_queryset(self, queryset):
        if self.form.is_valid() and any(self.form.cleaned_data.values()):
            return super(DocOrderHeaderFilter, self).filter_queryset(queryset)
        return queryset.filter(order_datetime__gte=timezone.now()-timedelta(days=7))



class CartridgeOrderFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='order_datetime', lookup_expr='date__gte', widget=HiddenInput)
    date_to = django_filters.DateFilter(field_name='order_datetime', lookup_expr='date__lte', widget=HiddenInput)
    client = django_filters.ModelChoiceFilter(field_name='cartridge__client', queryset=clients, label='Клиент')
    order = django_filters.NumberFilter(field_name='id', label='Номер заказа')

    class Meta:
        model = CartridgeOrder
        exclude = ['defect', 'client_position', 'cartridge', 'order_datetime']

    def filter_queryset(self, queryset):
        if self.form.is_valid() and any(self.form.cleaned_data.values()):
            return super(CartridgeOrderFilter, self).filter_queryset(queryset)
        return queryset.filter(order_datetime__gte=timezone.now()-timedelta(days=7))


class MaintenanceOrderFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='order_datetime', lookup_expr='date__gte', widget=HiddenInput)
    date_to = django_filters.DateFilter(field_name='order_datetime', lookup_expr='date__lte', widget=HiddenInput)
    client = django_filters.ModelChoiceFilter(field_name='client', queryset=clients, label='Клиент')
    order = django_filters.NumberFilter(field_name='id', label='Номер заказа')

    class Meta:
        model = MaintenanceOrder
        fields = ['client']

    def filter_queryset(self, queryset):
        if self.form.is_valid() and any(self.form.cleaned_data.values()):
            return super(MaintenanceOrderFilter, self).filter_queryset(queryset)
        return queryset.filter(order_datetime__gte=timezone.now()-timedelta(days=7))


class QrCartridgesFilter(django_filters.FilterSet):
    sn = django_filters.CharFilter(label='S/N' ,field_name='serial_number', lookup_expr='contains')

    class Meta:
        model = Cartridge
        exclude = ['add_datetime', 'model', 'client', 'client_position', 'serial_number']

    def filter_queryset(self, queryset):
        if any(self.form.cleaned_data.values()):
            return super(QrCartridgesFilter, self).filter_queryset(queryset)
        else:
            return queryset.none()