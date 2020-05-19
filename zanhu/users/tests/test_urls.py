#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from django.urls import reverse, resolve
from test_plus.test import TestCase


class TestUserURLs(TestCase):
    """对2个url进行正向解析1次和反向解析一次所以一共4次"""

    def setUp(self):
        self.user = self.make_user()

    def test_detail_reverse(self):
        """代表正向解析把detail的路由解析成带有参数的字符串"""
        # reverse就是将url字符串的名字解析成url路由的地址
        self.assertEqual(reverse("users:detail", kwargs = {"username": "testuser"}), "/users/testuser/")

    def test_detail_resolve(self):
        """代表反向解析将字符串的网址解析到命名的路由"""
        self.assertEqual(resolve("/users/testuser/").view_name, "users:detail")

    def test_update_reverse(self):
        self.assertEqual(reverse("users:update"), "/users/update/")

    def test_update_resolve(self):
        self.assertEqual(resolve("/users/update/").view_name, "users:update")
