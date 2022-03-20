# from .api_views import ParameterRUDView, ParameterLCView, CompanyRUDView, CompanyLCView, ParameterTreeLCView, \
#     ParameterTreeRUDView, ReportLCView, ReportRUDView, ReportVersionLCView, ReportVersionRUDView, ReportResultLCView, \
#     ReportResultRUDView, SubQuestionRUDView, SubQuestionLCView, QuestionLCView, QuestionRUDView, insideFormLCView
#
from .api_views import PlayerLCView, ParameterLCView, ReportResultLCView, ReportLCView, ParameterTreeLCView,\
    ReportVersionLCView, ReportVersionRUDView

from django.urls import path, include

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
    path("", ReportVersionLCView.as_view(), name="lc"),
    path("<int>/<int:id>", ReportVersionRUDView.as_view(), name="rud")
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
    path("player/", include((player_urls, "player"), namespace="player")),
    path("parameter/", include((parameter_urls, "parameter"), namespace="parameter")),
    path("parametertree/", include((parametertree_urls, "parametertree"), namespace="parametertree")),
    path("reports/", include((report_urls, "report"), namespace="report")),
    path("forms/", include((reportversion_urls, "reportversion"), namespace="reportversion")),
    path("reportresult/", include((reportresult_urls, "reportresult"), namespace="reportresult")),
    # path("subquestions/", include((subquestions_urls, "subquestions"), namespace="subquestions")),
    # path("questions/", include((questions_urls, "questions"), namespace="questions")),
    # path("insideForm/", include((insideForm_urls, "insideForm"), namespace="insideForm"))
]