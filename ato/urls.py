from django.conf.urls import url
from ato.views import TrainingList, TrainingDetails, TrainingCreate, TrainingUpdate, TrainingDelete
from ato.views import PhaseDetails, PhaseCreate, PhaseUpdate, PhaseDelete
from ato.views import ExerciseDetails, ExerciseCreate, ExerciseUpdate, ExerciseDelete
from ato.views import InstructorList, InstructorCreate, InstructorUpdate, InstructorDelete
from ato.views import InstructorInfo, InstructorFlights, InstructorTrainings
from ato.views import StudentList, StudentCreate, StudentUpdate, StudentDelete
from ato.views import StudentInfo, StudentFlights, StudentTrainings
from ato.views import TrainingInstList, TrainingInstDetails, TrainingInstCreate, TrainingInstUpdate, TrainingInstDelete, TrainingInstPass
from ato.views import PhaseInstDetails, PhaseInstCreate, PhaseInstUpdate, PhaseInstDelete, PhaseInstPass
from ato.views import ExerciseInstDetails, ExerciseInstCreate, ExerciseInstUpdate, ExerciseInstDelete, ExerciseInstPass
from ato.views import ExerciseOperCreate, ExerciseOperUpdate, ExerciseOperDelete
from ato.views import CardEntryList, CardReport, CardEntryDetails, CardEntryCreate, CardEntryUpdate, CardEntryDelete


from ato.loaders import update_phases

