from django import forms
from repair.models import DocOrderHeader, DocOrderAction, DocOrderSparesContent, DocOrderServiceContent


class OrderHeaderForm (forms.ModelForm):
    class Meta:
        model = DocOrderHeader
        fields = ["order_barcode", "client", "client_contact", "device_name", "device_defect", "device_serial",
                  "order_comment"]

    # client = forms.ModelChoiceField(queryset=)
    order_barcode = forms.CharField(max_length=150, label="Штрихкод")
    client_contact = forms.CharField(max_length=150, label="Контакты клиента", widget=forms.Textarea)
    device_name = forms.CharField(max_length=100, required=True, label="Наименование устройства")
    device_defect = forms.CharField(max_length=255, required=True, label="Заявленная неисправность", widget=forms.Textarea)
    device_serial = forms.CharField(required=True, label="Серийный номер устройства")
    order_comment = forms.CharField(max_length=255, label="Комментарий", widget=forms.Textarea)


class ActionForm(forms.ModelForm):
    class Meta:
        model = DocOrderAction
        fields = "__all__"


class SpareForm(forms.ModelForm):
    class Meta:
        model = DocOrderSparesContent
        fields = "__all__"


class ServiceForm(forms.ModelForm):
    class Meta:
        model = DocOrderServiceContent
        fields = "__all__"







