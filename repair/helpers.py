from django.utils import timezone
from .models import DocOrderHeader, DirStatus


def zero_padding(str):
    if len(str)<2:
        return '0'+str
    return str


def barcode_generator(model, user):
    orders = model.objects.filter(order_datetime__date=timezone.now().date(), docorderaction__setting_user=user, docorderaction__status__status_name=DirStatus.NEW).distinct()
    if orders:
        order = orders.latest('order_datetime')
        barcode_last_two_digit = order.order_barcode[-2:]
        barcode = order.order_datetime.strftime('%y%m%d')+zero_padding(str(user.id))+zero_padding(str(int(barcode_last_two_digit)+1))
    else:
        barcode = timezone.now().strftime('%y%m%d') + zero_padding(str(user.id)) + '01'
    return barcode