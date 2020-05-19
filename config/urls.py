from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from zanhu.news.views import NewsListView

urlpatterns = [
                  path("", NewsListView.as_view(), name = "home"),
                  path(
                      "about/", TemplateView.as_view(template_name = "pages/about.html"), name = "about"
                  ),
                  # User management
                  path("users/", include("zanhu.users.urls", namespace = "users")),
                  # 用户管理
                  path("accounts/", include("allauth.urls")),
                  # Your stuff: custom urls includes go here

                  # 需要开发的应用
                  # 动态的路由
                  path("news/", include("zanhu.news.urls", namespace = "news")),
                  # 文章的路由
                  path("articles/", include("zanhu.articles.urls", namespace = "articles")),
                  # 问题的模块
                  path("qa/", include("zanhu.qa.urls", namespace = "qa")),
                  # 私信模块
                  path("messages/", include("zanhu.messager.urls", namespace = "messages")),
                  # 通知模块
                  path("notifications/", include("zanhu.notifications.urls", namespace = "notifications")),
                  # 第三方应用
                  # 编辑文章时的markdown路由
                  path("markdownx/", include("markdownx.urls")),
                  # 搜索模块的url
                  path("search", include("haystack.urls")),
                  # 进行文章评论的路由
                  path('comments/', include('django_comments.urls')),
              ] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs = {"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs = {"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs = {"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
