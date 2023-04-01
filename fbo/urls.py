from django.urls import re_path

from fbo.views import FBOUserList, FBOUserInfo, FBOUserCreate, FBOUserUpdate, FBOUserDeactivate, FBOUserActivate, FBOUserModules, FBOUserAuth
from fbo.views import PilotList, PilotCreate, PilotDelete
from fbo.loaders import create_fbouser, update_duties, update_auth, new_params, orderpdt
from salt.views import ParamsList, ParamsUpdate


urlpatterns = [
   re_path(r'^$', FBOUserList.as_view(), name='user-list'),
   re_path(r'^user/info/(?P<pk>\d+)/$', FBOUserInfo.as_view(), name='user-info'),
   re_path(r'^user/create/$', FBOUserCreate.as_view(), name='user-create'),
   re_path(r'^user/update/(?P<pk>\d+)/$', FBOUserUpdate.as_view(), name='user-update'),
   re_path(r'^user/delete/(?P<pk>\d+)/$', FBOUserDeactivate.as_view(), name='user-delete'),
   re_path(r'^user/activate/(?P<pk>\d+)/$', FBOUserActivate.as_view(), name='user-activate'),
   re_path(r'^user/modules/(?P<pk>\d+)/$', FBOUserModules.as_view(), name='user-modules'),
   re_path(r'^user/auth/(?P<pk>\d+)/$', FBOUserAuth.as_view(), name='user-auth'),

   re_path(r'^pilot/list/$', PilotList.as_view(), name='pilot-list'),
   re_path(r'^pilot/create/$', PilotCreate.as_view(), name='pilot-create'),
   re_path(r'^pilot/delete/(?P<pk>\d+)/$', PilotDelete.as_view(), name='pilot-delete'),

   re_path(r'^params/list/$', ParamsList.as_view(), name='parameters'),
   re_path(r'^params/update/(?P<pk>\d+)/$', ParamsUpdate.as_view(), name='parameters-update'),

   re_path(r'^_createuser/$', create_fbouser, name='create_fbouser'),
   re_path(r'^_duties/$', update_duties, name='update_duties'),
   re_path(r'^_auth/$', update_auth, name='update_auth'),
   re_path(r'^_params/$', new_params, name='new_params'),
   re_path(r'^_order/$', orderpdt, name='order_pdt')

]