from django.conf.urls import url
from res.views import ResourceFBOList, ResourceFBOCreate, ResourceFBOUpdate, ResourceFBODelete
from res.views import ReservationList, ReservationInfo, ReservationCreate, ReservationUpdate, ReservationDelete
from res.views import ReservationFBOInfo, ReservationFBOCreate, ReservationFBOUpdate, ReservationFBODelete
from res.views import BlackoutList, BlackoutInfo, BlackoutCreate, BlackoutUpdate, BlackoutDelete
from res.views import ResParamsList, ResParamsUpdate
from res.views import ReservationCalendar, DutyCalendar, reservation_feed, reservation_move, duty_feed
from res.views import ReservationListMobile

urlpatterns = [

    url(r'^reservation/list/$', ReservationList, name='reservation-list'),
    url(r'^reservation/info/(?P<pk>\d+)/$', ReservationInfo.as_view(), name='reservation-info'),
    url(r'^reservation/create/$', ReservationCreate.as_view(), name='reservation-create'),
    url(r'^reservation/update/(?P<pk>\d+)/$', ReservationUpdate.as_view(), name='reservation-update'),
    url(r'^reservation/delete/(?P<pk>\d+)/$', ReservationDelete.as_view(), name='reservation-delete'),

    url(r'^resource/list/$', ResourceFBOList.as_view(), name='resource-list'),
    url(r'^resource/create/$', ResourceFBOCreate.as_view(), name='resource-create'),
    url(r'^resource/update/(?P<pk>\d+)/$', ResourceFBOUpdate.as_view(), name='resource-update'),
    url(r'^resource/delete/(?P<pk>\d+)/$', ResourceFBODelete.as_view(), name='resource-delete'),

    url(r'^resfbo/info/(?P<pk>\d+)/$', ReservationFBOInfo.as_view(), name='resfbo-info'),
    url(r'^resfbo/create/$', ReservationFBOCreate.as_view(), name='resfbo-create'),
    url(r'^resfbo/update/(?P<pk>\d+)/$', ReservationFBOUpdate.as_view(), name='resfbo-update'),
    url(r'^resfbo/delete/(?P<pk>\d+)/$', ReservationFBODelete.as_view(), name='resfbo-delete'),

    url(r'^blackout/list/$', BlackoutList.as_view(), name='blackout-list'),
    url(r'^blackout/info/(?P<pk>\d+)/$', BlackoutInfo.as_view(), name='blackout-info'),
    url(r'^blackout/create/$', BlackoutCreate.as_view(), name='blackout-create'),
    url(r'^blackout/update/(?P<pk>\d+)/$', BlackoutUpdate.as_view(), name='blackout-update'),
    url(r'^blackout/delete/(?P<pk>\d+)/$', BlackoutDelete.as_view(), name='blackout-delete'),

    url(r'^params/list/$', ResParamsList.as_view(), name='params-list'),
    url(r'^params/update/(?P<pk>\d+)/$', ResParamsUpdate.as_view(), name='params-update'),

    url(r'^res/calendar/$', ReservationCalendar, name='reservation-calendar'),
    url(r'^res/calendar/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/$', ReservationCalendar, name='reservation-cal-day'),
    url(r'^duty/calendar/$', DutyCalendar, name='duty-calendar'),
    url(r'^duty/calendar/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/$', DutyCalendar, name='duty-cal-day'),

    url(r'^res/mlist/$', ReservationListMobile, name='mobile-res'),

    url(r'^res_feed/$', reservation_feed, name='reservation-feed'),
    url(r'^res_move/$', reservation_move, name='reservation-move'),
    url(r'^duty_feed/$', duty_feed, name='duty-feed'),
]
