#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from __future__ import unicode_literals

import uuid
from django.utils.encoding import python_2_unicode_compatible
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import models
from asgiref.sync import async_to_sync
from zanhu.notifications.views import notification_handler


# Create your models here.
@python_2_unicode_compatible
class News(models.Model):
    """动态的模型类related_name父表反向查询就是通过查询父表的一条记录关联出字表的多条记录"""
    uuid_id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    # 发表动态的用户user on_delete设置为当父表的记录删除的时候子表置空，
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, on_delete = models.SET_NULL,
                             related_name = "publisher", verbose_name = "用户")
    # 就是把动态和动态的评论存在一张表中就需要自关联,关联到自己,就像是省市县存在一个表中这样的话就让县去关联市然后市再去关联省就可以了,on_delete = models.CASCADE删除的就直接清空
    parent = models.ForeignKey("self", blank = True, null = True, on_delete = models.CASCADE,
                               related_name = "thread", verbose_name = "自关联")
    # 用户发表的内容,可以市文章也可以市评论
    content = models.TextField(verbose_name = "动态内容")
    # 点赞的用户多对多外键
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name = "liked_news", verbose_name = "点赞的用户")
    # 判断内容为状态还是评论 flase为状态/即文章内容，true为评论
    reply = models.BooleanField(default = False, verbose_name = "是否为评论")

    created_at = models.DateTimeField(db_index = True, auto_now_add = True, verbose_name = "创建时间")
    updated_at = models.DateTimeField(auto_now = True, verbose_name = "更新时间")

    class Meta:
        verbose_name = "首页"
        verbose_name_plural = verbose_name
        # 默认按照时间的倒叙排序
        ordering = ("-created_at",)

    def __str__(self):
        # 返回用户发表的内容
        return self.content

    def save(self, *args, **kwargs):
        """重写父类方法通过异步发送消息通知"""
        super(News, self).save(*args, **kwargs)
        if not self.reply:
            channel_layer = get_channel_layer()
            payload = {
                "type": "receive",
                "key": "additional_news",
                "actor_name": self.user.username
            }
            async_to_sync(channel_layer.group_send)("notifications", payload)

    def switch_like(self, user):
        """判断点赞或者取消"""
        if user in self.liked.all():
            # 用户已经点过赞了则取消赞
            self.liked.remove(user)
        else:
            # 用户还没有赞过则增加赞
            self.liked.add(user)
            # 当有用户点赞的话通知楼主
            notification_handler(user, self.user, "L", self, id_value = str(self.uuid_id), key = "social_update")

    def get_parent(self):
        """返回自关联中的上级记录或者本身"""
        if self.parent:
            return self.parent
        else:
            # 如果当前市评论的话就返回自己
            return self

    def reply_this(self, user, text):
        """
        回复首页动态
        :param user:当前登陆的用户
        :param text:回复的内容
        :return:None
        """
        # 获取父记录，获取动态
        parent = self.get_parent()
        News.objects.create(
            user = user,
            content = text,
            reply = True,
            parent = parent
        )
        # 当有用户回复的时候通知楼主
        notification_handler(user,parent.user,"R", parent, id_value = str(parent.uuid_id), key = "social_update")

    def get_thread(self):
        """关联到当前记录的记录"""
        parent = self.get_parent()
        return parent.thread.all()

    def comment_count(self):
        """评论数"""
        return self.get_thread().count()

    def count_likers(self):
        """点赞数"""
        return self.liked.count()

    def get_likers(self):
        """获取所有点赞用户"""
        return self.liked.all()
