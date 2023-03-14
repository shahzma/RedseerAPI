from .api_views import PlayerLCView, ParameterLCView, ReportResultLCView, ReportLCView, SectorPlayerLView, ParameterTreeLCView, ReportVersionArchivedLView,\
    ReportVersionRUDView, ReportVersionLView, ReportVersionCView, UserViewSet, ReportVersionIDView,QuestionIDView,\
    AuditTableLCView, AuditReportVersionLCView, ValidateFormAPI
from rest_framework import routers
from django.urls import path, include

router = routers.DefaultRouter()
router.register('users', UserViewSet)

parameter_urls = [
    path("", ParameterLCView.as_view(), name="lc"),
]

player_urls = [
    path("", PlayerLCView.as_view(), name="lc"),
]

parametertree_urls = [
    path("", ParameterTreeLCView.as_view(), name="lc"),
    # path("<uuid:id>", ParameterTreeRUDView.as_view(), name="rud")
]

report_urls = [
    path("", ReportLCView.as_view(), name="lc"),
    # path("<uuid:id>", ReportRUDView.as_view(), name="rud")
]

sector_player_urls = [
    path("", SectorPlayerLView.as_view(), name="lc"),
]

reportversion_urls = [
    path("", ReportVersionLView.as_view(), name="l"),
    path("<int>/<int:id>/", ReportVersionRUDView.as_view(), name="rud")
]

reportversion_archived_urls = [
    path("", ReportVersionArchivedLView.as_view(), name="lc"),
    path('<str:month>/<int:sectorId>/<str:playerName>', ReportVersionArchivedLView.as_view(), name="l"),
]

formresult_urls = [
    path("<int>/<int:id>/", ReportVersionCView.as_view(), name="c")
]

reportresult_urls = [
    path("", ReportResultLCView.as_view(), name="lc"),
]

formID_urls = [
    path("", ReportVersionIDView.as_view(), name="lc"),
]

form_validate_urls = [
    path("", ValidateFormAPI.as_view(), name="lc"),
]

questionID_urls = [
    path("", QuestionIDView.as_view(), name="lc"),
]

audittable_urls = [
    path("", AuditTableLCView.as_view(), name='lc')
]

atrv_urls = [
    path("", AuditReportVersionLCView.as_view(), name='lc')
]

#
# subquestions_urls = [
#     path("", SubQuestionLCView.as_view(), name="lc"),
#     path("<uuid:id>", SubQuestionRUDView.as_view(), name="rud")
# ]
#
# questions_urls = [
#     path("", QuestionLCView.as_view(), name="lc"),
#     path("<uuid:id>", QuestionRUDView.as_view(), name="rud")
# ]
#
# insideForm_urls = [
#     path("", insideFormLCView.as_view(), name='lc')
# ]
#
urlpatterns = [
    path('', include(router.urls)),
    path("player/", include((player_urls, "player"), namespace="player")),
    path("parameter/", include((parameter_urls, "parameter"), namespace="parameter")),
    path("parametertree/", include((parametertree_urls, "parametertree"), namespace="parametertree")),
    path("reports/", include((report_urls, "report"), namespace="report")),
    path("sectors-players/", include((sector_player_urls, "report"), namespace="report")),
    path("forms/", include((reportversion_urls, "reportversion"), namespace="reportversion")),
    path("forms-archived/", include((reportversion_archived_urls, "reportversion_archived"), namespace="reportversion_archived")),
    path("formresult/", include((formresult_urls, "formresult"), namespace="formresult")),
    path("form-validate/", include((form_validate_urls, "form_validate"), namespace="form_validate")),
    path("reportresult/", include((reportresult_urls, "reportresult"), namespace="reportresult")),
    path("formID/", include((formID_urls, "formID"), namespace="formID")),
    path("questionID/", include((questionID_urls, "questionID"), namespace="questionID")),
    path("audittable/", include((audittable_urls, "audittable"), namespace="audittable")),
    path("atrv/", include((atrv_urls, "atrv"), namespace="atrv")),
    # path("subquestions/", include((subquestions_urls, "subquestions"), namespace="subquestions")),
    # path("questions/", include((questions_urls, "questions"), namespace="questions")),
    # path("insideForm/", include((insideForm_urls, "insideForm"), namespace="insideForm"))
]