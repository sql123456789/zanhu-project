#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from test_plus.test import TestCase
from zanhu.articles.models import Articles


class ArticlesModelsTest(TestCase):
    def setUp(self):
        """初始化操作"""
        self.user = self.make_user("test_user")  # make_user是创建测试用户
        self.other_user = self.make_user("other_test_user")
        self.article = Articles.objects.create(
            title="第一篇文章",
            content="程序员梦工厂",
            status="P",
            user=self.user,
        )
        self.not_p_article = Articles.objects.create(
            title="第二篇文章",
            content="""慕课网-程序员的梦工厂""",
            user=self.user,
        )

    def test_object_instance(self):
        """判断实例对象是否为Article类型"""
        assert isinstance(self.article, Articles)
        assert isinstance(self.not_p_article, Articles)
        assert isinstance(Articles.objects.get_published()[0], Articles)

    def test_return_values(self):
        """测试返回值"""
        assert self.article.status == "P"
        assert self.article.status != "p"
        assert self.not_p_article.status == "D"
        assert str(self.article) == "第一篇文章"  # 因为__str__方法返回的是title.
        assert self.article in Articles.objects.get_published()
        assert Articles.objects.get_published()[0].title == "第一篇文章"
        assert self.not_p_article in Articles.objects.get_drafts()
