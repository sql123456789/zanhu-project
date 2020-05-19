#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

# 从channels中导入协议路由解析
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from zanhu.messager.consumers import MessagesConsumer
from zanhu.notifications.consumers import NotificationsConsumer
# 使用channels的认证中间件栈
from channels.auth import AuthMiddlewareStack
# 元组级的校验
from channels.security.websocket import AllowedHostsOriginValidator

# self.scope["type"] 获取协议类型 然后再去字典中匹配对应的协议如果是websocket协议就传递给consumer如果是http协议就传递给django的视图view
# channels routing是scope级别的一个连接只能有一个consumer接收和处理
# self.scope["url_route"]["kwargs"]["username"]获取url中的关键字
application = ProtocolTypeRouter({
    # 不用写上HTTP协议框架回自动帮我们加上
    # "http":views,
    # AllowedHostsOriginValidator会读取djano中的allowed host就是允许那些主机或者域名去访问
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                # 为了和http协议区分开加上ws
                path("ws/notifications", NotificationsConsumer),
                path("ws/<str:username>/", MessagesConsumer)
            ])
        )
    )
})

"""
AuthMiddlewareStack用于websocket认证，继承了CookieMiddleware，SessionMiddleware, Authmiddleware兼容django的认证系统
AllowedHostsOriginValidator和OriginValidator可以防止通过websocket进行csrf攻击
OriginValidator需要手动添加允许访问的ip和域名和源站
使用AllowedHostsOriginValidator允许访问的源站和base.settings.py文件中的ALLOWED_HOSTS相同

from channels.security.websocket import OriginValidator
# 使用OriginValidator手动添加允许访问的源站
application = ProtocolTypeRouter(
    OriginValidator(
       AuthMiddlewareStack(
           URLRouter([
               ...
           ])
       ), ["imooc.com", "http://.imooc.com:80", "http://muke.site.com"]
    )
)
"""
