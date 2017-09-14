from django.shortcuts import render, redirect
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import DocOrderHeader, DocOrderAction, DirStatus, DocOrderServiceContent, DocOrderSparesContent, Clients, ClientsDep
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse
from .forms import OrderHeaderForm, ActionForm, SpareForm, ServiceForm, ServiceOutForm, ClientForm, ClientDepForm, ClientEditForm
from django.utils.decorators import method_decorator
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from serviceman.settings import LOGIN_URL
from django.contrib import messages
from django.core.exceptions import FieldError


@login_required
def index (request):
    user = request.user
    outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
    if user.is_active:
        if not outsource_group:
            orders = DocOrderHeader.objects.all()
            return render(request, 'repair/index.html', {"orders": orders, "user": request.user, "outsource": False})
        else:
            # for "outsource" group
            raw_orders = DocOrderHeader.objects.filter(docorderaction__executor_user=user).distinct()
            orders = [obj for obj in raw_orders if obj.last_action().executor_user == user]
            return render(request, 'repair/index.html', {"orders": orders, "user": request.user, "outsource": True})
    redirect(LOGIN_URL)

@login_required
def my_order(request):
    user = request.user
    outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
    if user.is_active:
        if not outsource_group:
            orders = DocOrderHeader.objects.filter(docorderaction__manager_user=user).order_by('-id').distinct()
            return render(request, 'repair/my_order.html', {"orders": orders, "user": request.user})
        else:
            return redirect(reverse("repair:index"))
    return redirect(LOGIN_URL)





class OrderCreateView(CreateView):
    form_class = OrderHeaderForm
    model = DocOrderHeader
    template_name = "repair/order_add.html"


    def get(self, request, *args, **kwargs):
        user = request.user
        outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
        if user.is_active and (user.is_superuser or not outsource_group):
            return super(OrderCreateView, self).get(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)

    def post(self, request, *args, **kwargs):
        self.success_url=reverse("repair:my_order")
        user = request.user
        outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
        if user.is_active and (user.is_superuser or not outsource_group):
            return super(OrderCreateView, self).post(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)

    def get_context_data(self, **kwargs):
        context = super(OrderCreateView, self).get_context_data(**kwargs)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OrderCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        resp = super(OrderCreateView, self).form_valid(form)
        instance = self.object
        ord_action = DocOrderAction(doc_order=instance, manager_user=self.request.user, setting_user=self.request.user, executor_user=User.objects.get(pk=self.request.POST["executor"]), status=DirStatus.objects.get(status_name="Новый"))
        ord_action.save()
        messages.add_message(self.request, messages.SUCCESS, "Новый заказ добавлен!!!")
        return resp


