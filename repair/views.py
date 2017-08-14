from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import DocOrderHeader, DocOrderAction, DirStatus
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse
from .forms import OrderHeaderForm
from django.utils.decorators import method_decorator



@login_required
def index (request):
    print(request.user)
    orders = DocOrderHeader.objects.all()
    return render(request, 'repair/index.html', {"orders": orders, "user": request.user})


@login_required
def my_order(request):
    orders = DocOrderHeader.objects.filter(user=request.user)
    return render(request, 'repair/my_order.html', {"orders": orders, "user": request.user})



class OrderCreate(CreateView):
    form_class = OrderHeaderForm
    model = DocOrderHeader
    template_name = "repair/order_add.html"
    # fields = ["order_barcode", "client", "client_contact", "device_name", "device_defect", "device_serial", "order_comment"]


    def get(self, request, *args, **kwargs):
        return super(OrderCreate, self).get(request, *args, **kwargs)



    def post(self, request, *args, **kwargs):
        self.success_url=reverse("repair:my_order")
        return super(OrderCreate, self).post(request, *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OrderCreate, self).dispatch(*args, **kwargs)



    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user= self.request.user
        instance.save()
        ord_action = DocOrderAction(doc_order=instance, user=instance.user, status=DirStatus.objects.get(status_name="Новый"))
        ord_action.save()
        return super(OrderCreate, self).form_valid(form)



