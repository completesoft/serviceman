from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone


class Clients(models.Model):
    client_name = models.CharField("Имя клиента", max_length=100, default='', null=False, blank=False)
    client_contact = models.CharField("Контакты клиента", max_length=100, default='', null=False, blank=False)
    client_corp = models.BooleanField("Корпоративность клиента", null=False, blank=False, default=False)

    class Meta:
        db_table = 'clients'
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return '{}'.format(self.client_name)

class DocOrderHeader (models.Model):
    order_barcode = models.CharField("Штрихкод", max_length=100, default='', unique=True, null=False, blank=False)
    order_datetime = models.DateTimeField("Дата", auto_now_add=True)
    client = models.ForeignKey(Clients, verbose_name="Клиент", on_delete=models.SET_NULL, null=True, blank=False)
    client_dep = models.ForeignKey('ClientsDep', verbose_name="Отделение клиента", null=True, blank=True)
    client_position = models.CharField("Размещение у клиента", max_length=100, default='', null=False, blank=False)
    device_name = models.CharField("Наименование устройства", default='',max_length=100, null=False, blank=False)
    device_defect = models.CharField("Заявленная неисправность", default='', max_length=155, null=False, blank=False)
    device_serial = models.CharField("Серийный номер устройства", default='', max_length=100, null=False, blank=False)
    order_comment = models.CharField("Комментарий", max_length=255, null=True, blank=True)


    class Meta:
        db_table = 'doc_order_header'
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return "{} ИД заказа {}".format(self.order_datetime, self.id)

    def last_action(self):
        acts = self.docorderaction_set.all().latest()
        return acts

    def last_status(self):
        acts = self.docorderaction_set.all().latest()
        return acts.status.status_name
    last_status.short_description = 'Статус заказа'

    def client_corp(self):
        return self.client.client_corp
    client_corp.short_description = "Корп. клиент"
    client_corp.boolean = True

    def status_expired(self):
        acts = self.docorderaction_set.all().latest()
        delta = acts.status.expiry_time
        if not delta:
            return False
        last_time = acts.action_datetime + timedelta(hours=delta)
        return timezone.now() > last_time
    status_expired.boolean = True


class DirStatus(models.Model):

    # status_set = (
    #     ('Новый', 'Новый'),
    #     ('В работе', 'В работе'),
    #     ('Ожидание', 'Ожидание'),
    #     ('Выполнен', 'Выполнен'),
    #     ('Просрочен', 'Просрочен'),
    #     ('Передан клиенту', 'Передан клиенту')
    # )

    status_name = models.CharField("Состояние", max_length=100, null=False, blank=False)
    expiry_time = models.PositiveIntegerField('Допустимая продолжительность статуса', help_text='в часах', default=0)

    class Meta:
        db_table = 'dir_status'
        verbose_name = "Справочник состояний (fixturizable+Group)"
        verbose_name_plural = "Справочник состояний (fixturizable+Group)"

    def __str__(self):
        return "{}".format(self.status_name)


class Storage(models.Model):

    title = models.CharField('Название склада', max_length=30, null=False, blank=False)

    class Meta:
        verbose_name = "Справочник СКЛАДОВ"
        verbose_name_plural = "Справочник СКЛАДОВ"

    def __str__(self):
        return "{}".format(self.title)


