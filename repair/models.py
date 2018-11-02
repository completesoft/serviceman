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
        ordering = ['client_name']

    def __str__(self):
        return '{}'.format(self.client_name)


class DocOrderHeader(models.Model):
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
        verbose_name = "Ремонты - заказы"
        verbose_name_plural = "Ремонты - заказы"

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

        # acts = self.docorderaction_set.all().latest()
        acts = self.docorderaction_set.latest()
        if not acts.status.expiry_time:
            return False

        to_date = acts.action_datetime + timedelta(hours=acts.status.expiry_time)
        last_date = acts.action_datetime + timedelta(hours=acts.status.expiry_time)

        for x in range((to_date - acts.action_datetime).days + 1):
            if (to_date + timedelta(days=x)).weekday() in [5, 6]:
                last_date += timedelta(days=1)
                if last_date.weekday() in [5, 6]:
                    last_date += timedelta(days=1)
        return timezone.now() > last_date
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
        verbose_name = "Справочник состояний РЕМОНТЫ"
        verbose_name_plural = "Справочник состояний РЕМОНТЫ"

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
        verbose_name = "Ремонты - статусы заказов"
        verbose_name_plural = "Ремонты - статусы заказов"
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
        verbose_name = "Ремонты - выполненные работы"
        verbose_name_plural = "Ремонты - выполненные работы"


class DocOrderSparesContent(models.Model):

    add_datetime = models.DateTimeField("Дата операции", auto_now_add=True)
    order = models.ForeignKey(DocOrderHeader, on_delete=models.CASCADE, null=False, blank=False)
    spare_name = models.CharField("Наименование запчасти", max_length=255, default="", null=False, blank=False)
    spare_serial = models.CharField("Серийный № запчасти", max_length=100, default="", null=False, blank=False)
    spares_qty = models.PositiveIntegerField("Кол-во", default=1, null=False, blank=False)
    setting_user = models.ForeignKey(User, verbose_name="Установил статус заказа", on_delete=models.SET_NULL, null=True, blank=False)

    class Meta():
        db_table = 'doc_order_spares_content'
        verbose_name = "Ремонты - использованные запчасти"
        verbose_name_plural = "Ремонты - использованные запчасти"


class ClientsDep(models.Model):

    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    client_dep_name = models.CharField("Подразделение клиента", max_length=100, default="", null=False, blank=False)

    class Meta:
        db_table = 'clients_dep'
        verbose_name = "Подразделения клиента"
        verbose_name_plural = "Подразделения клиентов"
        ordering = ['client_dep_name']

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
        verbose_name = 'Ремонты - выплаты'
        verbose_name_plural = 'Ремонты - выплаты'


    def __str__(self):
        return "{} получатель \"{}\"".format(self.add_datetime, self.serviceman)


class Cartridge(models.Model):

    add_datetime = models.DateTimeField("Дата регистрации в базе", auto_now_add=True)
    model = models.CharField('Модель', max_length=100, null=False, blank=False)
    serial_number = models.CharField('Модель', max_length=100, null=False, blank=False, unique=True)
    client = models.ForeignKey(Clients, verbose_name="Клиент", on_delete=models.SET_DEFAULT, default='None', null=False, blank=False)
    client_position = models.CharField("Размещение у клиента", max_length=100, default='', null=False, blank=True)

    class Meta:
        db_table = 'cartridge'
        verbose_name = 'Картриджи'
        verbose_name_plural = 'Картриджи'

    def __str__(self):
        return 'Model:{} S.n.-{}'.format(self.model, self.serial_number)


class CartridgeActionStatus(models.Model):
    NEW = 0
    IN_WORK = 1
    WAITING = 2
    COMPLETED = 3
    EXPIRED = 4
    TO_CLIENT = 5
    ARCHIVE = 6

    status_set = (
        (NEW, 'Новый'),
        (IN_WORK, 'В работе'),
        (WAITING, 'Ожидание'),
        (COMPLETED, 'Выполнен'),
        (EXPIRED, 'Просрочен'),
        (TO_CLIENT, 'Передан клиенту'),
        (ARCHIVE, 'Архивный')
    )

    status_name = models.PositiveIntegerField("Состояние", choices=status_set, unique=True, null=False, blank=False, default=0)
    expiry_time = models.PositiveIntegerField('Допустимая продолжительность статуса', help_text='в часах', default=0)

    class Meta:
        db_table = 'cartridge_action_status'
        verbose_name = "Справочник состояний КАРТРИДЖИ"
        verbose_name_plural = "Справочник состояний КАРТРИДЖИ"

    def __str__(self):
        return "{}".format(self.get_status_name_display())



