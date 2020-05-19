#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView
from zanhu.news.models import News
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
# require_http_methods表示要求的http方法可以用来装饰函数
from django.views.decorators.http import require_http_methods
from zanhu.helpers import ajax_required, AuthorRequreMixin
from django.urls import reverse_lazy


# Create your views here.
class NewsListView(LoginRequiredMixin, ListView):
    """首页动态"""
    # 指定关联的模型类，就是给前端模板返回哪一个表的数据
    model = News
    # 分页每页显示多少行 url中？page
    paginate_by = 20
    # 指定前端要渲染的模板 可以不写默认为 模板名_list.html
    template_name = "news/news_list.html"
    """
        # 前端html中要循环的对象就是进行遍历查询的 默认为 模型类名_.list 或 object_list
        context_object_name = 'new_list'  # 自定义查询集在模板中的名字
        ordering = 'created_at'  # 多字段排序 需要用元组
        # 简单过滤
        queryset = News.objects.all() 与def get_queryset(self): 二选一
        # 使用更复杂的排序
        def get_ordering(self):
            pass
        # 更复杂的分页 queryset -> 查询集对象
        def get_paginate_by(self, queryset):
            pass
    """

    def get_queryset(self):
        """过滤查询集，就是把查询出来的数据再过滤一下"""
        return News.objects.filter(reply = False).select_related("user", "parent").prefetch_related("liked")


class NewsDeleteView(LoginRequiredMixin, AuthorRequreMixin, DeleteView):
    """使用通用类来删除用户评论"""
    # 关联要使用的模型类
    model = News
    # 渲染到前端模板
    template_name = "news/news_confirm_delete.html"
    # 使用关键字url中要是出的动态或评论的主键去删除,通过url传入要删除的主键的id,默认值slug
    # slug_url_kwarg = 'slug'
    # 通过url传入要删除的主键的id,默认值是pk
    # pk_url_kwarg = 'pk'
    # 删除之后跳转的路径,这里跳转到首页,再项目URLConf未加载前使用
    success_url = reverse_lazy("news:list")


@login_required
@ajax_required
@require_http_methods(['POST'])
def post_new(request):
    """使用ajax post发送文章，必须是用户登陆状态@login_required，必须是post请求"""
    # 把前端返回的文章内容去掉前后的空格
    post = request.POST["post"].strip()
    if post:
        # 把用户发表的文章报错到数据库中
        posted = News.objects.create(user = request.user, content = post)
        # 把用户的文章渲染到前端页面中
        html = render_to_string("news/news_single.html", {"news": posted, "request": request})
        # 返回http请求
        return HttpResponse(html)
    else:
        return HttpResponseBadRequest("内容不能为空！")


@login_required
@ajax_required
@require_http_methods(['POST'])
def liked(request):
    """用户点赞使用ajax请求"""
    # 获取要被点赞的状态文章的id
    news_id = request.POST["news"]
    # 获取这个文章状态
    news = News.objects.get(pk = news_id)
    # 取消点赞或者增加点赞,传入当前要操作的用户
    news.switch_like(request.user)
    # 返回赞的数量
    return JsonResponse({"likes": news.count_likers()})


@login_required
@ajax_required
@require_http_methods(['GET'])
def get_thread(request):
    """返回文章的评论，AJAX GET请求"""
    # 拿到文章动态的主键
    news_id = request.GET["news"]
    # 通过查询到的主键获取到文章
    news = News.objects.select_related("user").get(pk = news_id)
    # 当没有评论时还是这个页面
    news_html = render_to_string("news/news_single.html", {"news": news})
    # 有评论的话就把评论渲染到这个页面
    thread_html = render_to_string("news/news_thread.html", {"thread": news.get_thread()})
    return JsonResponse(
        {
            "uuid": news_id,
            "news": news_html,
            "thread": thread_html
        }
    )


@login_required
@ajax_required
@require_http_methods(['POST'])
def post_comment(request):
    """进行评论，AJAX POST评论"""
    # 拿到用户的评论
    post = request.POST["reply"].strip()
    # 拿到评论的父主键
    parent_id = request.POST["parent"]
    # 拿到用户的父关联
    parent = News.objects.get(pk = parent_id)
    # 如果评论不为空
    if post:
        parent.reply_this(request.user, post)
        # 返回评论的数量渲染到标签中
        return JsonResponse({"comments": parent.comment_count()})
    else:
        return HttpResponseBadRequest("评论不能为空！")


@login_required
@ajax_required
@require_http_methods(['POST'])
def update_interactions(request):
    """更新互动信息"""
    data_point = request.POST["id_value"]
    news = News.objects.get(pk = data_point)
    return JsonResponse({"likes": news.count_likers(), "comments": news.comment_count()})
