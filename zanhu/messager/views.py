#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'
# async_to_sync异步变同步
from asgiref.sync import async_to_sync
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from django.template.loader import render_to_string
from channels.layers import get_channel_layer

from zanhu.messager.models import Message
from zanhu.helpers import ajax_required

class MessagesListView(LoginRequiredMixin, ListView):
    """私信详情列表页"""
    model = Message
    template_name = "messager/message_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        """重写上下文管理器"""
        context = super(MessagesListView, self).get_context_data()
        # 获取除当前登陆用户外的所有用户，按照最近登陆时间降序排列,按照最后的登陆时间降序排序,get_user_model()获取用户模型
        context["users_list"] = get_user_model().objects.filter(is_active=True).exclude(username=self.request.user).order_by("-last_login")[:10]
        # 最近一次私信的用户
        last_conversation = Message.objects.get_most_recent_conversation(self.request.user)
        context["active"] = last_conversation.username
        return context

    def get_queryset(self):
        """最近私信互动的内容"""
        active_user = Message.objects.get_most_recent_conversation(self.request.user)
        return Message.objects.get_conversation(self.request.user, active_user)

class ConversationListView(MessagesListView):
    """与指定用户的私信内容"""
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ConversationListView, self).get_context_data()
        context["active"] = self.kwargs["username"]
        return context

    def get_queryset(self):
        active_user = get_object_or_404(get_user_model(), username=self.kwargs["username"])
        return Message.objects.get_conversation(self.request.user, active_user)


@login_required
@ajax_required
@require_http_methods(["POST"])
def send_message(request):
    """发送消息，AJAX POST请求"""
    # 获取发送者
    sender = request.user
    # 获取接收者的名称
    recipient_username = request.POST["to"]
    # 获取接收者的用户模型
    recipient = get_user_model().objects.get(username = recipient_username)
    # 获取要发送的消息
    message = request.POST["message"]
    # 当用户发送的数据不为空并且接收者不为空时就发送数据
    if len(message.strip()) != 0 and sender != recipient:
        msg = Message.objects.create(
            sender = sender,
            recipient = recipient,
            message = message
        )
        channel_layer = get_channel_layer()
        # 固定传回的给是就是type未给那个函数传回
        payload={
            # receive代表的是consumer中的receive
            "type":"receive",
            # 前面是需要渲染的模板后面是渲染模板的数据
            "message":render_to_string("messager/single_message.html", {"message":msg}),
            "sender":sender.username
        }
        # 将私信加入到组里面 将msg发送给recipient_username这个用户,group_send(group:所在组接收者的username, message:消息内容)
        async_to_sync(channel_layer.group_send)(recipient_username, payload)
        return render(request, "messager/single_message.html",{"message":msg})
    return HttpResponse()

# @login_required
# @ajax_required
# @require_http_methods(["GEt"])
# def receive_message(request):
#     """接收消息，AJAX GET请求"""
#     # 获取发送者发送的消息的id主键
#     message_id= request.GET["messgae_id"]
#     # 获取消息
#     msg = Message.objects.get(pk=message_id)
#     return render(request, "messager/single_message.html",{"message":msg})
