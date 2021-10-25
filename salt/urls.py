from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import logout, logout_then_login
from salt.views import dispatcher, salt_login, salt_password_change, admin_password_change

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^panel/', include('panel.urls', namespace="panel")),
    url(r'^camo/', include('camo.urls', namespace="camo")),
    url(r'^pdt/', include('pdt.urls', namespace="pdt")),
    url(r'^sms/', include('sms.urls', namespace="sms")),
    url(r'^ato/', include('ato.urls', namespace="ato")),
    url(r'^fin/', include('fin.urls', namespace="fin")),
    url(r'^fbo/', include('fbo.urls', namespace="fbo")),
    url(r'^res/', include('res.urls', namespace="res")),

    url(r'^login/$', salt_login, name='login'),
    url(r'^logout/$', logout, {'next_page': 'dispatcher'}, name='logout'),
    url(r'^password/$', salt_password_change, {'post_change_redirect': 'dispatcher'}, name='pwd-change'),
    url(r'^adminpwd/(?P<user_id>\d+)/$', admin_password_change, name='admin-pwd-change'),
    url(r'^$', dispatcher, name='dispatcher'),
]

admin.site.site_header = 'Administracja systemu SALT'