class DocOrderAction(models.Model):

    doc_order = models.ForeignKey(DocOrderHeader, on_delete=models.CASCADE, null=True, blank=False)
    action_datetime = models.DateTimeField("Дата операции", auto_now_add=True)
    manager_user = models.ForeignKey(User, verbose_name="Руководитель заказа", on_delete=models.SET_NULL, null=True, blank=False)
    executor_user = models.ForeignKey(User,verbose_name="Исполнитель заказа", related_name='+',on_delete=models.SET_NULL, null=True, blank=False)
    setting_user = models.ForeignKey(User,verbose_name="Установил статус заказа", related_name='+',on_delete=models.SET_NULL, null=True, blank=False)
    status = models.ForeignKey(DirStatus, verbose_name="Статус заказа", on_delete=models.SET_NULL, null=True, blank=False)
    action_comment = models.TextField("Комментарий операции", max_length=100, default="", null=True, blank=True)
    storage = models.ForeignKey(Storage, verbose_name='Склад', on_delete=models.SET_NULL, null=True, blank=False)

    class Meta:
        db_table = 'doc_order_action'
        verbose_name = "Состояние заказа"
        verbose_name_plural = "Состояние заказа"
        get_latest_by = "action_datetime"

    def __str__(self):
        return "{}, {}, {}".format(self.doc_order_id, self.status_id, self.action_datetime)



class DocOrderServiceContent(models.Model):

    add_datetime = models.DateTimeField("Дата операции", auto_now_add=True)
    order = models.ForeignKey(DocOrderHeader, on_delete=models.CASCADE, null=False, blank=False)
    service_name = models.TextField("Наименование работ", max_length=255, null=False, blank=False)
    service_qty = models.PositiveIntegerField("Кол-во", default=1, null=False, blank=False)
    cost = models.PositiveIntegerField("Стоимость 1 шт", default=0, null=True, blank=False)
    setting_user = models.ForeignKey(User, verbose_name="Добавил выполненую работу", on_delete=models.SET_NULL, null=True, blank=False)

    class Meta:
        db_table = 'doc_order_service_content'
        verbose_name = "Выполненные работы"
        verbose_name_plural = "Выполненные работы"


class DocOrderSparesContent (models.Model):

    add_datetime = models.DateTimeField("Дата операции", auto_now_add=True)
    order = models.ForeignKey(DocOrderHeader, on_delete=models.CASCADE, null=False, blank=False)
    spare_name = models.CharField("Наименование запчасти", max_length=255, default="", null=False, blank=False)
    spare_serial = models.CharField("Серийный № запчасти", max_length=100, default="", null=False, blank=False)
    spares_qty = models.PositiveIntegerField("Кол-во", default=1, null=False, blank=False)
    setting_user = models.ForeignKey(User, verbose_name="Установил статус заказа", on_delete=models.SET_NULL, null=True, blank=False)

    class Meta():
        db_table = 'doc_order_spares_content'
        verbose_name = "Использованные запчасти"
        verbose_name_plural = "Использованные запчасти"


class ClientsDep(models.Model):

    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    client_dep_name = models.CharField("Подразделение клиента", max_length=100, default="", null=False, blank=False)

    class Meta:
        db_table = 'clients_dep'
        verbose_name = "Подразделения клиента"
        verbose_name_plural = "Подразделения клиентов"

    def __str__(self):
        return "{} - {}".format(self.client.client_name, self.client_dep_name)


class Images(models.Model):

    image = models.BinaryField ("Изображение устройства", null=True, blank=True)
    doc_order = models.ForeignKey(DocOrderHeader, on_delete=models.CASCADE)
    image_comment = models.CharField("Комментарий", max_length=255, default="", null=True, blank=True)

    class Meta:
        db_table = 'images'
        verbose_name = "Фотография устройства"
        verbose_name_plural = "Фотографии устройства"


class Reward(models.Model):

    add_datetime = models.DateField("Дата записи", blank=True, default=datetime.now, null=False)
    serviceman = models.ForeignKey(User, verbose_name="Мастер", on_delete=models.PROTECT, null=False, blank=False)
    amount = models.DecimalField(verbose_name="Сумма", max_digits=6, decimal_places=2, default=0, null=False, blank=False)

    class Meta:
        db_table = 'reward'
        verbose_name = 'Выплаты'
        verbose_name_plural = 'Выплаты'


    def __str__(self):
        return "{} получатель \"{}\"".format(self.add_datetime, self.serviceman)
