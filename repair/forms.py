from django import forms
from repair.models import DocOrderHeader, DocOrderAction, DocOrderSparesContent, DocOrderServiceContent, DirStatus
from django.contrib.auth.models import User
from django.forms import ModelChoiceField

# for user model
class MyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "{}".format(obj.get_full_name())


class OrderHeaderForm (forms.ModelForm):
    class Meta:
        model = DocOrderHeader
        fields = ["order_barcode", "client", "client_position", "device_name", "device_defect", "device_serial",
                  "order_comment"]

    # client = forms.ModelChoiceField(queryset=)
    order_barcode = forms.CharField(max_length=150, label="Штрихкод")
    client_position = forms.CharField(max_length=150, label="Размещение у клиента", widget=forms.Textarea)
    device_name = forms.CharField(max_length=100, required=True, label="Наименование устройства")
    device_defect = forms.CharField(max_length=255, required=True, label="Заявленная неисправность", widget=forms.Textarea)
    device_serial = forms.CharField(required=True, label="Серийный номер устройства")
    order_comment = forms.CharField(max_length=255, label="Комментарий", widget=forms.Textarea)
    executor = forms.ChoiceField(label="Исполнитель", choices=[(user.id, user.get_full_name()) for user in User.objects.all()], required=True)

class ActionForm(forms.ModelForm):
    class Meta:
        model = DocOrderAction
        fields = ["manager_user", "executor_user", "status", "action_comment"]

    manager_user = MyModelChoiceField(queryset= User.objects.all(), label="Руководитель заказа", required=True)

    def save(self, order_id):
        obj = super(ActionForm, self).save(commit=False)
        obj.doc_order = DocOrderHeader.objects.get(pk=order_id)
        return obj.save()


class SpareForm(forms.ModelForm):
    class Meta:
        model = DocOrderSparesContent
        fields = ["spare_name", "spare_serial"]


    def save(self, order_id):
        obj = super(SpareForm, self).save(commit=False)
        obj.order = DocOrderHeader.objects.get(pk=order_id)
        return obj.save()


class ServiceForm(forms.ModelForm):
    class Meta:
        model = DocOrderServiceContent
        fields = ["service_name", "service_qty"]

    def save(self, order_id):
        obj = super(ServiceForm, self).save(commit=False)
        obj.order = DocOrderHeader.objects.get(pk=order_id)
        return obj.save()


"""
Forms below - for outsource group users
"""

class ActionOutForm(forms.ModelForm):
    class Meta:
        model = DocOrderAction
        fields = ["action_comment"]

    def save(self, order_id, user):
        obj = super(ActionOutForm, self).save(commit=False)
        obj.doc_order = DocOrderHeader.objects.get(pk=order_id)
        obj.executor_user = user
        obj.status = DirStatus.objacts.filter(status_name="В работе")[0]
        return obj.save()


class ServiceOutForm(forms.ModelForm):
    class Meta:
        model = DocOrderServiceContent
        fields = ["service_name", "service_qty"]

    def save(self, order_id):
        obj = super(ServiceOutForm, self).save(commit=False)
        obj.order = DocOrderHeader.objects.get(pk=order_id)
        return obj.save()
