from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import DocOrderHeader, DocOrderAction, DirStatus, DocOrderServiceContent, DocOrderSparesContent, Clients, ClientsDep
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse
from .forms import OrderHeaderForm, ActionForm, SpareForm, ServiceForm, ClientForm, ClientDepForm, ClientEditForm
from django.utils.decorators import method_decorator
from django.forms import formset_factory, modelformset_factory, inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from serviceman.settings import LOGIN_URL
from django.contrib import messages
from django.core.exceptions import FieldError, ValidationError
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, InvalidPage

@login_required
def index (request):
    user = request.user
    outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
    if user.is_active:
        # try:
        #     page_num = request.GET["page"]
        # except KeyError:
        #     page_num = 1
        if not outsource_group:
            # paginator = Paginator(DocOrderHeader.objects.all(), 15)
            # try:
            #     orders = paginator.page(page_num)
            # except InvalidPage:
            #     orders = paginator.page(1)
            raw_orders = DocOrderHeader.objects.all()
            orders = [obj for obj in raw_orders if obj.last_status() != "Архивный"]
            return render(request, 'repair/index.html', {"orders": orders, "user": request.user, "outsource": False})
        else:
            # for "outsource" group
            orders = DocOrderHeader.objects.filter(docorderaction__executor_user=user).distinct("order_barcode")
            # orders = [obj for obj in raw_orders if obj.last_action().executor_user == user and obj.last_status()!="Архивный"]
            # paginator = Paginator(orders_set, 15)
            # try:
            #     orders = paginator.page(page_num)
            # except InvalidPage:
            #     orders = paginator.page(1)
            return render(request, 'repair/index.html', {"orders": orders, "user": request.user, "outsource": True})
    redirect(LOGIN_URL)

@login_required
def my_order(request):
    user = request.user
    outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
    if user.is_active:
        if not outsource_group:
            # try:
            #     page_num = request.GET["page"]
            # except KeyError:
            #     page_num = 1
            # orders_set = DocOrderHeader.objects.filter(docorderaction__manager_user=user).order_by('-id').distinct()
            # paginator = Paginator(orders_set, 15)
            # try:
            #     orders = paginator.page(page_num)
            # except InvalidPage:
            #     orders = paginator.page(1)
            raw_orders = DocOrderHeader.objects.filter(docorderaction__manager_user=user).order_by('-id').distinct()
            orders = [obj for obj in raw_orders if obj.last_status() != "Архивный"]
            return render(request, 'repair/my_order.html', {"orders": orders, "user": request.user})
        else:
            return redirect(reverse("repair:index"))
    return redirect(LOGIN_URL)


