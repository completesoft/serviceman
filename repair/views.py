from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import DocOrderHeader, DocOrderAction, DirStatus
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse
from .forms import OrderHeaderForm, ActionForm, SpareForm, ServiceForm
from django.utils.decorators import method_decorator
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from serviceman.settings import LOGIN_URL


@login_required
def index (request):
    print(request.user)
    user = request.user
    outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
    print(outsource_group)
    # outsource_group = Group.objects.filter(user=user).filter(name='outsource').values_list('name', flat=True)
    if not user.is_active:
        redirect(LOGIN_URL)
    elif user.is_superuser or not outsource_group:
        orders = DocOrderHeader.objects.all()
        return render(request, 'repair/index.html', {"orders": orders, "user": request.user})
    else:
        raw_orders = DocOrderHeader.objects.filter(docorderaction__executor_user=user)
        print(raw_orders)
        orders = [obj for obj in raw_orders if obj.last_action().executor_user==user]
        print(orders)
        return render(request, 'repair/index.html', {"orders": orders, "user": request.user})


@login_required
def my_order(request):
    orders = DocOrderHeader.objects.filter(user=request.user)
    return render(request, 'repair/my_order.html', {"orders": orders, "user": request.user})



class OrderCreateView(CreateView):
    form_class = OrderHeaderForm
    model = DocOrderHeader
    template_name = "repair/order_add.html"
    # fields = ["order_barcode", "client", "client_contact", "device_name", "device_defect", "device_serial", "order_comment"]


    def get(self, request, *args, **kwargs):
        return super(OrderCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.success_url=reverse("repair:my_order")
        return super(OrderCreateView, self).post(request, *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OrderCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user= self.request.user
        instance.save()
        ord_action = DocOrderAction(doc_order=instance, user=instance.user, status=DirStatus.objects.get(status_name="Новый"))
        ord_action.save()
        return super(OrderCreateView, self).form_valid(form)


class OrderDetailView(DetailView):
    template_name = "repair/order_detail.html"
    model = DocOrderHeader
    context_object_name = "order"
    pk_url_kwarg = "order_id"

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        print(context)
        # try:
        context["order_action"]=DocOrderAction.objects.filter(doc_order=self.object).order_by("action_datetime")
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(OrderDetailView, self).dispatch(request, *args, **kwargs)


@login_required
def action_add(request, order_id):
    spare_prefix = 'spare'
    service_prefix = 'service'
    if request.method == 'POST':
        action_form = ActionForm(request.POST)
        # formset
        SpareFormSet = formset_factory(SpareForm, extra=0)
        spare_formset = SpareFormSet(request.POST, prefix=spare_prefix)
        ServiceFormSet = formset_factory(ServiceForm, extra=0)
        service_formset = ServiceFormSet(request.POST, prefix=service_prefix)
        if action_form.is_valid():
            action_form.save()
            if spare_formset.is_valid():
                for form in spare_formset:
                    if form.has_changed():
                        form.save()
            if service_formset.is_valid():
                for form in service_formset:
                    if form.has_changed():
                        form.save()
            return HttpResponseRedirect(reverse("repair:my_order"))
    else:
        data_raw = {'{}-TOTAL_FORMS': '1', '{}-INITIAL_FORMS': '1', '{}-MAX_NUM_FORMS': ''}
        data_spare = {k.format(spare_prefix): v for k, v in data_raw.items()}
        data_service = {k.format(service_prefix): v for k, v in data_raw.items()}
        action_form = ActionForm()
        SpareFormSet = formset_factory(SpareForm, extra=0)
        spare_formset = SpareFormSet(data_spare, prefix=spare_prefix)
        ServiceFormSet = formset_factory(ServiceForm, extra=0)
        service_formset = ServiceFormSet(data_service, prefix=service_prefix)
    return render(request, 'repair/action.html',
                  {'action_form': action_form, 'spare_formset': spare_formset, 'service_formset': service_formset, 'order_id': order_id})


