#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from django.urls import reverse, resolve
from test_plus.test import TestCase
from zanhu.news.models import News


class TestNewsURLs(TestCase):
    """对2个url进行正向解析1次和反向解析一次所以一共4次"""

    def setUp(self):
        self.user = self.make_user("user01")
        # self.other_user = self.make_user("user02")
        # # 给第一个用户创建两个文章
        # self.first_news = News.objects.create(
        #     user = self.user,
        #     content = "第一条动态"
        # )
        # self.first_news = News.objects.create(
        #     user = self.user,
        #     content = "第二条动态"
        # )
        # # 创建一个评论
        # self.third_news = News.objects.create(
        #     user = self.other_user,
        #     content = "评论的第一条评论",
        #     reply = True,
        #     parent = self.first_news
        # )

    def test_list_reverse(self):
        """代表正向解析把news的list的路由解析成带有参数的字符串"""
        # reverse就是将url字符串的名字解析成url路由的地址
        self.assertEqual(reverse("news:list"), "/news/")

    def test_list_resolve(self):
        """代表反向解析将字符串的网址解析到命名的路由"""
        self.assertEqual(resolve("/news/").view_name, "news:list")

    def test_post_new_reverse(self):
        self.assertEqual(reverse("news:post_news"), "/news/post-news/")

    def test_post_new_resolve(self):
        self.assertEqual(resolve("/news/post-news/").view_name, "news:post_news")

    def test_delete_new_reverse(self):
        # 把pk写成固定的不就可以了
        self.assertEqual(reverse("news:delete_news", kwargs = {"pk": 100}), "/news/delete/100/")

    def test_delete_new_resolve(self):
        self.assertEqual(resolve("/news/delete/100/").view_name, "news:delete_news")

    def test_get_thread_reverse(self):
        self.assertEqual(reverse("news:get_thread"), "/news/get-thread/")

    def test_get_thread_resolve(self):
        self.assertEqual(resolve("/news/get-thread/").view_name, "news:get_thread")

    def test_post_comment_reverse(self):
        self.assertEqual(reverse("news:post_comment"), "/news/post-comment/")

    def test_post_comment_resolve(self):
        self.assertEqual(resolve("/news/post-comment/").view_name, "news:post_comment")

    def test_like_reverse(self):
        self.assertEqual(reverse("news:like_post"), "/news/like/")

    def test_like_resolve(self):
        self.assertEqual(resolve("/news/like/").view_name, "news:like_post")
