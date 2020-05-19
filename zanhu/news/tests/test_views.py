#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from test_plus.test import TestCase
from zanhu.news import views
from zanhu.news.models import News
# 导入client模拟一个浏览器
from django.test import Client
# 导入reverse解析url
from django.urls import reverse

class NewsViewsTest(TestCase):
    """测试news的view"""
    def setUp(self):
        # 创建2个用户
        self.user = self.make_user("user01")
        self.other_user = self.make_user("user02")

        # 模拟浏览器客户端发送请求
        self.client = Client()
        self.other_client = Client()

        # 模拟两个用户登陆
        self.client.login(username="user01",password="password")
        self.other_client.login(username="user02",password="password")

        # 创建2个动态文章
        self.first_news = News.objects.create(
            user = self.user,
            content = "第一条动态"
        )
        self.second_news = News.objects.create(
            user = self.user,
            content = "第二条动态"
        )
        # 创建一个评论
        self.third_news = News.objects.create(
            user = self.other_user,
            content = "第一条动态的评论",
            reply = True,
            parent = self.first_news
        )

    def test_news_list(self):
        """测试文章列表页的功能"""
        # 模拟客户端发送一个get请求,返回response
        response = self.client.get(reverse("news:list"))
        # 判断返回的状态码时候为200
        assert response.status_code == 200
        # 判断第一条文章是否再文章列表中
        assert self.first_news in response.context["news_list"]
        # 判断第二条文章是否再文章列表中
        assert self.second_news in response.context["news_list"]
        # 判断第一条评论是否再文章列表中
        assert self.third_news not in response.context["news_list"]

    def test_delete_news(self):
        """测试删除文章"""
        # 获取当前的文章总数
        initial_count = News.objects.count()
        # 模拟浏览器发送一个post请求,删除第二条文章
        response = self.client.post(reverse("news:delete_news",kwargs={"pk":self.second_news.pk}))
        # 判断返回的状态吗是否为302
        assert response.status_code == 302
        # 判断此时的文章总数少了一片
        assert News.objects.count() == initial_count-1

    def test_post_news(self):
        """测试发送文章"""
        # 获取当前的文章总数
        initial_count = News.objects.count()
        # 模拟发送一个post请求发送一片文章
        response = self.client.post(reverse("news:post_news"),{"post":"你好世界"},
                                    HTTP_X_REQUESTED_WITH="XMLHttpRequest" #表示发送一个ajax request请求
                                    )
        assert response.status_code == 200
        assert News.objects.count() == initial_count+1

    def test_like_news(self):
        """点赞"""
        # 模拟一个post请求，去给第一篇文章点赞
        response = self.client.post(reverse("news:like_post"),{"news":self.first_news.pk},
                                    HTTP_X_REQUESTED_WITH = "XMLHttpRequest" #表示发送一个ajax request请求
         )
        assert response.status_code == 200
        # 判断点赞后数量是否为1
        assert self.first_news.count_likers() == 1
        # 判断user01是否再点赞的用户当中
        assert self.user in self.first_news.get_likers()
        # 判断一下此时返回的赞的数量是否为1
        assert response.json()["likes"] == 1

    def test_get_thread(self):
        """测试获取的文章的评论"""
        response = self.client.get(reverse("news:get_thread"),{"news":self.first_news.pk},# 获取第一篇文章的评论
                                    HTTP_X_REQUESTED_WITH = "XMLHttpRequest"
                                   )
        assert response.status_code == 200
        # 判断一下返回的json中的uuid是否为第一篇文章的主键
        assert response.json()["uuid"] == str(self.first_news.pk)
        # 判断一下返回的json中的文章内容是否为第一篇文章
        assert "第一条动态" in response.json()["news"]
        # 判断的返回的文章评论是否为第一篇文章的评论
        assert "第一条动态的评论" in response.json()["thread"]

    def test_post_comments(self):
        """测试发表文章的评论"""
        # 模拟一个浏览器请求向第二条文章发送一个评论
        response = self.client.post(reverse("news:post_comment"),{"reply":"第二条文章的评论","parent":self.second_news.pk},
                                    HTTP_X_REQUESTED_WITH = "XMLHttpRequest")
        assert response.status_code == 200
        # 判断一下此时第二篇文章中评论的数量是否为1
        assert response.json()["comments"] == 1