class OrderCreateView(CreateView):
    form_class = OrderHeaderForm
    model = DocOrderHeader
    template_name = "repair/order_add.html"

    def get(self, request, *args, **kwargs):
        self.initial["client_dep"]=ClientsDep.objects.none()
        return super(OrderCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.success_url=reverse("repair:my_order")
        return super(OrderCreateView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OrderCreateView, self).get_context_data(**kwargs)
        context["form"].fields['client_dep'].queryset = ClientsDep.objects.none()
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
        if user.is_active and (user.is_superuser or not outsource_group):
            return super(OrderCreateView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)

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
            order = DocOrderHeader.objects.get(pk=self.kwargs["order_id"])
            outsource_group = True if request.user.groups.filter(name='outsource').values_list('name', flat=True) else False
            if outsource_group:
                act = DocOrderAction.objects.filter(doc_order=order).filter(executor_user=request.user)
                if not act:
                    return redirect("repair:my_order")
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
        if not self.request.user.is_superuser and request.POST["status"] == "Архивный":
            return self.get(request, *args, **kwargs)
        return super(ActionCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.doc_order = DocOrderHeader.objects.get(pk=self.kwargs["order_id"])
        form.instance.setting_user = self.request.user
        return super(ActionCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ActionCreateView, self).get_context_data(**kwargs)
        context["order"] = DocOrderHeader.objects.get(pk=self.kwargs["order_id"])
        if not self.request.user.is_superuser:
            context["form"].fields["status"].queryset = DirStatus.objects.exclude(status_name="Архивный")
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        outsource_group = True if request.user.groups.filter(name='outsource').values_list('name', flat=True) else False
        if not request.user.is_active:
            return redirect(LOGIN_URL)
        if outsource_group:
            return redirect("repair:index")
        order = DocOrderHeader.objects.get(pk=self.kwargs["order_id"])
        if order.last_status()== "Архивный" and not request.user.is_superuser:
            return redirect("repair:index")
        return super(ActionCreateView, self).dispatch(request, *args, **kwargs)


@login_required
def service_add(request, order_id):
    user = request.user
    if user.is_active:
        order = DocOrderHeader.objects.get(pk=order_id)
        outsource_group = True if user.groups.filter(name='outsource').values_list('name', flat=True) else False
        service_prefix = 'service'
        ServiceFormSet = inlineformset_factory(DocOrderHeader, DocOrderServiceContent, form=ServiceForm, extra=1)
        if request.method == 'POST':
            service_formset = ServiceFormSet(request.POST, prefix=service_prefix, instance=order)
            if service_formset.is_valid():
                service_formset.save()
                return redirect("repair:order_detail", order_id=order_id)
        # non POST method
        else:
            service_formset = ServiceFormSet(instance=order, prefix=service_prefix)
        return render(request, 'repair/service_add.html', {'service_formset': service_formset, 'order': order, "outsource": outsource_group})
    else:
        return redirect(LOGIN_URL)


@login_required
def spares_add(request, order_id):
    user = request.user
    order = DocOrderHeader.objects.get(pk=order_id)
    outsource_group = True if user.groups.filter(name='outsource').values_list('name', flat=True) else False
    if user.is_active and not outsource_group:
        order = DocOrderHeader.objects.get(pk=order_id)
        spare_prefix = 'spare'
        SpareFormSet = inlineformset_factory(DocOrderHeader, DocOrderSparesContent, form=SpareForm, extra=1)
        if request.method == 'POST':
            spare_formset = SpareFormSet(request.POST, prefix=spare_prefix, instance=order)
            if spare_formset.is_valid():
                spare_formset.save()
                return redirect("repair:order_detail", order_id=order_id)
        else:
            spare_formset = SpareFormSet(instance=order, prefix=spare_prefix)
        return render(request, 'repair/spares_add.html', {'spare_formset': spare_formset, 'order': order})
    else:
        return redirect(LOGIN_URL)


class ClientListView(ListView):
    template_name = "repair/client.html"
    model = Clients
    ordering = "client_name"
    context_object_name = "clients"
    # paginate_by = 15

    # def get_queryset(self):
    #     return Clients.objects.all().order_by("client_name")

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


def handlePopAdd(request, addForm, field):
    if request.method == "POST":
        form = addForm(request.POST)
        if form.is_valid():
            try:
                newObject = form.save()
            except ValidationError:
                newObject = None
            if newObject:
                client_dep_post = request.POST.getlist("client_dep_name")
                if client_dep_post:
                    for dep in client_dep_post:
                        if dep == "":
                            continue
                        client_dep = ClientsDep(client=newObject, client_dep_name=dep)
                        client_dep.save()
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                    (escape(newObject._get_pk_val()), escape(newObject)))
    else:
        form = addForm()
    pageContext = {'form': form, 'field': field}
    return render_to_response("repair/client_add_popup.html", pageContext)


@login_required
@csrf_exempt
def popupClientView(request):
    user = request.user
    outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
    if user.is_active and not outsource_group:
        return handlePopAdd(request, ClientForm, 'client')
    else:
        return redirect(LOGIN_URL)


@login_required
def dep_update(request, **kwargs):
    user = request.user
    outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
    if user.is_active and not outsource_group:
        department_set = [{"id": "", "client_dep_name": "Не выбрано"}]
        if request.method == "POST" and request.is_ajax():
            departments = list(ClientsDep.objects.filter(client=Clients.objects.get(pk=kwargs["client_id"])).values("id", "client_dep_name"))
            if departments:
                department_set.extend(departments)
        return JsonResponse(department_set, safe=False)
    else:
        return redirect(LOGIN_URL)


class OrderArchiveView(ListView):
    template_name = "repair/order_archive.html"
    context_object_name = "orders"

    def get_queryset(self):
        raw_orders = DocOrderHeader.objects.all()
        orders = [obj for obj in raw_orders if obj.last_status() == "Архивный"]
        return orders

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
        if user.is_active and not outsource_group:
            return super(OrderArchiveView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)