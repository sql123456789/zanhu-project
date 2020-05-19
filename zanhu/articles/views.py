#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from zanhu.articles.models import Articles
from django.urls import reverse_lazy
from django.contrib import messages
from zanhu.articles.forms import ArticleForm
from zanhu.helpers import AuthorRequreMixin
from django_comments.signals import comment_was_posted
from zanhu.notifications.views import notification_handler


class ArticlesListView(LoginRequiredMixin, ListView):
    """文章的list页，必须是登陆状态"""
    model = Articles
    paginate_by = 10
    context_object_name = "articles"
    template_name = "articles/article_list.html"

    def get_context_data(self, *, object_list = None, **kwargs):
        """重写父类的上下文管理"""
        context = super().get_context_data()
        # 拿到标签数
        context["popular_tags"] = Articles.objects.get_counted_tags()
        return context

    def get_queryset(self):
        return Articles.objects.get_published()


class DraftListView(ArticlesListView):
    """草稿箱文章列表"""

    def get_queryset(self):
        """返回当前用户的草稿箱内容"""
        return Articles.objects.filter(user = self.request.user).get_drafts()

# 把get请求的缓存一个小时
@method_decorator(cache_page(60 * 60), name = "get")
class ArticleCreateView(LoginRequiredMixin, CreateView):
    """用户发表文章和写草稿"""
    model = Articles
    form_class = ArticleForm
    template_name = "articles/article_create.html"
    # 使用django的消息机制把这个消息传递给下次请求
    message = "您的文章已经创建成功"

    def form_valid(self, form):
        """表单校验"""
        # 将当前登陆的用户加载到form表单中
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """创建成功之后跳转的页面"""
        messages.success(self.request, self.message)  # 把消息传递给下次请求
        return reverse_lazy("articles:list")

    # def get_initial(self):
    #     """动态获取文章的标题"""
    #     # 重写父类的initial方法
    #     initial = super().get_initial()
    #     pass
    #     return initial


class ArticleDetailView(LoginRequiredMixin, DetailView):
    """文章详情"""
    model = Articles
    template_name = "articles/article_detail.html"
    # 困扰了好久才发现的问题前端去遍历的时候是以这个context_object_name.user.username遍历的我没写上用了默认的所以出现前端不对一直报错
    context_object_name = "article"

    def get_queryset(self):
        # slug=self.kwargs['slug'] 为urls 中传递的参数 slug
        return Articles.objects.select_related('user').filter(slug = self.kwargs['slug'])


class ArticleEditView(LoginRequiredMixin, AuthorRequreMixin, UpdateView):
    """用户编辑文章1，用户必须是登陆状态 2，用户必须是这篇文章的作者"""
    # 绑定模型类
    model = Articles
    # 编辑成功之后发送一片文章给用户
    message = "您的文章编辑成功！"
    # 绑定表单
    form_class = ArticleForm
    # 绑定前端模板
    template_name = "articles/article_update.html"

    def form_valid(self, form):
        """进行表单验证"""
        # 把当前登陆的操作用户绑定进去
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """编辑成功之后跳转的页面"""
        messages.success(self.request, self.message)  # 把消息传递给下次请求
        return reverse_lazy("articles:article", kwargs = {"slug": self.get_object().slug})


def notify_comment(**kwargs):
    """文章有评论时通知作者"""
    # from django_comments.models import Comment
    actor = kwargs["request"].user
    obj = kwargs["comment"].content_object

    notification_handler(actor, obj.user, "C", obj)


# 观察者模式 = 订阅[列表] + 通知(同步)
comment_was_posted.connect(receiver = notify_comment)
