from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView
from django.contrib.auth.models import User
from rest_framework import viewsets
from . import serializers, models
from rest_framework.response import Response
import calendar
import datetime
from rest_framework.views import status
from datetime import date, timedelta
from dateutil import parser
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class ParameterLCView(ListCreateAPIView):
    serializer_class = serializers.ParameterSerializer
    queryset = models.Parameter.objects
#
#
# class ParameterRUDView(RetrieveUpdateDestroyAPIView):
#     serializer_class = serializers.ParameterSerializer
#     queryset = models.Parameter.objects
#     lookup_field = "id"
#     lookup_url_kwarg = "id"
#
#
class PlayerLCView(ListCreateAPIView):
    serializer_class = serializers.PlayerSerializer
    queryset = models.Player.objects


class ParameterTreeLCView(ListCreateAPIView):
    serializer_class = serializers.ParameterTreeSerializer
    queryset = models.ParameterTree.objects


class ReportLCView(ListCreateAPIView):
    serializer_class = serializers.ReportSerializer
    queryset = models.Report.objects

    def create(self, request, *args, **kwargs):
        data = request.data
        new_report = models.Report.objects.create(name=data['name'], frequency=data['frequency'], cutoff=data['cutoff'])

        new_report.save()
        for param in data['question']:
            print(param['id'])
            parameter_obj = models.ParameterTree.objects.get(id=param['id'])
            new_report.question.add(parameter_obj)
        for comp in data['companies']:
            comp_obj = models.Player.objects.get(player_id=comp['id'])
            new_report.companies.add(comp_obj)
        serializer = serializers.ReportSerializer(new_report)
        return Response(serializer.data)
    
class SectorPlayerLView(ListAPIView):
    serializer_class = serializers.SectorPlayerListSerializer
    queryset = models.Report.objects
#
#
# class ReportRUDView(RetrieveUpdateDestroyAPIView):
#     serializer_class = serializers.ReportSerializer
#     queryset = models.Report.objects
#     lookup_field = "id"
#     lookup_url_kwarg = "id"


# ignore
class ReportVersionLCView(ListCreateAPIView):
    serializer_class = serializers.ReportVersionGetSerializer
    queryset = models.ReportVersion.objects

    def create(self, request, *args, **kwargs):
        data = request.data
        report_obj = models.Report.objects.get(id=data['id'])
        # report_obj = models.Report.objects.get(id=data['report'])
        curr_instance = data['current_instance']
        company_obj = models.Player.objects.get(player_name=data['company'])
        # new_report_ver = models.ReportVersion.objects.create(name=data["name"], report=report_obj, company=data["company"])
        try:
        #check wrt instance id instead
            # new_report_ver = models.ReportVersion.objects.get(name=data["name"], report=report_obj, company=data["company"])
            new_report_ver = models.ReportVersion.objects.get(id=curr_instance['id'])
            print('exists')
            # update code for reportresult
            if new_report_ver:
                # start_date = datetime.date.today().replace(day=1)
                # end_date = date.today().replace(day=calendar.monthrange(date.today().year, date.today().month)[1])
                end_date = date.today().replace(day=1) - timedelta(days=1)
                start_date = date.today().replace(day=1) - timedelta(days=end_date.day)
                for i in data['questions']:
                    parametertree_obj = models.ParameterTree.objects.get(id=i['id'])
                    for j in i['sub_questions']:
                        parameter_obj = models.Parameter.objects.get(parameter_id=j['id'])
                        report_ver_obj = models.ReportVersion.objects.get(id=data['current_instance']['id'])
                        report_res, created = models.MainData.objects.update_or_create(parameter=parameter_obj,
                                                                                       parametertree=parametertree_obj,
                                                                                       report_version=report_ver_obj,
                                                                                       source='Benchmark', #renamed
                                                                                       player=company_obj,
                                                                                       start_date=start_date,
                                                                                       end_date=end_date,
                                                                                    defaults={'value': j['current_value'],
                                                                                              'date_created':datetime.date.today()})
                        report_res.save()
        except models.ReportVersion.DoesNotExist:
            # no need to create new entry in report result as this part will be triggered by scheduler
            new_report_ver = models.ReportVersion.objects.create(name=data["name"], report=report_obj,
                                                                 company=data['company'])
            new_report_ver.save()

        serializer = serializers.ReportVersionSerializer(new_report_ver)
        return Response(serializer.data)


class ReportVersionLView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.ReportVersionGetSerializer
    queryset = models.ReportVersion.objects


