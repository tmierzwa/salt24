from django.urls import re_path
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

app_name = "ato"

urlpatterns = [
    re_path(r'^$', TrainingInstList.as_view(), name='training-inst-list'),
    re_path(r'^trinst/details/(?P<pk>\d+)/$', TrainingInstDetails.as_view(), name='training-inst-details'),
    re_path(r'^trinst/create/$', TrainingInstCreate, name='training-inst-create'),
    re_path(r'^trinst/update/(?P<pk>\d+)/$', TrainingInstUpdate.as_view(), name='training-inst-update'),
    re_path(r'^trinst/delete/(?P<pk>\d+)/$', TrainingInstDelete.as_view(), name='training-inst-delete'),
    re_path(r'^trinst/pass/(?P<pk>\d+)/$', TrainingInstPass, name='training-inst-pass'),

    re_path(r'^phinst/details/(?P<pk>\d+)/$', PhaseInstDetails.as_view(), name='phase-inst-details'),
    re_path(r'^phinst/create/(?P<training_inst_id>\d+)/$', PhaseInstCreate.as_view(), name='phase-inst-create'),
    re_path(r'^phinst/update/(?P<pk>\d+)/$', PhaseInstUpdate.as_view(), name='phase-inst-update'),
    re_path(r'^phinst/delete/(?P<pk>\d+)/$', PhaseInstDelete.as_view(), name='phase-inst-delete'),
    re_path(r'^phinst/pass/(?P<pk>\d+)/$', PhaseInstPass, name='phase-inst-pass'),

    re_path(r'^exinst/details/(?P<pk>\d+)/$', ExerciseInstDetails.as_view(), name='exercise-inst-details'),
    re_path(r'^exinst/create/(?P<phase_inst_id>\d+)/$', ExerciseInstCreate.as_view(), name='exercise-inst-create'),
    re_path(r'^exinst/update/(?P<pk>\d+)/$', ExerciseInstUpdate.as_view(), name='exercise-inst-update'),
    re_path(r'^exinst/delete/(?P<pk>\d+)/$', ExerciseInstDelete.as_view(), name='exercise-inst-delete'),
    re_path(r'^exinst/pass/(?P<pk>\d+)/$', ExerciseInstPass, name='exercise-inst-pass'),

    re_path(r'^exoper/create/(?P<exercise_inst_id>\d+)/$', ExerciseOperCreate, name='exercise-oper-create'),
    re_path(r'^exoper/update/(?P<pk>\d+)/$', ExerciseOperUpdate.as_view(), name='exercise-oper-update'),
    re_path(r'^exoper/delete/(?P<pk>\d+)/$', ExerciseOperDelete.as_view(), name='exercise-oper-delete'),

    re_path(r'^card/list/(?P<training_inst_id>\d+)/$', CardEntryList.as_view(), name='card-entry-list'),
    re_path(r'^card/report/(?P<training_inst_id>\d+)/$', CardReport.as_view(), name='card-report'),
    re_path(r'^card/details/(?P<pk>\d+)/$', CardEntryDetails.as_view(), name='card-entry-details'),
    re_path(r'^card/create/(?P<training_inst_id>\d+)/$', CardEntryCreate.as_view(), name='card-entry-create'),
    re_path(r'^card/update/(?P<pk>\d+)/$', CardEntryUpdate.as_view(), name='card-entry-update'),
    re_path(r'^card/delete/(?P<pk>\d+)/$', CardEntryDelete.as_view(), name='card-entry-delete'),

    re_path(r'^training/list/$', TrainingList.as_view(), name='training-list'),
    re_path(r'^training/details/(?P<pk>\d+)/$', TrainingDetails.as_view(), name='training-details'),
    re_path(r'^training/create/$', TrainingCreate.as_view(), name='training-create'),
    re_path(r'^training/update/(?P<pk>\d+)/$', TrainingUpdate.as_view(), name='training-update'),
    re_path(r'^training/delete/(?P<pk>\d+)/$', TrainingDelete.as_view(), name='training-delete'),

    re_path(r'^phase/details/(?P<pk>\d+)/$', PhaseDetails.as_view(), name='phase-details'),
    re_path(r'^phase/create/(?P<training_id>\d+)/$', PhaseCreate.as_view(), name='phase-create'),
    re_path(r'^phase/update/(?P<pk>\d+)/$', PhaseUpdate.as_view(), name='phase-update'),
    re_path(r'^phase/delete/(?P<pk>\d+)/$', PhaseDelete.as_view(), name='phase-delete'),

    re_path(r'^exercise/details/(?P<pk>\d+)/$', ExerciseDetails.as_view(), name='exercise-details'),
    re_path(r'^exercise/create/(?P<phase_id>\d+)/$', ExerciseCreate.as_view(), name='exercise-create'),
    re_path(r'^exercise/update/(?P<pk>\d+)/$', ExerciseUpdate.as_view(), name='exercise-update'),
    re_path(r'^exercise/delete/(?P<pk>\d+)/$', ExerciseDelete.as_view(), name='exercise-delete'),

    re_path(r'^instructor/list/$', InstructorList.as_view(), name='instr-list'),
    re_path(r'^instructor/info/(?P<pk>\d+)/$', InstructorInfo.as_view(), name='instr-info'),
    re_path(r'^instructor/trainings/(?P<type>\w+)/(?P<pk>\d+)/$', InstructorTrainings.as_view(), name='instr-trainings'),
    re_path(r'^instructor/flights/(?P<pk>\d+)/$', InstructorFlights.as_view(), name='instr-flights'),
    re_path(r'^instructor/create/$', InstructorCreate.as_view(), name='instr-create'),
    re_path(r'^instructor/update/(?P<pk>\d+)/$', InstructorUpdate.as_view(), name='instr-update'),
    re_path(r'^instructor/delete/(?P<pk>\d+)/$', InstructorDelete.as_view(), name='instr-delete'),

    re_path(r'^student/list/$', StudentList.as_view(), name='student-list'),
    re_path(r'^student/info/(?P<pk>\d+)/$', StudentInfo.as_view(), name='student-info'),
    re_path(r'^student/flights/(?P<pk>\d+)/$', StudentFlights.as_view(), name='student-flights'),
    re_path(r'^student/account/(?P<pk>\d+)/$', StudentInfo.as_view(), name='student-account'),
    re_path(r'^student/trainings/(?P<type>\w+)/(?P<pk>\d+)/$', StudentTrainings.as_view(), name='student-trainings'),
    re_path(r'^student/create/$', StudentCreate.as_view(), name='student-create'),
    re_path(r'^student/update/(?P<pk>\d+)/$', StudentUpdate.as_view(), name='student-update'),
    re_path(r'^student/delete/(?P<pk>\d+)/$', StudentDelete.as_view(), name='student-delete'),

    re_path(r'^_update/$', update_phases, name='update-phases'),

]
