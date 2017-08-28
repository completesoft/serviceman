from django.db import models
from django.contrib.auth.models import User




class Clients(models.Model):
    client_name = models.CharField("Имя клиента", max_length=100, default='', null=False, blank=False)
    client_contact = models.CharField("Контакты клиента", max_length=100, default='', null=False, blank=False)
    client_corp = models.BooleanField("Корпоративность клиента", null=False, blank=False)

    class Meta():
        db_table = 'clients'
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return '{}'.format(self.client_name)

class DocOrderHeader (models.Model):
    order_barcode = models.IntegerField("Штрихкод", null=False, blank=False)
    order_datetime = models.DateTimeField("Дата", auto_now_add=True)
    client = models.ForeignKey(Clients, verbose_name="Клиент", on_delete=models.SET_NULL, null=True, blank=False)
    client_position = models.CharField("Размещение у клиента", max_length=100, default='', null=False, blank=False)
    device_name = models.CharField("Наименование устройства", default='',max_length=100, null=False, blank=False)
    device_defect = models.CharField("Заявленная неисправность", default='', max_length=255, null=False, blank=False)
    device_serial = models.CharField("Серийный номер устройства", default='', max_length=100, null=False, blank=False)
    order_comment = models.CharField("Комментарий", max_length=255, null=True, blank=True)

    class Meta():
        db_table = 'doc_order_header'
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return "{} ИД заказа {}".format(self.order_datetime, self.id)

    def last_action(self):
        acts = self.docorderaction_set.all().latest()
        return acts

    def last_status(self):
        acts = DocOrderAction.objects.filter(doc_order=self).latest()
        return acts.status.status_name

class DirStatus (models.Model):

    # status_set = (
    #     ('Новый', 'Новый'),
    #     ('В работе', 'В работе'),
    #     ('Ожидание', 'Ожидание'),
    #     ('Выполнен', 'Выполнен'),
    #     ('Просрочен', 'Просрочен')
    # )

    status_name = models.CharField("Состояние", max_length=100, null=False, blank=False)

    class Meta():
        db_table = 'dir_status'
        verbose_name = "Справочник состояний"
        verbose_name_plural = "Справочник состояний"

    def __str__(self):
        return "{}".format(self.status_name)


class DocOrderAction(models.Model):

    doc_order = models.ForeignKey(DocOrderHeader, on_delete=models.CASCADE, null=True, blank=False)
    action_datetime = models.DateTimeField("Дата операции", auto_now_add=True)
    manager_user = models.ForeignKey(User, verbose_name="Руководитель заказа", on_delete=models.SET_NULL, null=True, blank=False)
    executor_user = models.ForeignKey(User,verbose_name="Исполнитель заказа", related_name='+',on_delete=models.SET_NULL, null=True, blank=False)
    status = models.ForeignKey(DirStatus, on_delete=models.SET_NULL, null=True, blank=False)
    action_comment = models.TextField("Комментарий операции", max_length=100, null=True, blank=True)

    class Meta():
        db_table = 'doc_order_action'
        verbose_name = "Состояние заказа"
        verbose_name_plural = "Состояние заказа"
        get_latest_by = "action_datetime"

    def __str__(self):
        return "{}, {}, {}".format(self.doc_order_id, self.status_id, self.action_datetime)



class DocOrderServiceContent(models.Model):

    order = models.ForeignKey(DocOrderHeader, on_delete=models.CASCADE, null=False, blank=False)
    service_name = models.TextField("Наименование работ", max_length=255, null=False, blank=False)
    service_qty = models.DecimalField("Количество работ", max_digits=4, decimal_places=2, default=1.0, null=False, blank=False)

    class Meta():
        db_table = 'doc_order_service_content'
        verbose_name = "Выполненные работы"
        verbose_name_plural = "Выполненные работы"


class DocOrderSparesContent (models.Model):

    order = models.ForeignKey(DocOrderHeader, on_delete=models.CASCADE, null=False, blank=False)
    spare_name = models.CharField("Наименование запчасти", max_length=255, default="", null=False, blank=False)
    spare_serial = models.CharField("Серийный № запчасти", max_length=100, default="", null=False, blank=False)

    class Meta():
        db_table = 'doc_order_spares_content'
        verbose_name = "Использованные запчасти"
        verbose_name_plural = "Использованные запчасти"


class ClientsDep (models.Model):

    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    client_dep_name = models.CharField("Подразделение клиента", max_length=100, default="", null=False, blank=False)

    class Meta():
        db_table = 'clients_dep'
        verbose_name = "Подразделения клиента"
        verbose_name_plural = "Подразделения клиентов"


class Images(models.Model):

    image = models.BinaryField ("Изображение устройства", null=True, blank=True)
    doc_order = models.ForeignKey(DocOrderHeader, on_delete=models.CASCADE)
    image_comment = models.CharField("Комментарий", max_length=255, default="", null=True, blank=True)

    class Meta():
        db_table = 'images'
        verbose_name = "Фотография устройства"
        verbose_name_plural = "Фотографии устройства"



