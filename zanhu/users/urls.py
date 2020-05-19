from django.urls import path
from zanhu.users import views

app_name = "users"
urlpatterns = [
    path("update/", views.user_update_view, name="update"),
    #       把username当作参数
    path("<str:username>/", views.user_detail_view, name="detail"),
    # path("~redirect/", views.user_redirect_view, name="redirect"),
]
