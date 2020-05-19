#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from __future__ import unicode_literals
import uuid

from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


@python_2_unicode_compatible
class MessageQuerySet(models.query.QuerySet):
    """重写消息的queryset"""

    def get_conversation(self, sender, recipient):
        """用户间的私信会话"""
        # A发送给B的消息
        qs_one = self.filter(sender = sender, recipient = recipient).select_related("sender", "recipient")
        # B发送给A的消息
        qs_two = self.filter(sender = recipient, recipient = sender).select_related("sender", "recipient")
        # 取并集之后按照时间排序
        return qs_one.union(qs_two).order_by("created_at")

    def get_most_recent_conversation(self, recipient):
        """获取最近一次私信互动的用户"""
        try:
            # 当前登陆用户发送的消息
            qs_sent = self.filter(sender = recipient).select_related("sender", "recipient")
            # 当前登陆用户接收的消息
            qs_received = self.filter(recipient = recipient).select_related("sender", "recipient")
            # union表示把两个查询集取并集，取并集之后按照时间排序，获取最后一条
            qs = qs_sent.union(qs_received).latest("created_at")
            if qs.sender == recipient:
                # 如果登陆用户有发送消息，返回消息的接受者
                return qs.recipient
            # 否则返回消息的发送者
            return qs.sender
        except self.model.DoesNotExist:
            # 如果模型实例不存在，则返回当前用户
            return get_user_model().objects.get(username = recipient.username)


@python_2_unicode_compatible
class Message(models.Model):
    """用户间私信模型类"""
    uuid_id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = "sent_messages", blank = True, null = True,
                               on_delete = models.SET_NULL, verbose_name = "发送者")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = "received_messages", blank = True,
                                  null = True, on_delete = models.SET_NULL, verbose_name = "接收者")
    message = models.TextField(blank = True, null = True, verbose_name = "内容")
    # True表示这个消息已读，False表示这个消息未读
    unread = models.BooleanField(default = True, verbose_name = "是否未读")
    # 没有updated_at，私信发送之后不能修改或撤回
    created_at = models.DateTimeField(db_index = True, auto_now_add = True, verbose_name = "创建时间")
    objects = MessageQuerySet.as_manager()

    class Meta:
        verbose_name = "私信"
        verbose_name_plural = verbose_name
        ordering = ("-created_at",)

    def __str__(self):
        return self.message

    def mark_as_read(self):
        # 标记是否读了
        if self.unread:
            self.unread = False
            self.save()
