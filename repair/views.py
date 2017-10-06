from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect, render_to_response, resolve_url
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Group, User
from django.contrib.auth.views import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import deprecate_current_app
from django.views.decorators.cache import never_cache
from .models import DocOrderHeader, DocOrderAction, DirStatus, DocOrderServiceContent, DocOrderSparesContent, Clients, \
    ClientsDep
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse
from .forms import OrderHeaderForm, ActionForm, ActionFormOut,SpareForm, ServiceForm, ClientForm, ClientDepForm, ClientEditForm
from django.utils.decorators import method_decorator
from django.forms import formset_factory, modelformset_factory, inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404, HttpResponseNotFound
from serviceman.settings import LOGIN_URL
from django.contrib import messages
from django.core.exceptions import FieldError, ValidationError, ObjectDoesNotExist
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.core.paginator import Paginator, InvalidPage
from django.middleware.csrf import get_token
from django.db.models import Q

@login_required
def index(request):
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
            raw_orders = DocOrderHeader.objects.filter(docorderaction__executor_user=user).distinct()
            orders = [obj for obj in raw_orders if obj.last_status()!="Архивный"]
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
            # raw_orders = DocOrderHeader.objects.filter(docorderaction__manager_user=user).order_by('-id').distinct()
            raw_orders = DocOrderHeader.objects.filter(Q(docorderaction__manager_user=user)|Q(docorderaction__executor_user=user)).order_by('-id').distinct()
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
        # self.initial["client_dep"] = ClientsDep.objects.none()
        return super(OrderCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.success_url = reverse("repair:my_order")
        return super(OrderCreateView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OrderCreateView, self).get_context_data(**kwargs)
        context["form"].fields['client_dep'].queryset = ClientsDep.objects.none()
        if context["form"]['client'].data:
            context["form"].fields['client_dep'].queryset = ClientsDep.objects.filter(client=context["form"]['client'].data)
        else:
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
        ord_action = DocOrderAction(doc_order=instance, manager_user=self.request.user, setting_user=self.request.user,
                                    executor_user=User.objects.get(pk=self.request.POST["executor"]),
                                    status=DirStatus.objects.get(status_name="Новый"))
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
        context["order_action"] = DocOrderAction.objects.filter(doc_order=self.object).order_by("action_datetime")
        context["spares"] = DocOrderSparesContent.objects.filter(order=self.object)
        context["services"] = DocOrderServiceContent.objects.filter(order=self.object)
        service_form = ServiceForm()
        context["service_form"] = service_form
        spare_form = SpareForm()
        context["spare_form"] = spare_form
        user = self.request.user
        outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
        context["outsource"] = True if outsource_group else False
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_active:
            order = DocOrderHeader.objects.get(pk=self.kwargs["order_id"])
            outsource_group = True if request.user.groups.filter(name='outsource').values_list('name',
                                                                                               flat=True) else False
            if outsource_group:
                act = DocOrderAction.objects.filter(doc_order=order).filter(executor_user=request.user)
                if not act:
                    return redirect("repair:my_order")
            return super(OrderDetailView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


class ActionCreateView(CreateView):
    model = DocOrderAction
    template_name = "repair/action_add.html"

    def get(self, request, *args, **kwargs):
        outsource_group = request.user.groups.filter(name='outsource').values_list('name', flat=True)
        if outsource_group:
            self.form_class = ActionFormOut
        else:
            self.form_class = ActionForm
        order = DocOrderHeader.objects.get(pk=kwargs["order_id"])
        self.initial["manager_user"] = order.last_action().manager_user
        return super(ActionCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.success_url = reverse("repair:my_order")
        outsource_group = request.user.groups.filter(name='outsource').values_list('name', flat=True)
        if outsource_group:
            self.form_class = ActionFormOut
        else:
            self.form_class = ActionForm
        if not request.user.is_superuser and request.POST["status"] == "Архивный":
            return self.get(request, *args, **kwargs)
        return super(ActionCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.doc_order = DocOrderHeader.objects.get(pk=self.kwargs["order_id"])
        form.instance.setting_user = self.request.user
        outsource_group = self.request.user.groups.filter(name='outsource').values_list('name', flat=True)
        if outsource_group:
            last_act = DocOrderHeader.objects.get(pk=self.kwargs["order_id"]).last_action()
            form.instance.manager_user = last_act.manager_user
            form.instance.executor_user = last_act.executor_user
        return super(ActionCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ActionCreateView, self).get_context_data(**kwargs)
        context["order"] = DocOrderHeader.objects.get(pk=self.kwargs["order_id"])
        outsource_group = self.request.user.groups.filter(name='outsource').values_list('name', flat=True)
        context["outsource"] = True if outsource_group else False
        if not self.request.user.is_superuser:
            if outsource_group:
                context["form"].fields["status"].queryset = DirStatus.objects.exclude(status_name__in=["Архивный", "Передан клиенту"])
            else:
                context["form"].fields["status"].queryset = DirStatus.objects.exclude(status_name="Архивный")
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        outsource_group = True if request.user.groups.filter(name='outsource').values_list('name', flat=True) else False
        if not request.user.is_active:
            return redirect(LOGIN_URL)
        order = DocOrderHeader.objects.get(pk=self.kwargs["order_id"])
        if order.last_status() == "Архивный" and not request.user.is_superuser:
            return redirect("repair:order_detail", order_id=kwargs["order_id"])
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
        return render(request, 'repair/service_add.html',
                      {'service_formset': service_formset, 'order': order, "outsource": outsource_group})
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
                if dep == "":
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
                return HttpResponse(
                    '<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
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
            departments = list(
                ClientsDep.objects.filter(client=Clients.objects.get(pk=kwargs["client_id"])).values("id",
                                                                                                     "client_dep_name"))
            if departments:
                department_set.extend(departments)
        return JsonResponse(department_set, safe=False)
    else:
        return redirect(LOGIN_URL)


class OrderArchiveView(ListView):
    template_name = "repair/order_archive.html"
    context_object_name = "orders"

    def get_queryset(self):
        user = self.request.user
        outsource_group = user.groups.filter(name='outsource').values_list('name', flat=True)
        if outsource_group:
            raw_orders = DocOrderHeader.objects.filter(docorderaction__executor_user=user).order_by('-id').distinct()
        else:
            raw_orders = DocOrderHeader.objects.all()
        orders = [obj for obj in raw_orders if obj.last_status() == "Архивный"]
        return orders

    def get_context_data(self, **kwargs):
        context = super(OrderArchiveView, self).get_context_data(**kwargs)
        outsource_group = self.request.user.groups.filter(name='outsource').values_list('name', flat=True)
        context["outsource"] = True if outsource_group else False
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_active:
            return super(OrderArchiveView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


@login_required
def ajax_add_service(request, order_id):
    try:
        order = DocOrderHeader.objects.get(pk=order_id)
        if order.last_status() == "Архивный" and not request.user.is_superuser:
            raise ObjectDoesNotExist("Access denied")
    except ObjectDoesNotExist as msg:
        return HttpResponseNotFound(msg)
    if request.method == "POST":
        service_form = ServiceForm(request.POST)
        if service_form.is_valid():
            obj_service = service_form.save(commit=False)
            obj_service.order = order
            obj_service.setting_user = request.user
            obj_service.save()
            new_service_form = ServiceForm()
            form = render_to_string('repair/ajax/ajax_add_service_form.html',
                                    context={'service_form': new_service_form, 'order_id': order.id}, request=request)
            tr = render_to_string('repair/ajax/ajax_add_service_tr.html',
                                  context={'order_id': order.id, "service": obj_service}, request=request)
        else:
            form = render_to_string('repair/ajax/ajax_add_service_form.html',
                                    context={'service_form': service_form, 'order_id': order.id}, request=request)
            tr = "error"
        data = {"form": form, "tr": tr}
        return JsonResponse(data)
    return HttpResponseNotFound()


@login_required
@ensure_csrf_cookie
def service(request):
    try:
        order_id = request.GET.get("order_id") if request.GET else request.POST.get("order_id")
        order = DocOrderHeader.objects.get(pk=order_id)
        if order.last_status() == "Архивный" and not request.user.is_superuser:
            raise ObjectDoesNotExist("Access denied")
    except ObjectDoesNotExist as msg:
        return HttpResponseNotFound(msg)
    if request.method == "POST":
        service = DocOrderServiceContent.objects.get(pk=request.POST["service_id"])
        if service in order.docorderservicecontent_set.all():
            service.delete()
            data = {"service": "#service{}".format(request.POST["service_id"])}
            return JsonResponse(data)
    else:
        service = DocOrderServiceContent.objects.get(pk=request.GET["service_id"])
        if service in order.docorderservicecontent_set.all():
            data = {"order_id": order_id, "service_id": request.GET["service_id"],
                    "csrf_token": get_token(request)}
            return JsonResponse(data)
    return redirect("repair:order_detail", order_id=order_id)


@login_required
def ajax_add_spare(request, order_id):
    try:
        order = DocOrderHeader.objects.get(pk=order_id)
        if order.last_status() == "Архивный" and not request.user.is_superuser:
            raise ObjectDoesNotExist("Access denied")
    except ObjectDoesNotExist as msg:
        return HttpResponseNotFound(msg)
    if request.method == "POST":
        spare_form = SpareForm(request.POST)
        if spare_form.is_valid():
            obj_spare = spare_form.save(commit=False)
            obj_spare.order = order
            obj_spare.setting_user = request.user
            obj_spare.save()
            print(obj_spare.spares_qty)
            new_spare_form = SpareForm()
            form = render_to_string('repair/ajax/ajax_add_spare_form.html',
                                    context={'spare_form': new_spare_form, 'order_id': order.id}, request=request)
            tr = render_to_string('repair/ajax/ajax_add_spare_tr.html',
                                  context={'order_id': order.id, "spare": obj_spare}, request=request)
        else:
            form = render_to_string('repair/ajax/ajax_add_spare_form.html',
                                    context={'spare_form': spare_form, 'order_id': order.id}, request=request)
            tr = "error"
        data = {"form": form, "tr": tr}
        return JsonResponse(data)
    return HttpResponseNotFound()


@login_required
@ensure_csrf_cookie
def spare(request):
    try:
        order_id = request.GET.get("order_id") if request.GET else request.POST.get("order_id")
        order = DocOrderHeader.objects.get(pk=order_id)
        if order.last_status() == "Архивный" and not request.user.is_superuser:
            raise ObjectDoesNotExist("Access denied")
    except ObjectDoesNotExist as msg:
        return HttpResponseNotFound(msg)
    if request.method == "POST":
        spare = DocOrderSparesContent.objects.get(pk=request.POST["spare_id"])
        if spare in order.docordersparescontent_set.all():
            spare.delete()
            data = {"spare": "#spare{}".format(request.POST["spare_id"])}
            return JsonResponse(data)
    else:
        spare = DocOrderSparesContent.objects.get(pk=request.GET["spare_id"])
        if spare in order.docordersparescontent_set.all():
            data = {"order_id": order_id, "spare_id": request.GET["spare_id"],
                    "csrf_token": get_token(request)}
            return JsonResponse(data)
    return redirect("repair:order_detail", order_id=order_id)


@sensitive_post_parameters()
@csrf_protect
@login_required
@deprecate_current_app
def password_change(request,
                    template_name='registration/password_change_form.html',
                    post_change_redirect=None,
                    password_change_form=PasswordChangeForm,
                    extra_context=None):
    if post_change_redirect is None:
        post_change_redirect = reverse('password_change_done')
    else:
        post_change_redirect = resolve_url(post_change_redirect)
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Updating the password logs out all other sessions for the user
            # except the current one.
            update_session_auth_hash(request, form.user)
            messages.add_message(request, messages.SUCCESS, "Пароль изменен!!!")
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)