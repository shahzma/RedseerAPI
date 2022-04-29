from .api_views import PlayerLCView, ParameterLCView, ReportResultLCView, ReportLCView, ParameterTreeLCView,\
    ReportVersionRUDView, ReportVersionLView, ReportVersionCView, UserViewSet
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

reportversion_urls = [
    path("", ReportVersionLView.as_view(), name="l"),
    path("<int>/<int:id>/", ReportVersionRUDView.as_view(), name="rud")
]

formresult_urls = [
    path("<int>/<int:id>/", ReportVersionCView.as_view(), name="c")
]

reportresult_urls = [
    path("", ReportResultLCView.as_view(), name="lc"),
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
    path("forms/", include((reportversion_urls, "reportversion"), namespace="reportversion")),
    path("formresult/", include((formresult_urls, "formresult"), namespace="formresult")),
    path("reportresult/", include((reportresult_urls, "reportresult"), namespace="reportresult")),
    # path("subquestions/", include((subquestions_urls, "subquestions"), namespace="subquestions")),
    # path("questions/", include((questions_urls, "questions"), namespace="questions")),
    # path("insideForm/", include((insideForm_urls, "insideForm"), namespace="insideForm"))
]