urlpatterns = [

    url(r'^$', TrainingInstList.as_view(), name='training-inst-list'),
    url(r'^trinst/details/(?P<pk>\d+)/$', TrainingInstDetails.as_view(), name='training-inst-details'),
    url(r'^trinst/create/$', TrainingInstCreate, name='training-inst-create'),
    url(r'^trinst/update/(?P<pk>\d+)/$', TrainingInstUpdate.as_view(), name='training-inst-update'),
    url(r'^trinst/delete/(?P<pk>\d+)/$', TrainingInstDelete.as_view(), name='training-inst-delete'),
    url(r'^trinst/pass/(?P<pk>\d+)/$', TrainingInstPass, name='training-inst-pass'),

    url(r'^phinst/details/(?P<pk>\d+)/$', PhaseInstDetails.as_view(), name='phase-inst-details'),
    url(r'^phinst/create/(?P<training_inst_id>\d+)/$', PhaseInstCreate.as_view(), name='phase-inst-create'),
    url(r'^phinst/update/(?P<pk>\d+)/$', PhaseInstUpdate.as_view(), name='phase-inst-update'),
    url(r'^phinst/delete/(?P<pk>\d+)/$', PhaseInstDelete.as_view(), name='phase-inst-delete'),
    url(r'^phinst/pass/(?P<pk>\d+)/$', PhaseInstPass, name='phase-inst-pass'),

    url(r'^exinst/details/(?P<pk>\d+)/$', ExerciseInstDetails.as_view(), name='exercise-inst-details'),
    url(r'^exinst/create/(?P<phase_inst_id>\d+)/$', ExerciseInstCreate.as_view(), name='exercise-inst-create'),
    url(r'^exinst/update/(?P<pk>\d+)/$', ExerciseInstUpdate.as_view(), name='exercise-inst-update'),
    url(r'^exinst/delete/(?P<pk>\d+)/$', ExerciseInstDelete.as_view(), name='exercise-inst-delete'),
    url(r'^exinst/pass/(?P<pk>\d+)/$', ExerciseInstPass, name='exercise-inst-pass'),

    url(r'^exoper/create/(?P<exercise_inst_id>\d+)/$', ExerciseOperCreate, name='exercise-oper-create'),
    url(r'^exoper/update/(?P<pk>\d+)/$', ExerciseOperUpdate.as_view(), name='exercise-oper-update'),
    url(r'^exoper/delete/(?P<pk>\d+)/$', ExerciseOperDelete.as_view(), name='exercise-oper-delete'),

    url(r'^card/list/(?P<training_inst_id>\d+)/$', CardEntryList.as_view(), name='card-entry-list'),
    url(r'^card/report/(?P<training_inst_id>\d+)/$', CardReport.as_view(), name='card-report'),
    url(r'^card/details/(?P<pk>\d+)/$', CardEntryDetails.as_view(), name='card-entry-details'),
    url(r'^card/create/(?P<training_inst_id>\d+)/$', CardEntryCreate.as_view(), name='card-entry-create'),
    url(r'^card/update/(?P<pk>\d+)/$', CardEntryUpdate.as_view(), name='card-entry-update'),
    url(r'^card/delete/(?P<pk>\d+)/$', CardEntryDelete.as_view(), name='card-entry-delete'),

    url(r'^training/list/$', TrainingList.as_view(), name='training-list'),
    url(r'^training/details/(?P<pk>\d+)/$', TrainingDetails.as_view(), name='training-details'),
    url(r'^training/create/$', TrainingCreate.as_view(), name='training-create'),
    url(r'^training/update/(?P<pk>\d+)/$', TrainingUpdate.as_view(), name='training-update'),
    url(r'^training/delete/(?P<pk>\d+)/$', TrainingDelete.as_view(), name='training-delete'),

    url(r'^phase/details/(?P<pk>\d+)/$', PhaseDetails.as_view(), name='phase-details'),
    url(r'^phase/create/(?P<training_id>\d+)/$', PhaseCreate.as_view(), name='phase-create'),
    url(r'^phase/update/(?P<pk>\d+)/$', PhaseUpdate.as_view(), name='phase-update'),
    url(r'^phase/delete/(?P<pk>\d+)/$', PhaseDelete.as_view(), name='phase-delete'),

    url(r'^exercise/details/(?P<pk>\d+)/$', ExerciseDetails.as_view(), name='exercise-details'),
    url(r'^exercise/create/(?P<phase_id>\d+)/$', ExerciseCreate.as_view(), name='exercise-create'),
    url(r'^exercise/update/(?P<pk>\d+)/$', ExerciseUpdate.as_view(), name='exercise-update'),
    url(r'^exercise/delete/(?P<pk>\d+)/$', ExerciseDelete.as_view(), name='exercise-delete'),

    url(r'^instructor/list/$', InstructorList.as_view(), name='instr-list'),
    url(r'^instructor/info/(?P<pk>\d+)/$', InstructorInfo.as_view(), name='instr-info'),
    url(r'^instructor/trainings/(?P<type>\w+)/(?P<pk>\d+)/$', InstructorTrainings.as_view(), name='instr-trainings'),
    url(r'^instructor/flights/(?P<pk>\d+)/$', InstructorFlights.as_view(), name='instr-flights'),
    url(r'^instructor/create/$', InstructorCreate.as_view(), name='instr-create'),
    url(r'^instructor/update/(?P<pk>\d+)/$', InstructorUpdate.as_view(), name='instr-update'),
    url(r'^instructor/delete/(?P<pk>\d+)/$', InstructorDelete.as_view(), name='instr-delete'),

    url(r'^student/list/$', StudentList.as_view(), name='student-list'),
    url(r'^student/info/(?P<pk>\d+)/$', StudentInfo.as_view(), name='student-info'),
    url(r'^student/flights/(?P<pk>\d+)/$', StudentFlights.as_view(), name='student-flights'),
    url(r'^student/account/(?P<pk>\d+)/$', StudentInfo.as_view(), name='student-account'),
    url(r'^student/trainings/(?P<type>\w+)/(?P<pk>\d+)/$', StudentTrainings.as_view(), name='student-trainings'),
    url(r'^student/create/$', StudentCreate.as_view(), name='student-create'),
    url(r'^student/update/(?P<pk>\d+)/$', StudentUpdate.as_view(), name='student-update'),
    url(r'^student/delete/(?P<pk>\d+)/$', StudentDelete.as_view(), name='student-delete'),

    url(r'^_update/$', update_phases, name='update-phases'),

]
