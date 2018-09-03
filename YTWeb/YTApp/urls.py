from django.conf.urls import url
from . import views  
from django.http import HttpResponse

app_name = 'YTApp'

urlpatterns = [
    url(r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /", content_type="text/plain")),
    url(r'^accounts/login/$', views.login_user, name='login_user2'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^register/$', views.UserFormView.as_view(), name='register'),
    url(r'^$', views.ytHome, name='ytHome'),
    url(r'^ytmp3/(?P<ytVidUrlmp3>.+)/$', views.YTmp3Success, name='ytAutomp3'),
    url(r'^ytsearch/$', views.YTSearchSuccess, name='ytAutoSearch'),
]


