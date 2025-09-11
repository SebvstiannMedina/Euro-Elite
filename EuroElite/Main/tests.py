from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class RegistroTests(TestCase):
    def test_pagina_registro_carga(self):
        resp = self.client.get(reverse('registro'))
        self.assertEqual(resp.status_code, 200)

    def test_crear_usuario(self):
        User = get_user_model()
        usuario = User.objects.create_user(username="test", email="t@test.com", password="12345")
        self.assertTrue(User.objects.filter(username="test").exists())

