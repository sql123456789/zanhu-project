#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__sql__'

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    """用户详情"""

    model = User
    # 定义前端模板就是将数据渲染到那个前端模板
    template_name = "users/user_detail.html"
    # 模型类里面内置字段
    slug_field = "username"
    # url路由配置里面包含slup的关键字参数
    slug_url_kwarg = "username"

    def get_context_data(self, *args, **kwargs):
        """重写上下文管理器"""
        context = super(UserDetailView, self).get_context_data(**kwargs)
        user = User.objects.get(username = self.request.user.username)
        # 'publisher'为News表中的related_name，获取动态数
        context["moments_num"] = user.publisher.filter(reply = False).count()
        # 获取已经发表的文章数
        context["article_num"] = user.author.filter(status = "P").count()
        # 文章+动态的评论数
        context["comment_num"] = user.publisher.filter(reply = True).count() + user.comment_comments.all().count()
        # 问题数
        context["question_num"] = user.q_author.all().count()
        # 答案数
        context["answer_num"] = user.a_author.all().count()
        # 互动数 = 动态点赞数+问答点赞数+评论数+私信用户数（都有发送或者接收到的私信）
        tmp = set()
        # 我发送私信给了多少不同的用户
        sent_num = user.sent_messages.all()
        for i in sent_num:
            tmp.add(i.recipient.username)
        # 我接收到的私信来自不同的用户
        received_num = user.received_messages.all()
        for r in received_num:
            tmp.add(r.sender.username)

        context["interaction_num"] = user.liked_news.all().count() + user.qa_vote.all().count() + context[
            "comment_num"] + len(tmp)
        return context


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """用户只能更新自己的信息"""

    model = User
    # 是允许用户自己更改的字段
    fields = ["nickname", "email", "picture", "introduction", "job_title", "location", "personal_url", "weibo", "zhihu",
              "github", "linkedin"]
    # 指定数据渲染的前端模板
    template_name = "users/user_form.html"

    def get_success_url(self):
        """更新成功后跳转的页面，默认跳转到用户自己的页面"""
        return reverse("users:detail", kwargs = {"username": self.request.user.username})

    def get_object(self, queryet = None):
        """获取需要返回给前端的对象"""
        # 通过get获取当前的登陆修改的模型类实例
        return self.request.user

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.INFO, _("Infos successfully updated")
        )
        return super().form_valid(form)


user_update_view = UserUpdateView.as_view()

# class UserRedirectView(LoginRequiredMixin,RedirectView):
#     permanent = False
#
#     template_name = "accounts/login.html"
#     def get_redirect_url(self):
#         return reverse("users:detail", kwargs = {"username": self.request.user.username})