class CartridgeOrder(models.Model):

    order_datetime = models.DateTimeField("Дата заказа", auto_now_add=True)
    cartridge = models.ForeignKey(Cartridge, verbose_name='Картридж', on_delete=models.CASCADE, null=False, blank=False)
    defect = models.CharField("Заявленная неисправность", default='', max_length=255, null=False, blank=False)
    client_position = models.CharField("Размещение у клиента", max_length=100, default='', null=False, blank=False)

    class Meta:
        db_table = 'cartridge_order'
        verbose_name = "Картриджи - заказы"
        verbose_name_plural = "Картриджи - заказы"

    def __str__(self):
        return "{} {}".format(self.order_datetime, self.cartridge)

    def last_action(self):
        acts = self.cartridgeaction_set.all().latest()
        return acts

    def last_status(self):
        return self.cartridgeaction_set.all().latest().status.get_status_name_display()
    last_status.short_description = 'Статус заказа'

    def status_expired(self):
        acts = self.cartridgeaction_set.all().latest()
        if not acts.status.expiry_time:
            return False

        to_date = acts.action_datetime + timedelta(hours=acts.status.expiry_time)
        last_date = acts.action_datetime + timedelta(hours=acts.status.expiry_time)

        for x in range((to_date - acts.action_datetime).days + 1):
            if (to_date + timedelta(days=x)).weekday() in [5, 6]:
                last_date += timedelta(days=1)
                if last_date.weekday() in [5, 6]:
                    last_date += timedelta(days=1)
        return timezone.now() > last_date
    status_expired.boolean = True



class CartridgeAction(models.Model):

    order = models.ForeignKey(CartridgeOrder, on_delete=models.CASCADE, null=True, blank=False)
    action_datetime = models.DateTimeField("Дата операции", auto_now_add=True)
    manager_user = models.ForeignKey(User, verbose_name="Руководитель заказа", on_delete=models.SET_NULL, null=True, blank=False)
    executor_user = models.ForeignKey(User,verbose_name="Исполнитель заказа", related_name='+',on_delete=models.SET_NULL, null=True, blank=False)
    setting_user = models.ForeignKey(User,verbose_name="Установил статус заказа", related_name='+',on_delete=models.SET_NULL, null=True, blank=False)
    status = models.ForeignKey(CartridgeActionStatus, verbose_name="Статус заказа", on_delete=models.SET_NULL, null=True, blank=False)
    action_content = models.TextField("Комментарии", max_length=100, default="", null=True, blank=True)

    class Meta:
        db_table = 'cartridge_action'
        verbose_name = "Картриджи - статусы заказов"
        verbose_name_plural = "Картриджи - статусы заказов"
        get_latest_by = "action_datetime"


class CartridgeOrderServiceContent(models.Model):

    add_datetime = models.DateTimeField("Дата операции", auto_now_add=True)
    order = models.ForeignKey(CartridgeOrder, on_delete=models.CASCADE, null=False, blank=False)
    service_name = models.TextField("Вид работ", max_length=255, null=False, blank=False)
    service_qty = models.PositiveIntegerField("Кол-во", default=1, null=False, blank=False)
    cost = models.PositiveIntegerField("Стоимость 1 шт", default=0, null=True, blank=False)
    setting_user = models.ForeignKey(User, verbose_name="Добавил выполненую работу", on_delete=models.SET_NULL, null=True, blank=False)

    class Meta:
        verbose_name = "Картриджи - выполненные работы"
        verbose_name_plural = "Картриджи - выполненные работы"


class CartridgeServiceType(models.Model):

    FILL = 0
    REPAIR = 1
    OTHER = 2

    service_set = (
        (FILL, 'Заправка'),
        (REPAIR, 'Ремонт'),
        (OTHER, 'Прочее'),
    )

    service_type = models.PositiveIntegerField("Вид работ", choices=service_set, unique=True, null=False, blank=False)

    class Meta:
        verbose_name = "Картриджи - виды работы"
        verbose_name_plural = "Картриджи - виды работы"

class CartridgeOrderSparesContent(models.Model):

    add_datetime = models.DateTimeField("Дата операции", auto_now_add=True)
    order = models.ForeignKey(CartridgeOrder, on_delete=models.CASCADE, null=False, blank=False)
    spare_name = models.CharField("Наименование запчасти", max_length=255, default="", null=False, blank=False)
    spare_serial = models.CharField("Серийный № запчасти", max_length=100, default="", null=False, blank=False)
    spares_qty = models.PositiveIntegerField("Кол-во", default=1, null=False, blank=False)
    setting_user = models.ForeignKey(User, verbose_name="Установил статус заказа", on_delete=models.SET_NULL, null=True, blank=False)

    class Meta():
        verbose_name = "Картриджи - использованые запчасти"
        verbose_name_plural = "Картриджи - использованые запчасти"


