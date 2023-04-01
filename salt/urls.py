from django.urls import include, re_path
from django.contrib import admin
from django.contrib.auth.views import LogoutView as logout, logout_then_login
from salt.views import dispatcher, salt_login, salt_password_change, admin_password_change


app_name = "salt"

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),

    re_path(r'^panel/', include('panel.urls')),
    re_path(r'^camo/', include('camo.urls')),
    re_path(r'^pdt/', include('pdt.urls')),
    re_path(r'^sms/', include('sms.urls')),
    re_path(r'^ato/', include('ato.urls')),
    re_path(r'^fin/', include('fin.urls')),
    re_path(r'^fbo/', include('fbo.urls')),
    re_path(r'^res/', include('res.urls')),

    re_path(r'^login/$', salt_login, name='login'),
    re_path(r'^logout/$', logout.as_view(), {'next_page': 'dispatcher'}, name='logout'),
    re_path(r'^password/$', salt_password_change, {'post_change_redirect': 'dispatcher'}, name='pwd-change'),
    re_path(r'^adminpwd/(?P<user_id>\d+)/$', admin_password_change, name='admin-pwd-change'),
    re_path(r'^$', dispatcher, name='dispatcher'),
]

admin.site.site_header = 'Administracja systemu SALT'