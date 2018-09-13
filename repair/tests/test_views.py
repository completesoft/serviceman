from django.test import TestCase
from ..models import DocOrderHeader
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from ..urls import urlpatterns
from django.conf.urls import RegexURLPattern
import re



class LoginTestCase(TestCase):
    fixtures = ['User', 'Group','test_data']
    # users = {'admin':{'username': 'admin', 'password': 'serviceman'}}

    def _get_admin_user(self):
        admin = User.objects.get(username='admin')
        admin.data = {'username': 'admin', 'password': 'serviceman'}
        admin.save()
        return admin

    def _get_in_serviceman_user(self):
        group_service = Group.objects.get(name='serviceman')
        worker = User.objects.get(username='worker')
        worker.groups.add(group_service)
        worker.data = {'username': 'worker', 'password': 'serviceman'}
        worker.save()
        return worker

    def _get_outsource_serviceman_user(self):
        group_service = Group.objects.get(name='serviceman')
        group_out = Group.objects.get(name='outsource')
        outsourcer = User.objects.create_user(username='outsourcer', password='serviceman')
        outsourcer.groups.add(group_out, group_service)
        outsourcer.data = {'username': 'outsourcer', 'password': 'serviceman'}
        outsourcer.save()
        return outsourcer

    def test_not_logged_get_status_code_302(self):
        i = 1
        for url in urlpatterns:
            ptrn = re.compile(url.regex.pattern)
            kwarg = ptrn.groupindex
            if kwarg:
                resp = self.client.get(reverse('repair:' + url.name, kwargs=kwarg))
                print(i, '***', reverse('repair:' + url.name, kwargs=kwarg))
            else:
                resp = self.client.get(reverse('repair:' + url.name))
                print(i, '***', reverse('repair:' + url.name))
            self.assertEqual(resp.status_code, 302)
            i+=1

    def test_admin_loged_in_get_status_200(self):
        login = self.client.login(**self.users['admin'])
        response = self.client.get(reverse('repair:index'))
        self.assertEqual(str(response.context['user']), self.users['admin']['username'])
        self.assertEqual(response.status_code, 200)
