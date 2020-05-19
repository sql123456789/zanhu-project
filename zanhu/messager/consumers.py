#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'
"""
# event loop(事件循环)/event handler(事件处理)/sync(同步)/async(异步)
from channels.consumer import SyncConsumer, AsyncConsumer


class EchoConsumer(SyncConsumer):
    """'同步的consumer'"""

    def websocket_connect(self, event):
        # type==self.request
        # 接收建立的连接
        self.send({
            "type": "websocket.accept"
        })

    def websocket_recieve(self, event):
        """'接收信息'"""
        # 获取用户
        user = self.scope["user"]
        # 获取请求的路径
        path = self.scope["path"]  # Request请求的路径 HTTP, WebSocket
        # 把接收到的消息直接返回回去
        self.send({
            "type": "websocket.send",
            # 发送回去的内容 把text返回回去
            "text": event["text"]
        })


class EchoAsynConsumer(AsyncConsumer):
    """'异步的consumer'"""

    async def websocket_connect(self, event):
        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event):
        # ORM语句同步变异步
        # user = User.objects.get(username=uername)
        # 方式一
        # from channels.db import database_sync_to_async
        # user = await database_sync_to_async(User.objects.get(username=uername))
        # 方式二使用装饰器的方式
        # @database_sync_to_async
        # def get_user(username)
        #     return ser.objects.get(username=uername)
        await self.send({
            "type": "websocket.send",
            "text": event["text"]
        })


# 什么时候使用sync什么时候使用async,用同步或者异步都行但是千万不要再异步的逻辑中写入同步的代码

# scop 再asgi接口规范中定义了,相当于wsgi中的.request
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer


class MyConsumer(WebsocketConsumer):
    """'定义一个同步的消费者'"""

    def connect(self):
        """'重写父类建立连接的方法'"""
        # 使用自己的子协议
        self.accept()
        self.accept(subprotocol = "you protocol")
        # 拒绝连接,并且传入一个状态码
        self.close(code = 403)

    def receive(self, text_data = None, bytes_data = None):
        # 接收的数据原封不动的返回回去 text_data为文本数据
        self.send(text_data = "imooc.com")
        # 把字符串转换为二进制的帧返回
        self.send(bytes_data = "imooc.com")
        # 断开连接
        self.close()

    def disconnect(self, code):
        pass


class MyAsyncConsumer(AsyncWebsocketConsumer):
    """'定义一个异步的consumer'"""


async def connect(self):
    await self.accept(subprotocol = "you protocol")
    await self.close(code = 403)


async def receive(self, text_data = None, bytes_data = None):
    await self.send(text_data = "imooc.com")
    await self.send(bytes_data = "imooc.com")
    await self.close()


async def disconnect(self, code):
    pass
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MessagesConsumer(AsyncWebsocketConsumer):
    """私信功能的consumer,处理私信中的websock请求"""

    async def connect(self):
        if self.scope["user"].is_anonymous:
            # 如果是未登陆的用户直接关闭连接
           await self.close()
        else:
            # 如果是登陆的用户那么每2个一组加入到聊天组监听频道，以用户名作为用户组比较唯一，channels_name未频道
            # self.scope["user"].username等价于self.request.user.username
            await self.channel_layer.group_add(self.scope["user"].username, self.channel_name)
            # 接收websocket聊天
            await self.accept()

    async def receive(self, text_data = None, bytes_data = None):
        """接收私信并返回给前端"""
        await self.send(text_data = json.dumps(text_data))

    async def disconnect(self, code):
        """离开聊天组"""
        # 把当前的用户从聊天组移除出去
        await self.channel_layer.group_discard(str(self.scope["user"].username), self.channel_name)
