#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

# import pytest
#
# from zanhu.users.models import User
#
# pytestmark = pytest.mark.django_db
#
#
# def test_user_get_absolute_url(user: User):
#     assert user.get_absolute_url() == f"/users/{user.username}/"

from test_plus.test import TestCase


class TestUser(TestCase):
    """定义一个测试user模型类的测试类TestUser"""

    def setUp(self):
        """测试类中的基本信息"""
        # 创建一个用户user
        self.user = self.make_user()

    def test__str__(self):
        """测试模型类中的__str__方法"""
        # 使用断言查看返回的值是否相等,判断调用user模型类中的__str__方法返回的用户名时候和调用测试类生成的一样
        self.assertEqual(self.user.__str__(), "testuser")

    def test_get_absolute_url(self):
        """查看跳转的url是否正确"""
        self.assertEqual(self.user.get_absolute_url(), "/users/testuser/")

    def test_get_profile_name(self):
        """测试没有昵称的话返回的是用户的用户名"""
        assert self.user.get_profile_name() == "testuser"
        # 设置昵称之后在测试一下是否等于我们的昵称
        self.user.nickname = "昵称"
        assert self.user.get_profile_name() == "昵称"
