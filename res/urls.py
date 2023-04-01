from django.urls import re_path
from res.views import ResourceFBOList, ResourceFBOCreate, ResourceFBOUpdate, ResourceFBODelete
from res.views import ReservationList, ReservationInfo, ReservationCreate, ReservationUpdate, ReservationDelete
from res.views import ReservationFBOInfo, ReservationFBOCreate, ReservationFBOUpdate, ReservationFBODelete
from res.views import BlackoutList, BlackoutInfo, BlackoutCreate, BlackoutUpdate, BlackoutDelete
from res.views import ResParamsList, ResParamsUpdate
from res.views import ReservationCalendar, DutyCalendar, reservation_feed, reservation_move, duty_feed
from res.views import ReservationListMobile


app_name = "res"

urlpatterns = [

    re_path(r'^reservation/list/$', ReservationList, name='reservation-list'),
    re_path(r'^reservation/info/(?P<pk>\d+)/$', ReservationInfo.as_view(), name='reservation-info'),
    re_path(r'^reservation/create/$', ReservationCreate.as_view(), name='reservation-create'),
    re_path(r'^reservation/update/(?P<pk>\d+)/$', ReservationUpdate.as_view(), name='reservation-update'),
    re_path(r'^reservation/delete/(?P<pk>\d+)/$', ReservationDelete.as_view(), name='reservation-delete'),

    re_path(r'^resource/list/$', ResourceFBOList.as_view(), name='resource-list'),
    re_path(r'^resource/create/$', ResourceFBOCreate.as_view(), name='resource-create'),
    re_path(r'^resource/update/(?P<pk>\d+)/$', ResourceFBOUpdate.as_view(), name='resource-update'),
    re_path(r'^resource/delete/(?P<pk>\d+)/$', ResourceFBODelete.as_view(), name='resource-delete'),

    re_path(r'^resfbo/info/(?P<pk>\d+)/$', ReservationFBOInfo.as_view(), name='resfbo-info'),
    re_path(r'^resfbo/create/$', ReservationFBOCreate.as_view(), name='resfbo-create'),
    re_path(r'^resfbo/update/(?P<pk>\d+)/$', ReservationFBOUpdate.as_view(), name='resfbo-update'),
    re_path(r'^resfbo/delete/(?P<pk>\d+)/$', ReservationFBODelete.as_view(), name='resfbo-delete'),

    re_path(r'^blackout/list/$', BlackoutList.as_view(), name='blackout-list'),
    re_path(r'^blackout/info/(?P<pk>\d+)/$', BlackoutInfo.as_view(), name='blackout-info'),
    re_path(r'^blackout/create/$', BlackoutCreate.as_view(), name='blackout-create'),
    re_path(r'^blackout/update/(?P<pk>\d+)/$', BlackoutUpdate.as_view(), name='blackout-update'),
    re_path(r'^blackout/delete/(?P<pk>\d+)/$', BlackoutDelete.as_view(), name='blackout-delete'),

    re_path(r'^params/list/$', ResParamsList.as_view(), name='params-list'),
    re_path(r'^params/update/(?P<pk>\d+)/$', ResParamsUpdate.as_view(), name='params-update'),

    re_path(r'^res/calendar/$', ReservationCalendar, name='reservation-calendar'),
    re_path(r'^res/calendar/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/$', ReservationCalendar, name='reservation-cal-day'),
    re_path(r'^duty/calendar/$', DutyCalendar, name='duty-calendar'),
    re_path(r'^duty/calendar/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/$', DutyCalendar, name='duty-cal-day'),

    re_path(r'^res/mlist/$', ReservationListMobile, name='mobile-res'),

    re_path(r'^res_feed/$', reservation_feed, name='reservation-feed'),
    re_path(r'^res_move/$', reservation_move, name='reservation-move'),
    re_path(r'^duty_feed/$', duty_feed, name='duty-feed'),
]
