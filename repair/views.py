from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect, render_to_response, resolve_url
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Group, User
from django.contrib.auth.views import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import deprecate_current_app
from django.views.decorators.cache import never_cache
from .models import (DocOrderHeader, DocOrderAction, DirStatus, DocOrderServiceContent,
                     DocOrderSparesContent, Clients, ClientsDep, Reward, Storage, CartridgeOrder, CartridgeActionStatus,
                     Cartridge, CartridgeAction, MaintenanceOrder, MaintenanceAction, MaintenanceActionStatus, CartridgeOrderSparesContent,
                     CartridgeOrderServiceContent)
from django.views.generic.edit import CreateView, UpdateView, FormMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse, reverse_lazy
from .forms import ( OrderHeaderForm, ActionForm, ActionFormOut,SpareForm, ServiceForm,
                     ClientForm, ClientDepForm, ClientEditForm, RewardForm, CartridgeOrderForm ,
                     CartridgeFilterOrderForm, CartridgeRegularActionForm, CartridgeSuperActionForm,
                     MaintenanceOrderForm, MaintenanceRegularActionForm, DateRangeWidgetForm,
                     MaintenanceSuperActionForm, CartridgeCreateForm, CartridgeActionExpressForm, CartridgeServiceForm,
                     CartridgeSpareForm)
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404, HttpResponseNotFound
# from serviceman.settings import LOGIN_URL
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import FieldError, ValidationError, ObjectDoesNotExist
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.core.paginator import Paginator, InvalidPage
from django.middleware.csrf import get_token
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from .helpers import outsource_group_check
import logging
from .filters import DocOrderHeaderFilter, CartridgeOrderFilter, MaintenanceOrderFilter
from django_filters.views import FilterView
from django.utils.timezone import now
from django.forms import CharField

logger = logging.getLogger('user.activity')
LOGIN_URL = getattr(settings, 'LOGIN_URL', None)


class DocOrderHeaderListView(FilterView):
    filterset_class = DocOrderHeaderFilter
    template_name = 'repair/index.html'
    context_object_name = "object_list"
    outsource = True
    daterange_widget_form = DateRangeWidgetForm

    def get(self, request, *args, **kwargs):
        resp = super(DocOrderHeaderListView, self).get(request, *args, **kwargs)
        return resp

    def get_queryset(self):
        user = self.request.user
        if self.outsource:
            orders = DocOrderHeader.objects.filter(docorderaction__executor_user=user).exclude(docorderaction__status__status_name="Архивный").distinct()
        else:
            orders = DocOrderHeader.objects.exclude(docorderaction__status__status_name="Архивный").distinct()
        return orders

    def get_context_data(self, **kwargs):
        context = super(DocOrderHeaderListView, self).get_context_data(**kwargs)
        context['daterange_widget_form'] = self.daterange_widget_form()
        context["outsource"] = self.outsource
        if self.request.GET.get('all'):
            context['object_list'] = self.get_queryset()
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.outsource = request.user.groups.filter(name='outsource').exists()
        if request.user.is_active:
            return super(DocOrderHeaderListView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)



