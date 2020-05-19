#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from test_plus.test import TestCase
from zanhu.news.models import News


class NewsModelsTest(TestCase):
    """测试News的models"""

    def setUp(self):
        """创建两个用户可以互相发表评论点赞"""
        self.user = self.make_user("user01")
        self.other_user = self.make_user("user02")
        # 给第一个用户创建两个文章
        self.first_news = News.objects.create(
            user = self.user,
            content = "第一条动态"
        )
        self.first_news = News.objects.create(
            user = self.user,
            content = "第二条动态"
        )
        # 创建一个评论
        self.third_news = News.objects.create(
            user = self.other_user,
            content = "评论的第一条评论",
            reply = True,
            parent = self.first_news
        )

    def test__str__(self):
        # 这里为什么测试的时第二条动态，因为刚才在这创建动态的时候创建第一条动态的语句时报错了，第一条动态失败了所以第二天先创建了，所以测试的第二条动态才是第一条动态，str时返回的就是他了
        self.assertEqual(self.first_news.__str__(), "第二条动态")

    def test_switch_liked(self):
        """测试点赞或者取消点赞"""
        # 给user01这个用户的第一个文章点赞
        self.first_news.switch_like(self.user)
        # 判断此时的文章点赞数是否为1
        assert self.first_news.count_likers() == 1
        # 当点过赞了判断此时的用户是否再已经点过赞的用户当中
        assert self.user in self.first_news.get_likers()

    def test_reply_this(self):
        """测试回复功能"""
        # 获取当前的所有评论数
        initial_count = News.objects.count()
        # 给第一个文章评论
        self.first_news.reply_this(self.other_user, "评论第一条动态")
        # 判断测试的评论数
        assert News.objects.count() == initial_count + 1
        # 判断测试的评论数是否为2
        assert self.first_news.comment_count() == 2
        # 判断测试的评论是否再已经评论过的内容里面
        assert self.third_news in self.first_news.get_thread()
