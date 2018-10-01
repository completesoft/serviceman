from django import forms
from .models import (DocOrderHeader, DocOrderAction, DocOrderSparesContent, DocOrderServiceContent,
                           DirStatus, Clients, ClientsDep, Reward, Storage, CartridgeOrder, Cartridge, CartridgeAction,
                     CartridgeActionStatus, MaintenanceOrder, MaintenanceAction, MaintenanceActionStatus, CartridgeOrderServiceContent,
                     CartridgeOrderSparesContent)
from django.contrib.auth.models import User, Group
from django.forms import ModelChoiceField, CharField, IntegerField
from django.forms import widgets




class DateRangeWidgetForm(forms.Form):
    period = forms.CharField(label='Период', required=False)


# for user model
class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "{}".format(obj.get_full_name())


class OrderHeaderForm (forms.ModelForm):
    class Meta:
        model = DocOrderHeader
        fields = ["order_barcode", "client", "client_dep", "client_position", "device_name", "device_serial", "device_defect",
                  "order_comment"]

    order_barcode = forms.CharField(max_length=150, label="Штрихкод", widget=forms.TextInput(attrs={'class':'form-control'}), error_messages={'unique': 'Этот штрихкод уже существует'})
    client_position = forms.CharField(max_length=150, label="Размещение у клиента", required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    device_name = forms.CharField(max_length=100, required=True, label="Наименование устройства", widget=forms.TextInput(attrs={'class':'form-control'}))
    device_defect = forms.CharField(max_length=255, required=True, label="Заявленная неисправность", widget=forms.Textarea(attrs={'class':'form-control'}))
    device_serial = forms.CharField(required=True, label="Серийный номер устройства", widget=forms.TextInput(attrs={'class':'form-control'}))
    order_comment = forms.CharField(max_length=255, label="Комментарий", widget=forms.Textarea, required=False)
    client_dep = forms.ModelChoiceField(label="Отделение клиента", queryset=ClientsDep.objects.all(), required=False, widget=forms.Select(attrs={'class':'form-control'}))
    executor = MyModelChoiceField(label="Исполнитель заказа", queryset= User.objects.filter(groups__name="serviceman"), required=True, empty_label="Выберите исполнителя", widget=forms.Select(attrs={'class':'form-control'}))
    client = forms.ModelChoiceField(label="Клиент", queryset=Clients.objects.all(), required=True, widget=forms.Select(attrs={'class':'form-control'}))
    order_comment = forms.CharField(label="Комментарий", required=False, widget=forms.TextInput(attrs={'class':'form-control'}))
    storage = forms.ModelChoiceField(label="Склад", queryset=Storage.objects.all(), required=True, widget=forms.Select(attrs={'class':'form-control'}))

    def clean(self):
        cleaned_data = super(OrderHeaderForm, self).clean()
        client = cleaned_data.get("client")
        client_position = cleaned_data.get("client_position")
        client_dep = cleaned_data.get("client_dep")

        if client.client_corp and not client_dep:
            msg = "У корпоративного клиента не указано отделение"
            self.add_error('client_dep', msg)
        if client.client_corp and not client_position:
            msg = "Обязательно укажите размещение у клиента"
            self.add_error('client_position', msg)




class ActionForm(forms.ModelForm):
    class Meta:
        model = DocOrderAction
        fields = ['manager_user', 'executor_user', 'status', 'storage', 'action_comment']

    status = forms.ModelChoiceField(label="Статус заказа", required=True, queryset=DirStatus.objects.all(), widget=forms.Select(attrs={'class':'form-control'}))
    manager_user = MyModelChoiceField(queryset= User.objects.exclude(groups__name="outsource"), label="Руководитель заказа", required=True, widget=forms.Select(attrs={'class':'form-control'}))
    executor_user = MyModelChoiceField(queryset= User.objects.filter(groups__name="serviceman"), label="Исполнитель заказа", required=True, widget=forms.Select(attrs={'class':'form-control'}))
    storage = forms.ModelChoiceField(label="Склад", queryset=Storage.objects.all(), required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    action_comment = forms.CharField(label="Комментарий", required=False, widget=forms.TextInput(attrs={'class':'form-control'}))


class ActionFormOut(forms.ModelForm):
    class Meta:
        model = DocOrderAction
        fields = ["status", 'storage', "action_comment"]

    status = forms.ModelChoiceField(label="Статус заказа", required=True, queryset=DirStatus.objects.all(), widget=forms.Select(attrs={'class':'form-control'}))
    storage = forms.ModelChoiceField(label="Склад", queryset=Storage.objects.all(), required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    action_comment = forms.CharField(label="Комментарий", required=False, widget=forms.TextInput(attrs={'class':'form-control'}))


class SpareForm(forms.ModelForm):
    class Meta:
        model = DocOrderSparesContent
        fields = ["spare_name", "spare_serial", "spares_qty"]

    spare_name = forms.CharField(required=True, widget=forms.Textarea(attrs={'class':'form-control', 'cols': '30', 'rows': '4'}))
    spare_serial = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    spares_qty = forms.IntegerField(required=True, min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))

class ServiceForm(forms.ModelForm):
    class Meta:
        model = DocOrderServiceContent
        fields = ["service_name", "service_qty", "cost"]

    service_name = forms.CharField(required=True, widget=forms.Textarea(attrs={'class':'form-control', 'cols': '30', 'rows': '4'}))
    service_qty = forms.IntegerField(required=True, min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    cost = forms.IntegerField(required=True, min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))


class ClientForm(forms.ModelForm):
    class Meta:
        model = Clients
        fields = ["client_name", "client_contact", "client_corp"]


class ClientDepForm(forms.ModelForm):
    class Meta:
        model = ClientsDep
        fields = ["client_dep_name"]

class ClientEditForm(forms.ModelForm):
    class Meta:
        model = Clients
        fields = ["client_contact"]


class RewardForm(forms.ModelForm):
    class Meta:
        model = Reward
        fields = ["serviceman", "amount", 'add_datetime']

    serviceman = MyModelChoiceField(queryset= User.objects.filter(groups__name="serviceman"), label="Мастер", required=True, widget=forms.Select(attrs={'class':'form-control'}))
    amount = forms.DecimalField(label="Сумма", max_digits=6, decimal_places=2, required=True)


class CartridgeRegularActionForm(forms.ModelForm):
    class Meta:
        model = CartridgeAction
        fields = ['status', 'action_content']

    status = forms.ModelChoiceField(label="Статус заказа", required=True, queryset=CartridgeActionStatus.objects.exclude(status_name__in=[5, 6]), widget=forms.Select(attrs={'class':'form-control'}))
    action_content = forms.CharField(label="Выполненные работы", required=True, widget=forms.Textarea(attrs={'class': 'form-control'}))


class CartridgeSuperActionForm(CartridgeRegularActionForm):
    class Meta:
        model = CartridgeAction
        fields = ['manager_user', 'executor_user', 'status', 'action_content']

    manager_user = MyModelChoiceField(queryset= User.objects.exclude(groups__name="outsource"),
                                      label="Руководитель заказа", required=True, widget=forms.Select(attrs={'class':'form-control'}))
    executor_user = MyModelChoiceField(queryset= User.objects.filter(groups__name="serviceman"),
                                       label="Исполнитель заказа", required=True, widget=forms.Select(attrs={'class':'form-control'}))
    status = forms.ModelChoiceField(label="Статус заказа", required=True,
                                    queryset=CartridgeActionStatus.objects.all(),
                                    widget=forms.Select(attrs={'class': 'form-control'}))

class CartridgeActionExpressForm(forms.ModelForm):
    class Meta:
        model = CartridgeAction
        fields = ['status']

    status = forms.ModelChoiceField(required=True, queryset=CartridgeActionStatus.objects.all(), empty_label=None, to_field_name='status_name', widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        status_set = kwargs.pop('status_set', None)
        super(CartridgeActionExpressForm, self).__init__(*args, **kwargs)

        if status_set:
            self.fields['status'].queryset = CartridgeActionStatus.objects.filter(status_name__in=status_set)


class CartridgeCreateForm(forms.ModelForm):
    class Meta:
        model = Cartridge
        fields = ['client', 'model', 'serial_number']

    client = forms.ModelChoiceField(label="Клиент", queryset=Clients.objects.all(), required=True,
                                    widget=forms.Select(attrs={'class': 'form-control'}))
    model = forms.CharField(label='Модель', required=True, max_length=100,
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    serial_number = forms.CharField(label='Серийный номер', required=True, max_length=100,
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))


class CartridgeOrderForm (forms.ModelForm):
    class Meta:
        model = CartridgeOrder
        fields = ["cartridge", "defect", "client_position"]

    cartridge = forms.ModelChoiceField(label="Картридж", queryset=Cartridge.objects.all(), required=True, widget=forms.Select(attrs={'class':'form-control'}))
    defect = forms.CharField(max_length=255, required=True, label="Заявленная неисправность", widget=forms.Textarea(attrs={'class':'form-control'}))
    executor = MyModelChoiceField(label="Исполнитель заказа", queryset= User.objects.filter(groups__name="serviceman"), required=True, empty_label="Выберите исполнителя", widget=forms.Select(attrs={'class':'form-control'}))
    client_position = forms.CharField(max_length=150, label="Размещение у клиента", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))


class CartridgeFilterOrderForm (forms.Form):
    class Meta:
        model = Cartridge
        fields = ['serial_number', 'client']

    serial_number = forms.CharField(label='Серийный номер', required=False,  max_length=100,
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    client = forms.ModelChoiceField(label="Клиент", queryset=Clients.objects.all(), required=False,
                                    widget=forms.Select(attrs={'class': 'form-control'}))


class MaintenanceOrderForm(forms.ModelForm):
    class Meta:
        model = MaintenanceOrder
        fields = ['client', 'client_dep', 'client_position', 'list_of_jobs', 'order_comment']

    client = forms.ModelChoiceField(label="Клиент", queryset=Clients.objects.all(), required=True,
                                    widget=forms.Select(attrs={'class': 'form-control'}))
    client_dep = forms.ModelChoiceField(label="Отделение клиента", queryset=ClientsDep.objects.all(), required=False,
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    client_position = forms.CharField(max_length=150, label="Размещение у клиента", required=False,
                                      widget=forms.TextInput(attrs={'class': 'form-control'}))
    executor = MyModelChoiceField(label="Исполнитель заказа", queryset=User.objects.all(),
                                  required=True, empty_label="Выберите исполнителя",
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    list_of_jobs = forms.CharField(max_length=255, required=True, label="Список работ",
                                    widget=forms.Textarea(attrs={'class': 'form-control'}))
    order_comment = forms.CharField(max_length=255, required=False, label="Комментарий",
                                    widget=forms.Textarea(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super(MaintenanceOrderForm, self).clean()
        client = cleaned_data.get("client")
        client_position = cleaned_data.get("client_position")
        client_dep = cleaned_data.get("client_dep")

        if client.client_corp and not client_dep:
            msg = "У корпоративного клиента не указано отделение"
            self.add_error('client_dep', msg)
        if client.client_corp and not client_position:
            msg = "Обязательно укажите размещение у клиента"
            self.add_error('client_position', msg)


class MaintenanceRegularActionForm(forms.ModelForm):
    class Meta:
        model = MaintenanceAction
        fields = ['status', 'action_content']

    status = forms.ModelChoiceField(label="Статус заказа", required=True, queryset=MaintenanceActionStatus.objects.exclude(status_name__in=[4,5]), widget=forms.Select(attrs={'class':'form-control'}))
    action_content = forms.CharField(label="Выполненные работы", required=True, widget=forms.Textarea(attrs={'class': 'form-control'}))


class MaintenanceSuperActionForm(MaintenanceRegularActionForm):
    class Meta:
        model = MaintenanceAction
        fields = ['manager_user', 'executor_user', 'status', 'action_content']

    manager_user = MyModelChoiceField(queryset= User.objects.exclude(groups__name="outsource"),
                                      label="Руководитель заказа", required=True, widget=forms.Select(attrs={'class':'form-control'}))
    executor_user = MyModelChoiceField(queryset= User.objects.filter(groups__name="serviceman"),
                                       label="Исполнитель заказа", required=True, widget=forms.Select(attrs={'class':'form-control'}))
    status = forms.ModelChoiceField(label="Статус заказа", required=True,
                                    queryset=MaintenanceActionStatus.objects.all(),
                                    widget=forms.Select(attrs={'class': 'form-control'}))


class CartridgeSpareForm(forms.ModelForm):
    class Meta:
        model = CartridgeOrderSparesContent
        fields = ["spare_name", "spare_serial", "spares_qty"]

    spare_name = forms.CharField(label='Наименование запчасти', required=True, widget=forms.Textarea(attrs={'class':'form-control', 'cols': '30', 'rows': '4'}))
    spare_serial = forms.CharField(label='Серийный номер запчасти', required=True, max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}))
    spares_qty = forms.IntegerField(label='Кол-во', required=True, min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))

class CartridgeServiceForm(forms.ModelForm):
    class Meta:
        model = CartridgeOrderServiceContent
        fields = ["service_name", "service_qty", "cost"]

    service_name = forms.CharField(label="Наименование работ", required=True, widget=forms.Textarea(attrs={'class':'form-control', 'cols': '30', 'rows': '4'}))
    service_qty = forms.IntegerField(label="Кол-во", required=True, min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    cost = forms.IntegerField(label="Стоимость 1 шт", required=True, min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))