class ReportVersionCView(CreateAPIView):
    serializer_class = serializers.ReportVersionGetSerializer
    queryset = models.ReportVersion.objects

    def create(self, request, *args, **kwargs):
        data = request.data
        report_obj = models.Report.objects.get(id=data['id'])
        curr_instance = data['current_instance']
        time = curr_instance['created_at']
        date_time = parser.parse(time.split('T')[0])
        company_obj = models.Player.objects.get(player_name=data['company'])
        # new_report_ver = models.ReportVersion.objects.create(name=data["name"], report=report_obj, company=data["company"])
        try:
            new_report_ver = models.ReportVersion.objects.get(id=curr_instance['id'])
            new_report_ver.is_submitted = data['is_submitted']
            new_report_ver.filled_count = data['filled_count']
            new_report_ver.email = data['email']
            # update code for reportresult
            if new_report_ver:
                new_report_ver.save()
                end_date = date_time.date().replace(day=1) - timedelta(days=1)
                start_date = date_time.date().replace(day=1) - timedelta(days=end_date.day)
                for i in data['questions']:
                    parametertree_obj = models.ParameterTree.objects.get(id=i['id'])
                    for j in i['sub_questions']:
                        try:
                            # doing this bcoz data can be string /blank/integer etc
                            j['current_value'] = float(j['current_value'])
                            parameter_obj = models.Parameter.objects.get(parameter_id=j['id'])
                            report_ver_obj = models.ReportVersion.objects.get(id=data['current_instance']['id'])
                            report_res, created = models.MainData.objects.update_or_create(parameter=parameter_obj,
                                                                                           parametertree=parametertree_obj,
                                                                                           report_version=report_ver_obj,
                                                                                           source='Benchmark',  # rename
                                                                                           player=company_obj,
                                                                                           start_date=start_date,
                                                                                           end_date=end_date,
                                                                                           defaults={'value': j['current_value'],
                                                                                                    'date_created': datetime.date.today()})
                            report_res.save()
                        except:
                            print('error')
        except models.ReportVersion.DoesNotExist:
            # no need to create new entry in report result as this part will be triggered by scheduler
            new_report_ver = models.ReportVersion.objects.create(name=data["name"], report=report_obj,
                                                                 company=data['company'])
            new_report_ver.save()

        serializer = serializers.ReportVersionSerializer(new_report_ver)
        return Response(serializer.data)


# # wont work if you dont have lookup field id defined by you make id auto field
class ReportVersionRUDView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.ReportVersionSerializer
    queryset = models.ReportVersion.objects
    lookup_field = "id"
    lookup_url_kwarg = "id"


class ReportResultLCView(ListCreateAPIView):
    serializer_class = serializers.ReportResultSerializer
    queryset = models.MainData.objects

    def create(self, request, *args, **kwargs):
        data = request.data
        report_ver_obj = models.ReportVersion.objects.get(id=data['report_version'])
        parameter_obj = models.Parameter.objects.get(parameter_id=data['parameter'])
        parametertree_obj = models.ParameterTree.objects.get(id=data['parametertree'])
        player = data['player']
        player_obj = models.Player.objects.get(player_id=player)
        start_date = datetime.date.today().replace(day=1)
        if data['start_date']:
            start_date = data['start_date']
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            start_date = start_date.date()
        end_date = date.today().replace(day=calendar.monthrange(date.today().year, date.today().month)[1])
        if data['end_date']:
            end_date = data['end_date']
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date.date()
        date_created = datetime.date.today()
        new_result_entry, created = models.MainData.objects.update_or_create(parameter=parameter_obj,
                                                                        parametertree=parametertree_obj,
                                                                        report_version=report_ver_obj,
                                                                             source=data['source'],
                                                                        player=player_obj, start_date=start_date,
                                                                        end_date=end_date,
                                                                        defaults={'value': data['value']
                                                                                  })
        new_result_entry.save()
        serializer = serializers.ReportResultSerializer(new_result_entry)
        return Response(serializer.data)


class ReportVersionIDView(CreateAPIView):

    def post(self, request):
        start_date = request.data.get('start_date')
        start_date = datetime.datetime.strptime(start_date, '%d/%m/%y').date()
        end_date = request.data.get('end_date')
        end_date = datetime.datetime.strptime(end_date, '%d/%m/%y').date()
        company_name = request.data.get('company_name')
        question_name = request.data.get('question_name')
        report_version = models.ReportVersion.objects.filter(company = company_name, date_created__range=[start_date,end_date])[0]
        report_id = report_version.report_id
        questions = models.ParameterTree.objects.filter(report=report_id)
        question_id = 107
        for i in questions:
            if i.question == question_name:
                question_id = i.id
                break
        return Response({'report_version_id': report_version.id, 'question_id': question_id}, status=status.HTTP_200_OK)


class QuestionIDView(CreateAPIView):

    def post(self, request):
        report_version_id = request.data.get('report_version_id')
        question_name = request.data.get('question_name')
        report_id = models.ReportVersion.objects.filter(id=report_version_id)[0].report_id
        questions = models.ParameterTree.objects.filter(report=report_id)
        question_id = 0
        for i in questions:
            if i.question == question_name:
                question_id = i.id
                break
        return Response({'question_id': question_id}, status=status.HTTP_200_OK)


class AuditTableLCView(ListCreateAPIView):
    serializer_class = serializers.AuditTableSerializer
    queryset = models.AuditTable.objects

    def get_queryset(self):
        today = datetime.date.today()
        query_params = self.request.query_params
        month = query_params.get('month')
        if month:
            self.queryset = self.queryset.filter(date__year=today.year, date__month=month)
        qs = self.queryset
        form_id = self.request.query_params.get('form_id')
        print(form_id)
        if form_id:
            qs = qs.filter(form_id=form_id)
        return qs


class AuditReportVersionLCView(ListCreateAPIView):
    serializer_class = serializers.AuditReportVersionSerializer
    queryset = models.ReportVersion.objects

    def get_queryset(self):
        today = datetime.date.today()
        year = today.year
        query_params = self.request.query_params
        month = query_params.get('month')
        company = query_params.get('company')
        if month:
            if company:
                self.queryset = self.queryset.filter(date_created__year=today.year, date_created__month=month,
                                                     company__contains=company)
            else:
                self.queryset = self.queryset.filter(date_created__year=today.year, date_created__month=month)
        else:
            if company:
                self.queryset = self.queryset.filter(company__contains = company)
            else:
                self.queryset = self.queryset.filter(date_created__year=today.year, date_created__month=today.month-1)
        return self.queryset