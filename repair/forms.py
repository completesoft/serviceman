from django import forms
from repair.models import DocOrderHeader, DocOrderAction, DocOrderSparesContent, DocOrderServiceContent, DirStatus, Clients, ClientsDep
from django.contrib.auth.models import User
from django.forms import ModelChoiceField, CharField, IntegerField
from django.forms import widgets

# for user model
class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "{}".format(obj.get_full_name())


class OrderHeaderForm (forms.ModelForm):
    class Meta:
        model = DocOrderHeader
        fields = ["order_barcode", "client", "client_dep", "client_position", "device_name", "device_serial", "device_defect",
                  "order_comment"]

    order_barcode = forms.CharField(max_length=150, label="Штрихкод", widget=forms.TextInput(attrs={'class':'form-control'}), error_messages={'unique': 'Поле должно быть уникальным'})
    client_position = forms.CharField(max_length=150, label="Размещение у клиента", widget=forms.TextInput(attrs={'class':'form-control'}))
    device_name = forms.CharField(max_length=100, required=True, label="Наименование устройства", widget=forms.TextInput(attrs={'class':'form-control'}))
    device_defect = forms.CharField(max_length=255, required=True, label="Заявленная неисправность", widget=forms.Textarea(attrs={'class':'form-control'}))
    device_serial = forms.CharField(required=True, label="Серийный номер устройства", widget=forms.TextInput(attrs={'class':'form-control'}))
    order_comment = forms.CharField(max_length=255, label="Комментарий", widget=forms.Textarea, required=False)
    client_dep = forms.ModelChoiceField(label="Отделения клиента", initial=ClientsDep.objects.none(), queryset=ClientsDep.objects.all(), required=False, widget=forms.Select(attrs={'class':'form-control'}))
    executor = MyModelChoiceField(label="Исполнитель заказа", queryset= User.objects.all(), required=True, empty_label="Выберите исполнителя", widget=forms.Select(attrs={'class':'form-control'}))
    client = forms.ModelChoiceField(label="Клиент", queryset=Clients.objects.all(), required=True, widget=forms.Select(attrs={'class':'form-control'}))
    order_comment = forms.CharField(label="Комментарий", required=False, widget=forms.TextInput(attrs={'class':'form-control'}))

class ActionForm(forms.ModelForm):
    class Meta:
        model = DocOrderAction
        fields = ["manager_user", "executor_user", "status", "action_comment"]

    status = forms.ModelChoiceField(label="Статус заказа", required=True, queryset=DirStatus.objects.all())
    manager_user = MyModelChoiceField(queryset= User.objects.exclude(groups__name="outsource"), label="Руководитель заказа", required=True)
    executor_user = MyModelChoiceField(queryset= User.objects.all(), label="Исполнитель заказа", required=True)


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