class MaintenanceOrder(models.Model):
    order_datetime = models.DateTimeField("Дата", auto_now_add=True)
    client = models.ForeignKey(Clients, verbose_name="Клиент", on_delete=models.SET_NULL, null=True, blank=False)
    client_dep = models.ForeignKey('ClientsDep', verbose_name="Отделение клиента", null=True, blank=True)
    client_position = models.CharField("Размещение у клиента", max_length=100, default='', null=False, blank=False)
    list_of_jobs = models.CharField("Список работ", default='', max_length=250, null=False, blank=False)
    order_comment = models.CharField("Комментарий", max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'maintenance_order'
        verbose_name = "Работы - заказы"
        verbose_name_plural = "Работы - заказы"

    def __str__(self):
        return "{} ИД заказа {}".format(self.order_datetime, self.id)

    def last_action(self):
        return self.maintenanceaction_set.all().latest()

    def last_status(self):
        return self.maintenanceaction_set.all().latest().status.get_status_name_display()
    last_status.short_description = 'Статус заказа'

    def status_expired(self):
        acts = self.maintenanceaction_set.all().latest()
        if not acts.status.expiry_time:
            return False
        to_date = acts.action_datetime + timedelta(hours=acts.status.expiry_time)
        last_date = acts.action_datetime + timedelta(hours=acts.status.expiry_time)
        for x in range((to_date - acts.action_datetime).days + 1):
            if (to_date + timedelta(days=x)).weekday() in [5, 6]:
                last_date += timedelta(days=1)
                if last_date.weekday() in [5, 6]:
                    last_date += timedelta(days=1)
        return timezone.now() > last_date
    status_expired.boolean = True




class MaintenanceActionStatus(models.Model):
    NEW = 0
    IN_WORK = 1
    WAITING = 2
    COMPLETED = 3
    EXPIRED = 4
    TO_CLIENT = 5
    ARCHIVE = 6

    status_set = (
             (NEW, 'Новый'),
             (IN_WORK, 'В работе'),
             (WAITING, 'Ожидание'),
             (COMPLETED, 'Выполнен'),
             (EXPIRED, 'Просрочен'),
             (TO_CLIENT, 'Передан клиенту'),
             (ARCHIVE, 'Архивный')
         )

    status_name = models.PositiveIntegerField("Состояние", choices=status_set, unique=True, null=False, blank=False, default=0)
    expiry_time = models.PositiveIntegerField('Допустимая продолжительность статуса', help_text='в часах', default=0)

    class Meta:
        db_table = 'maintenance_action_status'
        verbose_name = 'Справочник состояний РАБОТЫ'
        verbose_name_plural = 'Справочник состояний РАБОТЫ'

    def __str__(self):
        return "{}".format(self.get_status_name_display())



class MaintenanceAction(models.Model):
    order = models.ForeignKey(MaintenanceOrder, on_delete=models.CASCADE, null=False, blank=False)
    action_datetime = models.DateTimeField("Дата операции", auto_now_add=True)
    manager_user = models.ForeignKey(User, verbose_name="Руководитель заказа", on_delete=models.SET_NULL, null=True,
                                     blank=False)
    executor_user = models.ForeignKey(User, verbose_name="Исполнитель заказа", related_name='+',
                                      on_delete=models.SET_NULL, null=True, blank=False)
    setting_user = models.ForeignKey(User, verbose_name="Установил статус заказа", related_name='+',
                                     on_delete=models.SET_NULL, null=True, blank=False)
    status = models.ForeignKey(MaintenanceActionStatus, verbose_name="Статус заказа", on_delete=models.CASCADE,
                               null=False, blank=False)
    action_content = models.TextField("Выполненные работы", max_length=100, default="Заказ принят", null=True, blank=True)

    class Meta:
        db_table = 'maintenance_action'
        verbose_name = "Работы - статусы заказов"
        verbose_name_plural = "Работы - статусы заказов"
        get_latest_by = "action_datetime"

    def __str__(self):
        return "ID заказа:{}".format(self.order.id)


class MaintenanceOrderServiceContent(models.Model):

    add_datetime = models.DateTimeField("Дата операции", auto_now_add=True)
    order = models.ForeignKey(MaintenanceOrder, on_delete=models.CASCADE, null=False, blank=False)
    service_name = models.TextField("Наименование работ", max_length=255, null=False, blank=False)
    service_qty = models.PositiveIntegerField("Кол-во", default=1, null=False, blank=False)
    cost = models.PositiveIntegerField("Стоимость 1 шт", default=0, null=True, blank=False)
    setting_user = models.ForeignKey(User, verbose_name="Добавил выполненую работу", on_delete=models.SET_NULL, null=True, blank=False)

    class Meta:
        verbose_name = "Работы - выполненные работы"
        verbose_name_plural = "Работы - выполненные работы"


class MaintenanceOrderSparesContent(models.Model):

    add_datetime = models.DateTimeField("Дата операции", auto_now_add=True)
    order = models.ForeignKey(MaintenanceOrder, on_delete=models.CASCADE, null=False, blank=False)
    spare_name = models.CharField("Наименование запчасти", max_length=255, default="", null=False, blank=False)
    spare_serial = models.CharField("Серийный № запчасти", max_length=100, default="", null=False, blank=False)
    spares_qty = models.PositiveIntegerField("Кол-во", default=1, null=False, blank=False)
    setting_user = models.ForeignKey(User, verbose_name="Установил статус заказа", on_delete=models.SET_NULL, null=True, blank=False)

    class Meta():
        verbose_name = "Работы - использованые запчасти"
        verbose_name_plural = "Работы - использованые запчасти"