class MyOrderListView(ListView):
    template_name = "repair/my_order.html"
    model = DocOrderHeader
    ordering = "-id"
    context_object_name = "orders"

    def get_queryset(self):
        user = self.request.user
        orders = DocOrderHeader.objects.filter(Q(docorderaction__manager_user=user)|Q(docorderaction__executor_user=user)).exclude(docorderaction__status__status_name="Архивный").distinct()
        return orders

    def get_context_data(self, **kwargs):
        context = super(MyOrderListView, self).get_context_data(**kwargs)
        context["outsource"] = self.outsource
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.outsource = request.user.groups.filter(name='outsource').exists()
        if request.user.is_active:
            return super(MyOrderListView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


class OrderCreateView(CreateView):
    form_class = OrderHeaderForm
    model = DocOrderHeader
    template_name = "repair/order_add.html"

    def get(self, request, *args, **kwargs):
        return super(OrderCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.success_url = reverse("repair:index")
        return super(OrderCreateView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OrderCreateView, self).get_context_data(**kwargs)
        context["form"].fields['client_dep'].queryset = ClientsDep.objects.none()
        if context["form"]['client'].data:
            context["form"].fields['client_dep'].queryset = ClientsDep.objects.filter(client=context["form"]['client'].data)
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        outsource_group = user.groups.filter(name='outsource').exists()
        if user.is_active and (user.is_superuser or not outsource_group):
            return super(OrderCreateView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)

    def form_valid(self, form):
        resp = super(OrderCreateView, self).form_valid(form)
        instance = self.object
        ord_action = DocOrderAction(doc_order=instance,
                                    manager_user=self.request.user,
                                    setting_user=self.request.user,
                                    executor_user=User.objects.get(pk=self.request.POST["executor"]),
                                    status=DirStatus.objects.get(status_name="Новый"),
                                    storage=Storage.objects.get(pk=self.request.POST["storage"]))
        ord_action.save()
        msg = "*{}* ДОБАВИЛ заказ -{}-{}-{}-".format(self.request.user.get_full_name(), instance.order_barcode, instance.client.client_name, instance.device_name)
        logger.info(msg)
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
        context["outsource"] = self.request.user.groups.filter(name='outsource').exists()
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_active:
            order = DocOrderHeader.objects.get(pk=self.kwargs["order_id"])
            if request.user.groups.filter(name='outsource').exists():
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
        if request.user.groups.filter(name='outsource').exists():
            self.form_class = ActionFormOut
        else:
            self.form_class = ActionForm
        order = DocOrderHeader.objects.get(pk=kwargs["order_id"])
        self.initial["manager_user"] = order.last_action().manager_user
        self.initial["storage"] = order.last_action().storage
        return super(ActionCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.success_url = reverse("repair:index")
        if request.user.groups.filter(name='outsource').exists():
            self.form_class = ActionFormOut
        else:
            self.form_class = ActionForm
        if not request.user.is_superuser and request.POST["status"] == "Архивный":
            return self.get(request, *args, **kwargs)
        return super(ActionCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.doc_order = DocOrderHeader.objects.get(pk=self.kwargs["order_id"])
        form.instance.setting_user = self.request.user
        if self.request.user.groups.filter(name='outsource').exists():
            last_act = DocOrderHeader.objects.get(pk=self.kwargs["order_id"]).last_action()
            form.instance.manager_user = last_act.manager_user
            form.instance.executor_user = last_act.executor_user
        msg = "*{}* ИЗМЕНИЛ статус заказа \"{}\"-->\"{}\". Заказ -{}-{}-{}-".format(
            self.request.user.get_full_name(), form.instance.doc_order.last_status(), form.instance.status,
            form.instance.doc_order.order_barcode, form.instance.doc_order.client.client_name, form.instance.doc_order.device_name)
        logger.info(msg)
        return super(ActionCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ActionCreateView, self).get_context_data(**kwargs)
        context["order"] = DocOrderHeader.objects.get(pk=self.kwargs["order_id"])
        context["outsource"] = self.request.user.groups.filter(name='outsource').exists()
        if not self.request.user.is_superuser:
            if context["outsource"]:
                context["form"].fields["status"].queryset = DirStatus.objects.exclude(status_name__in=["Архивный", "Передан клиенту"])
            else:
                context["form"].fields["status"].queryset = DirStatus.objects.exclude(status_name="Архивный")
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # outsource_group = request.user.groups.filter(name='outsource').exists()
        if not request.user.is_active:
            return redirect(LOGIN_URL)
        order = DocOrderHeader.objects.get(pk=self.kwargs["order_id"])
        if order.last_status() == "Архивный" and not request.user.is_superuser:
            return redirect("repair:order_detail", order_id=kwargs["order_id"])
        return super(ActionCreateView, self).dispatch(request, *args, **kwargs)


class ClientListView(ListView):
    template_name = "repair/client.html"
    model = Clients
    ordering = "client_name"
    context_object_name = "clients"


    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_active and not user.groups.filter(name='outsource').exists():
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
        msg = "*{}* ДОБАВИЛ клиента {}".format(self.request.user.get_full_name(), instance.client_name)
        logger.info(msg)
        messages.add_message(self.request, messages.SUCCESS, "Новый клиент добавлен!!!")
        return resp

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_active and not user.groups.filter(name='outsource').exists():
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
        if user.is_active and not user.groups.filter(name='outsource').exists():
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
        msg = "*{}* РЕДАКТИРОВАЛ клиента {}".format(self.request.user.get_full_name(), instance.client_name)
        logger.info(msg)
        return resp

    def get_context_data(self, **kwargs):
        context = super(ClientEditView, self).get_context_data(**kwargs)
        if self.object.client_corp:
            context["department"] = ClientsDep.objects.filter(client_id=self.object)
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_active and not user.groups.filter(name='outsource').exists():
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
                msg = "*{}* ДОБАВИЛ клиента {}".format(request.user.get_full_name(), newObject.client_name)
                logger.info(msg)
                return HttpResponse(
                    '<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                    (escape(newObject._get_pk_val()), escape(newObject)))
    else:
        form = addForm()
    pageContext = {'form': form, 'field': field}
    return render_to_response("repair/client_add_popup.html", pageContext)


@login_required
def popupClientView(request):
    user = request.user
    if user.is_active and not user.groups.filter(name='outsource').exists():
        return handlePopAdd(request, ClientForm, 'client')
    else:
        return redirect(LOGIN_URL)


#send department list if change a client (through ajax)
@login_required
def dep_update(request, **kwargs):
    user = request.user
    if user.is_active and not user.groups.filter(name='outsource').exists():
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


class OrderArchiveView(FilterView):
    filterset_class = DocOrderHeaderFilter
    template_name = "repair/order_archive.html"
    context_object_name = "filter"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='outsource').exists():
            orders = DocOrderHeader.objects.filter(docorderaction__executor_user=user).filter(docorderaction__status__status_name="Архивный").order_by('-id').distinct()
        else:
            orders = DocOrderHeader.objects.filter(docorderaction__status__status_name="Архивный").distinct()
        return orders

    def get_context_data(self, **kwargs):
        context = super(OrderArchiveView, self).get_context_data(**kwargs)
        if self.request.GET.get('all'):
            context['object_list'] = self.get_queryset()
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_active:
            return super(OrderArchiveView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)



@login_required
def ajax_add_service(request, order_id):
    try:
        order = DocOrderHeader.objects.get(pk=order_id)
        if order.last_status() == "Архивный" and not request.user.is_superuser:
            raise ObjectDoesNotExist("Access denied")
        if order.last_status() != "В работе":
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
            msg = "*{}* ДОБАВИЛ работу по заказу. Заказ -{}-{}-{}-".format(request.user.get_full_name(), order.order_barcode, order.client.client_name, order.device_name)
            logger.info(msg)
        else:
            form = render_to_string('repair/ajax/ajax_add_service_form.html',
                                    context={'service_form': service_form, 'order_id': order.id}, request=request)
            tr = "error"
        data = {"form": form, "tr": tr}
        return JsonResponse(data)
    return HttpResponseNotFound()


# del service through ajax
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
            msg = "*{}* УДАЛИЛ работу по заказу. Заказ -{}-{}-{}-".format(request.user.get_full_name(),
                                                                           order.order_barcode,
                                                                           order.client.client_name, order.device_name)
            logger.info(msg)
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
        if order.last_status() != "В работе":
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
            new_spare_form = SpareForm()
            form = render_to_string('repair/ajax/ajax_add_spare_form.html',
                                    context={'spare_form': new_spare_form, 'order_id': order.id}, request=request)
            tr = render_to_string('repair/ajax/ajax_add_spare_tr.html',
                                  context={'order_id': order.id, "spare": obj_spare}, request=request)
            msg = "*{}* ДОБАВИЛ запчасть по заказу. Заказ -{}-{}-{}-".format(request.user.get_full_name(),
                                                                           order.order_barcode,
                                                                           order.client.client_name, order.device_name)
            logger.info(msg)
        else:
            form = render_to_string('repair/ajax/ajax_add_spare_form.html',
                                    context={'spare_form': spare_form, 'order_id': order.id}, request=request)
            tr = "error"
        data = {"form": form, "tr": tr}
        return JsonResponse(data)
    return HttpResponseNotFound()


# del spare through ajax
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
            msg = "*{}* УДАЛИЛ запчасть по заказу. Заказ -{}-{}-{}-".format(request.user.get_full_name(),
                                                                             order.order_barcode,
                                                                             order.client.client_name,
                                                                             order.device_name)
            logger.info(msg)
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
            msg = "*{}* СМЕНИЛ ПАРОЛЬ".format(request.user.get_full_name())
            logger.info(msg)
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


# Assessment-view and Reward-view\change(through ajax)
class ServiceRewardAssessment(ListView):
    template_name = "repair/assessment.html"
    model = DocOrderServiceContent
    context_object_name = "services"

    def get_context_data(self, **kwargs):
        context = super(ServiceRewardAssessment, self).get_context_data(**kwargs)
        reward_queryset = Reward.objects.all()
        reward_form = RewardForm()
        context['rewards'] = reward_queryset
        context['reward_form'] = reward_form
        return context

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            act = request.POST.get("action")
            if act == "add":
                reward_form = RewardForm(request.POST)
                if reward_form.is_valid():
                    obj_reward = reward_form.save()
                    new_reward_form = RewardForm()
                    form = render_to_string('repair/ajax/ajax_add_reward_form.html',
                                            context={'reward_form': new_reward_form}, request=request)
                    tr = render_to_string('repair/ajax/ajax_add_reward_tr.html',
                                          context={"reward": obj_reward}, request=request)
                else:
                    form = render_to_string('repair/ajax/ajax_add_reward_form.html',
                                            context={'reward_form': reward_form}, request=request)
                    tr = "error"
                data = {"form": form, "tr": tr}
                return JsonResponse(data)
            if act == "delete":
                try:
                    obj_reward = Reward.objects.get(pk=request.POST.get("reward_id"))
                except ObjectDoesNotExist as msg:
                    return HttpResponseNotFound(msg)
                obj_reward.delete()
                data = {"reward_id": request.POST.get("reward_id")}
                return JsonResponse(data)
        else:
            return HttpResponseNotFound()

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_active:
            if request.user.is_superuser:
                return super(ServiceRewardAssessment, self).dispatch(request, *args, **kwargs)
            else:
                return redirect(reverse("repair:index"))
        else:
            return redirect(LOGIN_URL)


class CartridgeOrderListView(FilterView):
    filterset_class = CartridgeOrderFilter
    template_name = "repair/cartridge_orders.html"
    ordering = ["-order_datetime"]
    outsource = True

    def get_queryset(self):
        orders = CartridgeOrder.objects.exclude(cartridgeaction__status__status_name=6).order_by('-id').distinct()
        if self.outsource:
            user = self.request.user
            orders = orders.filter(cartridgeaction__executor_user=user)
        return orders

    def get_context_data(self, **kwargs):
        context = super(CartridgeOrderListView, self).get_context_data(**kwargs)
        context["outsource"] = self.outsource
        if self.request.GET.get('all'):
            context['object_list'] = self.get_queryset()
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        self.outsource = user.groups.filter(name='outsource').exists()
        if user.is_active:
            return super(CartridgeOrderListView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


class CartridgeMyOrderListView(ListView):
    template_name = "repair/cartridge_my_order.html"
    model = CartridgeOrder
    ordering = "-id"
    context_object_name = "orders"

    def get_queryset(self):
        user = self.request.user
        orders = CartridgeOrder.objects.filter(Q(cartridgeaction__manager_user=user)|Q(cartridgeaction__executor_user=user)).exclude(cartridgeaction__status__status_name=CartridgeActionStatus.ARCHIVE).distinct()
        return orders

    def get_context_data(self, **kwargs):
        context = super(CartridgeMyOrderListView, self).get_context_data(**kwargs)
        context["outsource"] = self.outsource
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.outsource = request.user.groups.filter(name='outsource').exists()
        if request.user.is_active:
            return super(CartridgeMyOrderListView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


class CartridgeListView(ListView):
    template_name = "repair/cartridges.html"
    model = Cartridge
    ordering = "add_datetime"
    context_object_name = "cartridges"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        outsource_group = request.user.groups.filter(name='outsource').exists()
        if user.is_active and not outsource_group:
            return super(CartridgeListView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


class CartridgeCreateView(CreateView):
    form_class = CartridgeCreateForm
    model = Cartridge
    template_name = 'repair/cartridge_create.html'
    success_url = reverse_lazy('repair:cartridges')


    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        outsource_group = request.user.groups.filter(name='outsource').exists()
        if user.is_active and not outsource_group:
            return super(CartridgeCreateView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


class CartridgeOrderCreateView(CreateView):
    form_class = CartridgeOrderForm
    model = CartridgeOrder
    template_name = "repair/cartridge_order_add.html"

    def get_context_data(self, **kwargs):
        context = super(CartridgeOrderCreateView, self).get_context_data(**kwargs)
        context['form'].fields['cartridge'].queryset = Cartridge.objects.none()
        context['filter_form'] = CartridgeFilterOrderForm()
        return context

    def post(self, request, *args, **kwargs):
        self.success_url = reverse('repair:cartridge_orders')
        return super(CartridgeOrderCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        resp = super(CartridgeOrderCreateView, self).form_valid(form)
        instance = self.object
        ord_action = CartridgeAction(order=instance,
                                    manager_user=self.request.user,
                                    setting_user=self.request.user,
                                    executor_user=User.objects.get(pk=self.request.POST["executor"]),
                                    status=CartridgeActionStatus.objects.get(status_name=0),
                                    action_content='Заказ принят')
        ord_action.save()
        msg = "*{}* ДОБАВИЛ заказ КАРТРИДЖ -{}-{}-".format(self.request.user.get_full_name(), instance.id, instance.cartridge.client.client_name)
        logger.info(msg)
        messages.add_message(self.request, messages.SUCCESS, "Новый заказ на КАРТРИДЖ добавлен!!!")
        return resp

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        outsource_group = request.user.groups.filter(name='outsource').exists()
        if user.is_active and not outsource_group:
            return super(CartridgeOrderCreateView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


class CartridgeOrderDetailView(DetailView):
    template_name = "repair/cartridge_order_detail.html"
    model = CartridgeOrder
    context_object_name = "order"
    pk_url_kwarg = "order_id"
    outsource = True
    status_map = {0:[1,],
                  1:[3,],
                  3:[1, 5,],
                  5:[1, 6,],
                  }

    def get_action_formset(self):
        status = self.object.last_action().status.status_name
        form_set = []
        if self.status_map.get(status):
            form_set = [CartridgeActionExpressForm(status_set=self.status_map[status], initial={'status':CartridgeActionStatus.objects.get(status_name=st)}) for st in self.status_map[status]]
        return form_set


    def get_context_data(self, **kwargs):
        context = super(CartridgeOrderDetailView, self).get_context_data(**kwargs)
        context['order_action'] = CartridgeAction.objects.filter(order=self.object).order_by("action_datetime")
        context['outsource'] = self.outsource
        context['action_formset'] = self.get_action_formset()
        context['spare_form'] = CartridgeSpareForm()
        context['service_form'] = CartridgeServiceForm()
        context['spares'] = CartridgeOrderSparesContent.objects.filter(order=self.object)
        context['services'] = CartridgeOrderServiceContent.objects.filter(order=self.object)
        return context

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        action = order.last_action()
        if self.status_map.get(action.status.status_name):
            form_action = CartridgeActionExpressForm(request.POST, status_set = self.status_map[action.status.status_name])
            if form_action.is_valid():
                new_action = form_action.save(commit=False)
                new_action.order = order
                new_action.manager_user = action.manager_user
                new_action.executor_user = action.executor_user
                new_action.setting_user = request.user
                new_action.action_content = 'Быстрая установка статуса'
                new_action.save()
        return super(CartridgeOrderDetailView, self).get(request, *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_active:
            order = CartridgeOrder.objects.get(pk=self.kwargs["order_id"])
            self.outsource = request.user.groups.filter(name='outsource').exists()
            if self.outsource:
                act = CartridgeAction.objects.filter(order=order).filter(executor_user=request.user).values_list('action_datetime', flat=True)
                if not act:
                    return redirect("repair:cartridge_orders")
            return super(CartridgeOrderDetailView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


@login_required
def cartridge_add_spare(request, order_id):
    try:
        order = CartridgeOrder.objects.get(pk=order_id)
        if order.last_status() == 'Архивный' and not request.user.is_superuser:
            raise ObjectDoesNotExist("Access denied")
        if order.last_status() != 'В работе':
            raise ObjectDoesNotExist("Access denied")
    except ObjectDoesNotExist as msg:
        return HttpResponseNotFound(msg)
    if request.method == "POST" and request.is_ajax():
        spare_form = CartridgeSpareForm(request.POST)
        if spare_form.is_valid():
            obj_spare = spare_form.save(commit=False)
            obj_spare.order = order
            obj_spare.setting_user = request.user
            obj_spare.save()
            new_spare_form = CartridgeSpareForm()
            form = render_to_string('repair/ajax/cartridge_add_spare_form.html',
                                    context={'spare_form': new_spare_form, 'order_id': order_id}, request=request)
            tr = render_to_string('repair/ajax/cartridge_add_spare_tr.html',
                                  context={'order_id': order_id, "spare": obj_spare}, request=request)
            msg = "*{}* ДОБАВИЛ запчасть по заказу КАРТРИДЖ. Заказ -{}-{}-{}-".format(request.user.get_full_name(),
                                                                           order.id,
                                                                           order.cartridge.client.client_name, order.cartridge.model)
            logger.info(msg)
        else:
            form = render_to_string('repair/ajax/cartridge_add_spare_form.html',
                                    context={'spare_form': spare_form, 'order_id': order.id}, request=request)
            tr = "error"
        data = {"form": form, "tr": tr}
        return JsonResponse(data)
    return HttpResponseNotFound()


@login_required
def cartridge_del_spare(request):
    data = {"error": 1}
    if request.method == "POST" and request.is_ajax():
        try:
            order = CartridgeOrder.objects.get(pk=request.POST.get("order_id"))
            spare = CartridgeOrderSparesContent.objects.get(pk=request.POST["spare_id"])
            if order.last_status() == 'Архивный' and not request.user.is_superuser:
                raise ObjectDoesNotExist("Access denied")
        except ObjectDoesNotExist as msg:
            data = {'error': msg}
            return JsonResponse(data)
        if spare in order.cartridgeordersparescontent_set.all():
            spare.delete()
            data = {"error": 0}
            msg = "*{}* УДАЛИЛ запчасть по заказу КАРТРИДЖ. Заказ -{}-{}-{}-".format(request.user.get_full_name(), order.id,
                                                                                     order.cartridge.client.client_name, order.cartridge.model)
            logger.info(msg)
        return JsonResponse(data)
    return redirect("repair:order_detail", order_id=request.POST.get("order_id"))


@login_required
def cartridge_add_service(request, order_id):
    try:
        order = CartridgeOrder.objects.get(pk=order_id)
        if order.last_status() == 'Архивный' and not request.user.is_superuser:
            raise ObjectDoesNotExist("Access denied")
        if order.last_status() != 'В работе':
            raise ObjectDoesNotExist("Access denied")
    except ObjectDoesNotExist as msg:
        return HttpResponseNotFound(msg)
    if request.method == "POST" and request.is_ajax():
        service_form = CartridgeServiceForm(request.POST)
        if service_form.is_valid():
            obj_service = service_form.save(commit=False)
            obj_service.order = order
            obj_service.setting_user = request.user
            obj_service.save()
            new_service_form = CartridgeServiceForm()
            form = render_to_string('repair/ajax/cartridge_add_service_form.html',
                                    context={'service_form': new_service_form, 'order_id': order_id}, request=request)
            tr = render_to_string('repair/ajax/cartridge_add_service_tr.html',
                                  context={'order_id': order_id, "service": obj_service}, request=request)
            msg = "*{}* ДОБАВИЛ работы по заказу КАРТРИДЖ. Заказ -{}-{}-{}-".format(request.user.get_full_name(),
                                                                           order.id,
                                                                           order.cartridge.client.client_name, order.cartridge.model)
            logger.info(msg)
        else:
            form = render_to_string('repair/ajax/cartridge_add_service_form.html',
                                    context={'service_form': service_form, 'order_id': order.id}, request=request)
            tr = "error"
        data = {"form": form, "tr": tr}
        return JsonResponse(data)
    return HttpResponseNotFound()


@login_required
def cartridge_del_service(request):
    data = {"error": 1}
    if request.method == "POST" and request.is_ajax():
        try:
            order = CartridgeOrder.objects.get(pk=request.POST.get("order_id"))
            service = CartridgeOrderServiceContent.objects.get(pk=request.POST["service_id"])
            if order.last_status() == 'Архивный' and not request.user.is_superuser:
                raise ObjectDoesNotExist("Access denied")
        except ObjectDoesNotExist as msg:
            data = {'error': msg}
            return JsonResponse(data)
        if service in order.cartridgeorderservicecontent_set.all():
            service.delete()
            data = {"error": 0}
            msg = "*{}* УДАЛИЛ работы по заказу КАРТРИДЖ. Заказ -{}-{}-{}-".format(request.user.get_full_name(), order.id,
                                                                                     order.cartridge.client.client_name, order.cartridge.model)
            logger.info(msg)
        return JsonResponse(data)
    return redirect("repair:cartridge_order_detail", order_id=request.POST.get("order_id"))


# Update through ajax
@login_required
def cartridge_update(request, **kwargs):
    if not request.is_ajax():
        return redirect(LOGIN_URL)
    user = request.user
    outsource_group = request.user.groups.filter(name='outsource').exists()
    cartridge_preset = {'cartridge': [{'id': '', 'model': '--------', 'serial_number': '--------', 'client__client_name': '--------'}], 'redirect': ''}
    if user.is_active and not outsource_group:
        filter_form = CartridgeFilterOrderForm(request.POST)
        if filter_form.is_valid():
            cartridge_set = Cartridge.objects.filter(serial_number__contains=filter_form.cleaned_data['serial_number'])
            if filter_form.cleaned_data['client']:
                cartridge_set = cartridge_set.filter(client=filter_form.cleaned_data['client'])
            if cartridge_set:
                cartridge_preset['cartridge'].extend(cartridge_set.values('id', 'model','serial_number', 'client__client_name'))
    else:
        cartridge_preset['redirect'] = reverse('login')
    return JsonResponse(cartridge_preset, safe=False)



class CartridgeActionCreateView(CreateView):

    model = CartridgeAction
    template_name = 'repair/cartridge_action_add.html'

    def get(self, request, *args, **kwargs):
        if self.outsource_group:
            self.form_class = CartridgeRegularActionForm
        else:
            self.form_class = CartridgeSuperActionForm
        last_action = self.order.cartridgeaction_set.latest()
        self.initial['manager_user'] = last_action.manager_user
        self.initial['executor_user'] = last_action.executor_user
        self.initial['status'] = last_action.status
        return super(CartridgeActionCreateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CartridgeActionCreateView, self).get_context_data(**kwargs)
        context['current_action'] = CartridgeAction.objects.filter(order__id=self.kwargs['order_id']).latest()
        context['order'] = CartridgeOrder.objects.get(pk=self.kwargs['order_id'])
        return context

    def post(self, request, *args, **kwargs):
        if self.outsource_group:
            self.form_class = CartridgeRegularActionForm
        else:
            self.form_class = CartridgeSuperActionForm
        self.success_url = reverse("repair:cartridge_order_detail", kwargs={'order_id': self.kwargs['order_id']})
        return super(CartridgeActionCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.order_id = self.kwargs['order_id']
        return super(CartridgeActionCreateView, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.outsource_group = request.user.groups.filter(name='outsource').exists()
        if not request.user.is_active:
            return redirect(LOGIN_URL)
        self.order = CartridgeOrder.objects.get(pk=self.kwargs["order_id"])
        if self.order.last_status() == "Архивный" and not request.user.is_superuser:
            return redirect("repair:cartridge_order_detail", order_id=kwargs["order_id"])
        return super(CartridgeActionCreateView, self).dispatch(request, *args, **kwargs)



class CartridgeOrderArchiveView(FilterView):
    filterset_class = CartridgeOrderFilter
    template_name = "repair/cartridge_order_archive.html"
    outsource = True

    def get_queryset(self):
        user = self.request.user
        orders = CartridgeOrder.objects.filter(cartridgeaction__status__status_name=6).order_by('-id').distinct()
        if self.outsource:
            orders = orders.filter(cartridgeaction__executor_user=user)
        return orders

    def get_context_data(self, **kwargs):
        context = super(CartridgeOrderArchiveView, self).get_context_data(**kwargs)
        context['outsource'] = self.outsource
        if self.request.GET.get('all'):
            context['object_list'] = self.get_queryset()
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.outsource = request.user.groups.filter(name='outsource').exists()
        if request.user.is_active:
            return super(CartridgeOrderArchiveView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)



class MaintenanceOrderCreateView(CreateView):
    form_class = MaintenanceOrderForm
    model = MaintenanceOrder
    template_name = "repair/maintenance_order_add.html"

    def post(self, request, *args, **kwargs):
        self.success_url = reverse("repair:maintenance_order_list")
        return super(MaintenanceOrderCreateView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MaintenanceOrderCreateView, self).get_context_data(**kwargs)
        context["form"].fields['client_dep'].queryset = ClientsDep.objects.none()
        if context["form"]['client'].data:
            context["form"].fields['client_dep'].queryset = ClientsDep.objects.filter(client=context["form"]['client'].data)
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        outsource_group = request.user.groups.filter(name='outsource').exists()
        if user.is_active and (user.is_superuser or not outsource_group):
            return super(MaintenanceOrderCreateView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)

    def form_valid(self, form):
        resp = super(MaintenanceOrderCreateView, self).form_valid(form)
        instance = self.object
        ord_action = MaintenanceAction(order=instance,
                                    manager_user=self.request.user,
                                    setting_user=self.request.user,
                                    executor_user=User.objects.get(pk=self.request.POST["executor"]),
                                    status=MaintenanceActionStatus.objects.get(status_name=0))
        ord_action.save()
        msg = "*{}* ДОБАВИЛ заказ РАБОТЫ -{}-{}-".format(self.request.user.get_full_name(), instance.id, instance.client.client_name)
        logger.info(msg)
        messages.add_message(self.request, messages.SUCCESS, "Новый заказ РАБОТЫ добавлен!!!")
        return resp


class MaintenanceOrderListView(ListView):
    template_name = "repair/maintenance_order_list.html"
    model = MaintenanceOrder
    ordering = "order_datetime"
    context_object_name = "orders"

    def get_queryset(self):
        user = self.request.user
        orders = MaintenanceOrder.objects.filter(Q(maintenanceaction__manager_user=user)|Q(maintenanceaction__executor_user=user)).exclude(maintenanceaction__status__status_name=MaintenanceActionStatus.ARCHIVE).distinct()
        return orders

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        outsource_group = request.user.groups.filter(name='outsource').exists()
        if user.is_active and not outsource_group:
            return super(MaintenanceOrderListView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


class MaintenanceMyOrderListView(ListView):
    template_name = "repair/maintenance_my_order.html"
    model = MaintenanceOrder
    ordering = "-id"
    context_object_name = "orders"

    def get_queryset(self):
        user = self.request.user
        orders = MaintenanceOrder.objects.filter(Q(maintenanceaction__manager_user=user)|Q(maintenanceaction__executor_user=user)).exclude(maintenanceaction__status__status_name=MaintenanceActionStatus.ARCHIVE).distinct()
        return orders

    def get_context_data(self, **kwargs):
        context = super(MaintenanceMyOrderListView, self).get_context_data(**kwargs)
        context["outsource"] = self.outsource
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.outsource = request.user.groups.filter(name='outsource').exists()
        if request.user.is_active and not self.outsource:
            return super(MaintenanceMyOrderListView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


class MaintenanceOrderDetailView(DetailView):
    template_name = "repair/maintenance_detail.html"
    model = MaintenanceOrder
    context_object_name = "order"
    pk_url_kwarg = "order_id"

    def get_context_data(self, **kwargs):
        context = super(MaintenanceOrderDetailView, self).get_context_data(**kwargs)
        context["order_action"] = MaintenanceAction.objects.filter(order=self.object).order_by("action_datetime")
        context["outsource"] = self.outsource_group
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_active:
            order = MaintenanceOrder.objects.get(pk=self.kwargs["order_id"])
            self.outsource_group = request.user.groups.filter(name='outsource').exists()
            if self.outsource_group:
                act = MaintenanceAction.objects.filter(order=order).filter(executor_user=request.user).values_list('action_datetime', flat=True)
                if not act:
                    return redirect("repair:maintenance_order_list")
            return super(MaintenanceOrderDetailView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)


class MaintenanceActionCreateView(CreateView):
    # form_class = MaintenanceRegularActionForm
    model = MaintenanceAction
    template_name = 'repair/maintenance_action_add.html'

    def get(self, request, *args, **kwargs):
        if self.outsource_group:
            self.form_class = MaintenanceRegularActionForm
        else:
            self.form_class = MaintenanceSuperActionForm
        # last_action = MaintenanceOrder.objects.get(pk=kwargs["order_id"]).maintenanceaction_set.latest()
        last_action = self.order.maintenanceaction_set.latest()
        self.initial['manager_user'] = last_action.manager_user
        self.initial['executor_user'] = last_action.executor_user
        self.initial['status'] = last_action.status
        return super(MaintenanceActionCreateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MaintenanceActionCreateView, self).get_context_data(**kwargs)
        context['current_action'] = MaintenanceAction.objects.filter(order__id=self.kwargs['order_id']).latest()
        context['order'] = MaintenanceOrder.objects.get(pk=self.kwargs['order_id'])
        return context

    def post(self, request, *args, **kwargs):
        if self.outsource_group:
            self.form_class = MaintenanceRegularActionForm
        else:
            self.form_class = MaintenanceSuperActionForm
        self.success_url = reverse("repair:maintenance_detail", kwargs={'order_id': self.kwargs['order_id']})
        return super(MaintenanceActionCreateView, self).post(request, *args, **kwargs)


    def form_valid(self, form):
        form.instance.order_id = self.kwargs['order_id']
        return super(MaintenanceActionCreateView, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.outsource_group = request.user.groups.filter(name='outsource').exists()
        if not request.user.is_active:
            return redirect(LOGIN_URL)
        self.order = MaintenanceOrder.objects.get(pk=self.kwargs["order_id"])
        if self.order.last_status() == "Архивный" and not request.user.is_superuser:
            return redirect("repair:maintenance_detail", order_id=kwargs["order_id"])
        return super(MaintenanceActionCreateView, self).dispatch(request, *args, **kwargs)


class MaintenanceOrderArchiveView(FilterView):
    filterset_class = MaintenanceOrderFilter
    template_name = "repair/maintenance_order_archive.html"
    outsource = True

    def get_queryset(self):
        user = self.request.user
        orders = MaintenanceOrder.objects.filter(maintenanceaction__status__status_name=MaintenanceActionStatus.ARCHIVE).order_by('-id').distinct()
        if self.outsource:
            orders = orders.filter(maintenanceaction__executor_user=user)
        return orders

    def get_context_data(self, **kwargs):
        context = super(MaintenanceOrderArchiveView, self).get_context_data(**kwargs)
        context['outsource'] = self.outsource
        if self.request.GET.get('all'):
            context['object_list'] = self.get_queryset()
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.outsource = request.user.groups.filter(name='outsource').exists()
        if request.user.is_active:
            return super(MaintenanceOrderArchiveView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect(LOGIN_URL)