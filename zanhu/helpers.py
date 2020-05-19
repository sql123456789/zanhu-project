#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'
from functools import wraps
from django.http import HttpResponseBadRequest
from django.views.generic import View
from django.core.exceptions import PermissionDenied


def ajax_required(f):
    """传入要装饰的函数是否为ajax请求这个装饰器用来判断是不是ajax请求"""

    # wraps使用wraps装饰不会改变f的名称以及信息
    @wraps(f)
    def wrap(request, *args, **kwargs):
        # request.is_ajax判断是不是ajax请求
        if not request.is_ajax():
            return HttpResponseBadRequest("不是ajax请求")
        else:
            return f(request, *args, **kwargs)

    return wrap


class AuthorRequreMixin(View):
    """验证是否为原作者, 用于状态删除,文章编辑"""

    def dispatch(self, request, *args, **kwargs):
        """重写父类的方法"""
        # 判断当前要请求的用户不和request中的用户相同的时候就报错
        if self.get_object().user.username != self.request.user.username:
            raise PermissionDenied()
        # 如果当前的用户就是登陆中的父类直接重载父类的方法返回
        return super().dispatch(request, *args, **kwargs)
