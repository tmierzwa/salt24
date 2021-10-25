from django.conf.urls import url

from fbo.views import FBOUserList, FBOUserInfo, FBOUserCreate, FBOUserUpdate, FBOUserDeactivate, FBOUserActivate, FBOUserModules, FBOUserAuth
from fbo.views import PilotList, PilotCreate, PilotDelete
from fbo.loaders import create_fbouser, update_duties, update_auth, new_params, orderpdt
from salt.views import ParamsList, ParamsUpdate


urlpatterns = [
   url(r'^$', FBOUserList.as_view(), name='user-list'),
   url(r'^user/info/(?P<pk>\d+)/$', FBOUserInfo.as_view(), name='user-info'),
   url(r'^user/create/$', FBOUserCreate.as_view(), name='user-create'),
   url(r'^user/update/(?P<pk>\d+)/$', FBOUserUpdate.as_view(), name='user-update'),
   url(r'^user/delete/(?P<pk>\d+)/$', FBOUserDeactivate.as_view(), name='user-delete'),
   url(r'^user/activate/(?P<pk>\d+)/$', FBOUserActivate.as_view(), name='user-activate'),
   url(r'^user/modules/(?P<pk>\d+)/$', FBOUserModules.as_view(), name='user-modules'),
   url(r'^user/auth/(?P<pk>\d+)/$', FBOUserAuth.as_view(), name='user-auth'),

   url(r'^pilot/list/$', PilotList.as_view(), name='pilot-list'),
   url(r'^pilot/create/$', PilotCreate.as_view(), name='pilot-create'),
   url(r'^pilot/delete/(?P<pk>\d+)/$', PilotDelete.as_view(), name='pilot-delete'),

   url(r'^params/list/$', ParamsList.as_view(), name='parameters'),
   url(r'^params/update/(?P<pk>\d+)/$', ParamsUpdate.as_view(), name='parameters-update'),

   url(r'^_createuser/$', create_fbouser, name='create_fbouser'),
   url(r'^_duties/$', update_duties, name='update_duties'),
   url(r'^_auth/$', update_auth, name='update_auth'),
   url(r'^_params/$', new_params, name='new_params'),
   url(r'^_order/$', orderpdt, name='order_pdt')

]