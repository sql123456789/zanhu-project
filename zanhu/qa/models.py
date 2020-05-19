#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from __future__ import unicode_literals
from collections import Counter
import uuid
from slugify import slugify
from taggit.managers import TaggableManager
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.db import models
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


@python_2_unicode_compatible
class Vote(models.Model):
    """使用Django中的Content Type，同时关联用户对问题和回答的投票，就是把vote变成通用类外键"""
    uuid_id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = "qa_vote", on_delete = models.CASCADE,
                             verbose_name = "用户")
    # true赞成 false反对
    value = models.BooleanField(default = False, verbose_name = "赞成或者反对")
    # 设置genericforeignkey通用外键的设置,就是把vote表变成一张通用的表用其他的模型类关联到这张表
    content_type = models.ForeignKey(ContentType, related_name = "votes_on", on_delete = models.CASCADE)
    # 通用类的被其他模型类关联的id就是如果其他类是什么主键这里的id的类型就是什么
    object_id = models.CharField(max_length = 255)
    # 直接使用主键GenericForeignKey
    vote = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField(auto_now_add = True, verbose_name = "创建时间")
    updated_at = models.DateTimeField(auto_now = True, verbose_name = "更新时间")

    class Meta:
        verbose_name = "投票"
        verbose_name_plural = verbose_name
        # 使用联合唯一键, 就是某一个用户只能给某一个模型类中的某一条数据点赞或者踩
        unique_together = ("user", "content_type", "object_id", )
        # SQL优化,联合唯一索引
        index_together = ("content_type", "object_id", )


@python_2_unicode_compatible
class QuestionQuerySet(models.query.QuerySet):
    """自定义QuerySet,提高模型类的可用性"""

    def get_answered(self):
        """已经回答的问题"""
        return self.filter(has_answer = True).select_related("user")

    def get_unanswered(self):
        """未被回答的问题"""
        return self.filter(has_answer = False).select_related("user")

    def get_counted_tags(self):
        """统计所有问题标签的数量（大于0的）"""
        tag_dict = {}
        for obj in self.all():
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1
        return tag_dict.items()


@python_2_unicode_compatible
class Question(models.Model):
    """问题的模型类"""
    STATUS = (("O", "Open"), ("C", "Close"), ("D", "Draft"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = "q_author", on_delete = models.CASCADE,
                             verbose_name = "提问者")
    title = models.CharField(max_length = 255, unique = True, verbose_name = "标题")
    slug = models.SlugField(max_length = 80, null = True, blank = True, verbose_name = "(URL)别名")
    # 问题的状态默认是开放的
    status = models.CharField(max_length = 1, choices = STATUS, default = "O", verbose_name = "问题状态")
    content = MarkdownxField(verbose_name = "内容")
    tags = TaggableManager(help_text = "多个标签使用,(英文)隔开", verbose_name = "标签")
    # 是否接收回答
    has_answer = models.BooleanField(default = False, verbose_name = "接收回答")
    # 听过GenericForeignKey关联到Vote表, 不是实际的字段，就是再生成数据表的时候这个并不是表里面的字段
    votes = GenericRelation(Vote, verbose_name = "投票情况")
    created_at = models.DateTimeField(auto_now_add = True, verbose_name = "创建时间")
    updated_at = models.DateTimeField(auto_now = True, verbose_name = "更新时间")

    objects = QuestionQuerySet.as_manager()

    class Meta:
        verbose_name = "问题"
        verbose_name_plural = verbose_name
        # 按照时间倒叙排列
        ordering = ("-created_at", )

    def save(self, *args, **kwargs):
        """重写父类的save方法当保存问题是没有slug时默认生成一个"""
        if not self.slug:
            self.slug = slugify(self.title)
        super(Question, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        """的票数"""
        # 赞同票多少，反对票多少，就是把True和false的都放在这个dic中
        dic = Counter(self.votes.values_list("value", flat = True))
        # 的票数就是value-false的
        return dic[True] - dic[False]

    def get_answers(self):
        """获取所有的回答"""
        return Answer.objects.filter(question = self)

    def count_answers(self):
        """当前的回答数"""
        # self作为参数当前的问题回答数
        return self.get_answers().count()

    def get_upvoters(self):
        """赞同的用户"""
        return [vote.user for vote in self.votes.filter(value = True)]

    def get_downvoters(self):
        """反对的用户就是踩的用户"""
        return [vote.user for vote in self.votes.filter(value = False)]

    def get_accepted_answer(self):
        """获取问题下面被接收的回答"""
        return Answer.objects.get(question = self, is_answer = True)


@python_2_unicode_compatible
class Answer(models.Model):
    """答案的模型类"""
    uuid_id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = "a_author", on_delete = models.CASCADE,
                             verbose_name = "回答者")
    question = models.ForeignKey(Question, on_delete = models.CASCADE, verbose_name = "问题")
    content = MarkdownxField(verbose_name = "内容")
    is_answer = models.BooleanField(default = False, verbose_name = "回答是否被采纳")
    # 听过GenericForeignKey关联到Vote表, 不是实际的字段，就是再生成数据表的时候这个并不是表里面的字段
    votes = GenericRelation(Vote, verbose_name = "投票情况")
    created_at = models.DateTimeField(db_index = True, auto_now_add = True, verbose_name = "创建时间")
    updated_at = models.DateTimeField(auto_now = True, verbose_name = "更新时间")

    class Meta:
        # 多条件排序，首先按照是否被采纳排序，然后按照时间顺序排序
        ordering = ("-is_answer", "-created_at", )
        verbose_name = "回答"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.content

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        """的票总数"""
        # 用Counter记录出value为True的支持的票数和反对的票数，那么的票数就是True-False
        dic = Counter(self.votes.values_list("value", flat = True))
        return dic[True] - dic[False]

    def get_upvoters(self):
        """支持的票的用户"""
        return [vote.user for vote in self.votes.filter(value = True)]

    def get_downvoters(self):
        """反对的票的用户"""
        return [vote.user for vote in self.votes.filter(value = False)]

    def accept_answer(self):
        """接收回答"""
        # 当一个问题有多个回答是只能接收一个回答其他的回答都需要置为未接收
        answer_set = Answer.objects.filter(question = self.question) # 查询当前问题的所有回答
        # 将查询出来的问题一律置为未接受
        answer_set.update(is_answer = False)
        # 接收当前的回答并保存
        self.is_answer = True
        self.save()
        # 该问题已经有被接收的回答，保存
        self.question.has_answer =True
        self.question.save()

# 1.需要返回查询集的逻辑写在QuerySetModel中
# 2.模型类中数据库处理的逻辑写在Models中
# 3.业务相关逻辑的处理写在Views中
