#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from django.test import RequestFactory
from test_plus.test import TestCase
from zanhu.users.views import UserUpdateView


class BaseUserTestCase(TestCase):
    """s所有的view的测试基类"""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = self.make_user()


class TestUserUpdateUserView(BaseUserTestCase):
    """测试用户更新数据的view"""

    def setUp(self):
        # 重载父类意思就是父类的这个方法我们按照自己需要的给改写了
        super().setUp()
        self.view = UserUpdateView()
        request = self.factory.get("/fake-url")
        request.user = self.user
        # 直接让测试类模拟发送request请求省去django框架的发送请求的成本
        self.view.request = request

    def test_get_success_url(self):
        self.assertEqual(self.view.get_success_url(), "/users/testuser/")

    def test_get_object(self):
        self.assertEqual(self.view.get_object(), self.user)
