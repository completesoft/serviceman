import django_filters
from .models import DocOrderHeader, CartridgeOrder, CartridgeActionStatus, Clients, MaintenanceOrder
from django.utils.timezone import is_aware, now
from datetime import timedelta
from django.contrib.admin.widgets import AdminDateWidget
from django.forms import HiddenInput, ModelChoiceField, CharField, IntegerField, DateField
from django.forms import Form


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
        fields = ['client']

    def filter_queryset(self, queryset):
        if self.form.is_valid() and any(self.form.cleaned_data.values()):
            return super(DocOrderHeaderFilter, self).filter_queryset(queryset)
        return queryset.none()


class CartridgeOrderFilter(django_filters.FilterSet):
    order_datetime = django_filters.DateRangeFilter(field_name='order_datetime', label='Период')
    client = django_filters.ModelChoiceFilter(field_name='cartridge__client', queryset=clients, label='Клиент')

    class Meta:
        model = CartridgeOrder
        exclude = ['defect', 'client_position', 'cartridge']

    def filter_queryset(self, queryset):
        if any(self.form.cleaned_data.values()):
            return super(CartridgeOrderFilter, self).filter_queryset(queryset)
        return queryset.none()


class MaintenanceOrderFilter(django_filters.FilterSet):
    order_datetime = django_filters.DateRangeFilter(field_name='order_datetime', label='Период')

    class Meta:
        model = MaintenanceOrder
        fields = ['order_datetime', 'client']

    def filter_queryset(self, queryset):
        if self.form.is_valid() and any(self.form.cleaned_data.values()):
            return super(MaintenanceOrderFilter, self).filter_queryset(queryset)
        return queryset.none()