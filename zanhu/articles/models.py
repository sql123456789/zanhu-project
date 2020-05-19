#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from __future__ import unicode_literals

from slugify import slugify
from taggit.managers import TaggableManager
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.db import models
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class ArticleQuerySet(models.query.QuerySet):
    """自定义article查询集QuerySet，提高模型类的可用性"""

    def get_published(self):
        """获取已经发表的文章"""
        return self.filter(status = "P").select_related("user")

    def get_drafts(self):
        """获取草稿箱的文章"""
        return self.filter(status = "D").select_related("user")

    def get_counted_tags(self):
        """统计所有已经发表的文章中，每一个标签的数量（大于0的）"""
        tag_dict = {}
        # self.get_published()获取已经发表的文章 annotate(tagged = models.Count("tags"))对查询集进行聚合分组 filter(tags__t=0)进行过滤出标签大于0的
        # query = self.get_published().annotate(tagged = models.Count("tags")).filter(tags__gt = 0)
        # 此时只要贴上标签那么肯定至少有一个直接遍历循环
        for obj in self.all():
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1
            return tag_dict.items()


@python_2_unicode_compatible
class Articles(models.Model):
    """文章的模型类，slug是url的别名比如再url后面跟一个标题的拼音从而去访问这个资源那么这个拼音就是url的别名"""
    # 定义一个元组用来区分文章时草稿还是已经发表的
    STATUS = (("D", "Draft"), ("P", "Published"))
    title = models.CharField(max_length = 255, unique = True, verbose_name = "标题")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null = True, blank = True, on_delete = models.SET_NULL,
                             related_name = "author", verbose_name = "作者")
    image = models.ImageField(upload_to = "articles_pictures/%Y/%m/%d/", verbose_name = "文章图片")
    slug = models.SlugField(max_length = 255, verbose_name = "(URL)别名")
    # 定义文章的状态D是草稿，P是已经发布
    status = models.CharField(max_length = 1, choices = STATUS, default = "D", verbose_name = "状态")
    content = MarkdownxField(verbose_name = "内容")
    edited = models.BooleanField(default = False, verbose_name = "是否可编辑")
    # tags进行标签管理
    tags = TaggableManager(help_text = "多个标签使用,(英文的逗号)隔开", verbose_name = "标签")
    created_at = models.DateTimeField(db_index = True, auto_now_add = True, verbose_name = "创建时间")
    updated_at = models.DateTimeField(auto_now = True, verbose_name = "更新时间")
    # 把自定义的queryset和模型类关联起来
    objects = ArticleQuerySet.as_manager()

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        ordering = ("created_at",)

    def __str__(self):
        return self.title

    def save(self, force_insert = False, force_update = False, using = None,
             update_fields = None):
        """重写父类方法让用户每次保存文章名的是否都会用slugify给文章起一个别名"""
        self.slug = slugify(self.title)
        super(Articles, self).save()

    def get_markdown(self):
        """将markdown文本转换成HTML"""
        return markdownify(self.content)