class OrderDetailView(DetailView):
    template_name = "repair/order_detail.html"
    model = DocOrderHeader
    context_object_name = "order"
    pk_url_kwarg = "order_id"

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context["order_action"]=DocOrderAction.objects.filter(doc_order=self.object).order_by("action_datetime")
        context["spares"]= DocOrderSparesContent.objects.filter(order=self.object)
        context["services"]= DocOrderServiceContent.objects.filter(order=self.object)
        user = self.request.user
        outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
        context["outsource"]=True if outsource_group else False
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_active:
            return super(OrderDetailView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


class ActionCreateView(CreateView):
    form_class = ActionForm
    model = DocOrderAction
    template_name = "repair/action_add.html"

    def get(self, request, *args, **kwargs):
        order = DocOrderHeader.objects.get(pk=kwargs["order_id"])

        self.initial["manager_user"]= order.last_action().manager_user
        return super(ActionCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.success_url = reverse("repair:my_order")
        return super(ActionCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.doc_order = DocOrderHeader.objects.get(pk=self.kwargs["order_id"])
        form.instance.setting_user = self.request.user
        return super(ActionCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ActionCreateView, self).get_context_data(**kwargs)
        context["order"] = DocOrderHeader.objects.get(pk=self.kwargs["order_id"])
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        outsource_group = True if request.user.groups.filter(name='outsource').values_list('name', flat=True) else False
        if not request.user.is_active:
            return redirect(LOGIN_URL)
        if outsource_group:
            return redirect("repair:index")
        return super(ActionCreateView, self).dispatch(request, *args, **kwargs)


@login_required
def service_add(request, order_id):
    user = request.user
    order = DocOrderHeader.objects.get(pk=order_id)
    if user.is_active:
        outsource_group = True if user.groups.filter(name='outsource').values_list('name', flat=True) else False
        service_prefix = 'service'
        if request.method == 'POST':
            ServiceFormSet = formset_factory(ServiceForm, extra=0)
            service_formset = ServiceFormSet(request.POST, prefix=service_prefix)
            if service_formset.is_valid():
                for form in service_formset:
                    form.save(order_id)
                return redirect("repair:order_detail", order_id=order_id)
            return render(request, 'repair/service_add.html', {'service_formset': service_formset, 'order': order, "outsource": outsource_group})
        # non POST method
        else:
            data_raw = {'{}-TOTAL_FORMS': '1', '{}-INITIAL_FORMS': '1', '{}-MAX_NUM_FORMS': ''}
            data_service = {k.format(service_prefix): v for k, v in data_raw.items()}
            ServiceFormSet = formset_factory(ServiceOutForm, extra=0)
            service_formset = ServiceFormSet(data_service, prefix=service_prefix)
            return render(request, 'repair/service_add.html', {'service_formset': service_formset, 'order': order, "outsource": outsource_group})
    else:
        return redirect(LOGIN_URL)


@login_required
def spares_add(request, order_id):
    user = request.user
    order = DocOrderHeader.objects.get(pk=order_id)
    outsource_group = True if user.groups.filter(name='outsource').values_list('name', flat=True) else False
    if user.is_active and not outsource_group:
        spare_prefix = 'spare'
        if request.method == 'POST':
            SpareFormSet = formset_factory(SpareForm, extra=0)
            spare_formset = SpareFormSet(request.POST, prefix=spare_prefix)
            if spare_formset.is_valid():
                for form in spare_formset:
                    form.save(order_id)
                return redirect("repair:order_detail", order_id=order_id)
            return render(request, 'repair/spares_add.html',{'spare_formset': spare_formset, 'order': order})
        else:
            data_raw = {'{}-TOTAL_FORMS': '1', '{}-INITIAL_FORMS': '1', '{}-MAX_NUM_FORMS': ''}
            data_spare = {k.format(spare_prefix): v for k, v in data_raw.items()}
            SpareFormSet = formset_factory(SpareForm, extra=0)
            spare_formset = SpareFormSet(data_spare, prefix=spare_prefix)
            return render(request, 'repair/spares_add.html', {'spare_formset': spare_formset, 'order': order})
    else:
        return redirect(LOGIN_URL)


class ClientListView(ListView):
    template_name = "repair/client.html"
    model = Clients
    ordering = "client_name"
    context_object_name = "clients"

    def get_queryset(self):
        return Clients.objects.all().order_by("client_name")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
        if user.is_active and not outsource_group:
            return super(ClientListView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


class ClientCreateView(CreateView):
    form_class = ClientForm
    model = Clients
    template_name = "repair/client_add.html"

    def get_context_data(self, **kwargs):
        context = super(ClientCreateView, self).get_context_data(**kwargs)
        context["dep_form"] = ClientDepForm()
        return context

    def post(self, request, *args, **kwargs):
        self.success_url = reverse("repair:clients")
        return super(ClientCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        resp = super(ClientCreateView, self).form_valid(form)
        instance = self.object
        if instance.client_corp:
            client_dep_post = self.request.POST.getlist("client_dep_name")
            if client_dep_post:
                for dep in client_dep_post:
                    if dep == "":
                        continue
                    client_dep = ClientsDep(client=instance, client_dep_name=dep)
                    client_dep.save()
        # messages.add_message(self.request, messages.SUCCESS, "Новый клиент добавлен!!!")
        return resp

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
        if user.is_active and not outsource_group:
            return super(ClientCreateView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


class ClientDetailView(DetailView):
    template_name = "repair/client_detail.html"
    model = Clients
    context_object_name = "client"
    pk_url_kwarg = "client_id"

    def get_context_data(self, **kwargs):
        context = super(ClientDetailView, self).get_context_data(**kwargs)
        if self.object.client_corp:
            context["department"] = ClientsDep.objects.filter(client_id=self.object)
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
        if user.is_active and not outsource_group:
            return super(ClientDetailView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


class ClientEditView(UpdateView):
    form_class = ClientEditForm
    model = Clients
    template_name = "repair/client_edit.html"
    pk_url_kwarg = "client_id"
    context_object_name = "client"

    def post(self, request, *args, **kwargs):
        self.success_url = reverse("repair:client_detail", kwargs={"client_id": kwargs["client_id"]})
        return super(ClientEditView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        resp = super(ClientEditView, self).form_valid(form)
        instance = self.object
        client_dep_post = self.request.POST.getlist("client_dep_name")
        if client_dep_post:
            for dep in client_dep_post:
                if dep=="":
                    continue
                client_dep = ClientsDep(client=instance, client_dep_name=dep)
                client_dep.save()
        # messages.add_message(self.request, messages.SUCCESS, "Новый клиент добавлен!!!")
        return resp

    def get_context_data(self, **kwargs):
        context = super(ClientEditView, self).get_context_data(**kwargs)
        if self.object.client_corp:
            context["department"] = ClientsDep.objects.filter(client_id=self.object)
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
        if user.is_active and not outsource_group:
            return super(ClientEditView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)