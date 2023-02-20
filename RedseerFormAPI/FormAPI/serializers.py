import datetime
from django.contrib.auth.models import User
from datetime import date, timedelta
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from .models import Player, Parameter, MainData, Report, ParameterTree, ReportVersion, AuditTable, ReportQuestion
from random import randrange


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        print(user)
        Token.objects.create(user=user)
        return user


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['player_id', 'player_name', 'industry_id']
        read_only_fields = ['player_id']


class ParameterSerializer(serializers.ModelSerializer):
    sub_question = serializers.CharField(source='parameter_name')
    id = serializers.IntegerField(source='parameter_id')

    class Meta:
        model = Parameter
        fields = ['id', 'sub_question']
        read_only_fields = ['id', 'parameter_id']

class ParameterTreeSerializer(serializers.ModelSerializer):
    aggregate = serializers.BooleanField(source='summate')
    sub_questions = ParameterSerializer(source='parameters', many=True, read_only=True)

    class Meta:
        model = ParameterTree
        fields = ['id', 'aggregate', 'question', 'sub_questions']
        read_only_fields = ['id']


class ReportSerializer(serializers.ModelSerializer):
    # parameters = ParameterTreeSerializer(many=True, read_only=True)
    companies = PlayerSerializer(many=True, read_only=True)
    questions = ParameterTreeSerializer(source='question', many=True, read_only=True)
    deadline_days = serializers.IntegerField(source='cutoff')
    schedule = serializers.CharField(source='frequency')

    def to_representation(self, instance):
        rep = super(ReportSerializer, self).to_representation(instance)
        time_codes = {'1': "Weekly", '2': "Monthly", '3': "Quarterly"}
        schedule_val = time_codes[rep['schedule']]
        rep['schedule'] = schedule_val
        rep['question_count'] = len(rep['questions'])
        # print(rep['companies'][0])
        rep['company'] = [d['player_name'] for d in rep['companies'] if 'player_name' in d]
        rep.pop('companies')
        # rep['filled_count'] = Report.objects.count()
        rep['filled_count'] = 1
        rep['last_modified_date'] = datetime.date.today()
        rep['is_submitted'] = False
        rep['current_instance'] = {
            'id': rep['id'],
            'created_at': datetime.date.today()
        }
        return rep

    class Meta:
        model = Report
        fields = ['id', 'name', 'companies', 'schedule', 'questions', 'deadline_days']
        read_only_fields = ['id']

#Listing the sector and their player
class SectorPlayerListSerializer(serializers.ModelSerializer):
    companies = PlayerSerializer(many=True, read_only=True)
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['company'] = []
        for d in rep['companies']:
            if 'player_name' in d and 'player_id' in d:
                playerobject = {}
                playerobject['name'] = d['player_name']
                playerobject['id'] = d['player_id']
                rep['company'].append(playerobject)
        rep.pop('companies')
        return rep
    class Meta:
        model = Report
        fields = ['id', 'name', 'companies']
        read_only_fields = ['id']

class ReportResultSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        rep = super(ReportResultSerializer, self).to_representation(instance)
        rep['current_value'] = rep['value']
        rep.pop('value')
        return rep

    class Meta:
        model = MainData
        fields = "__all__"
        read_only_fields = ['id']

# use for land c
class ReportVersionGetSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['current_instance'] = {
            'id': rep['id'],
            'created_at': rep['date_created']
        }
        rep['last_modified_date'] = datetime.date.today()
        # print(Report.objects.filter(id=instance.report.id)[0].question_count) #= none as question is many to many
        # remove questions in get and add for rud
        # rep_details = ReportSerializer(instance.report).data
        # rep_details.pop('questions')
        # rep.pop('report')
        curr_report_object = Report.objects.filter(id=instance.report.id)[0]
        rep['question_count'] = curr_report_object.question_count
        rep.pop('date_created')
        rep['schedule'] = "monthly"  # get it from report object if there are some whanges wrt schedult
        rep['deadline_days'] = 30  # get it from report object if  changes .Question count from report version or report
        rep['industry_name'] = curr_report_object.name
        # rep['excel_link'] = Player.objects.filter(player_name=instance.company)[0].excel_link
        # rep['id'] = rep['report']
        # rep = {**rep_details, **rep}
        return rep

    class Meta:
        model = ReportVersion
        fields = "__all__"
        read_only_fields = ['id']

class ReportVersionArchivedGetSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        curr_report_object = Report.objects.filter(id=instance.report.id)[0]
        rep['question_count'] = curr_report_object.question_count
        rep['schedule'] = "monthly" 
        rep['deadline_days'] = 30
        return rep

    class Meta:
        model = ReportVersion
        fields = "__all__"
        read_only_fields = ['id']

#ignore
# class ReportVersionPostSerializer(serializers.ModelSerializer):

#     def to_representation(self, instance):
#         rep = super().to_representation(instance)
#         rep['current_instance'] = {
#             'id': rep['id'],
#             'created_at': rep['date_created']
#         }
#         rep['last_modified_date'] = datetime.date.today()
#         # remove questions in get and add for rud
#         rep_details = ReportSerializer(instance.report).data
#         rep_details.pop('questions')
#         rep.pop('date_created')
#         rep['id'] = rep['report']
#         rep['industry_name'] = Report.objects.filter(id=instance.report.id)[0].name
#         rep = {**rep_details, **rep}
#         return rep

#     class Meta:
#         model = ReportVersion
#         fields = "__all__"
#         read_only_fields = ['id']


# use for rud bcoz we want questions there
class ReportVersionSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['current_instance'] = {
            'id': rep['id'],
            'created_at': rep['date_created']
        }
        # rep['is_submitted'] = False
        rep['last_modified_date'] = datetime.date.today()
        # print(Report.objects.filter(id=instance.report.id)[0].question) = none as question is many to many
        rep_details = ReportSerializer(instance.report).data
        # # is a list.testing for instance-id = 7
        all_ques_sequence = ReportQuestion.objects.filter(report=instance.report)
        current_rep_results = MainData.objects.filter(report_version=instance.id)
        # # getting all previous ids which is less than current id and are of same report instance and
        # then choosing last3
        ids=[a.id for a in ReportVersion.objects.filter(report=instance.report,
                                                        id__lt=instance.id,
                                                        company=instance.company).order_by('-id')[:3]]
        print(ids)
        # getting form report result based on previous ids
        last_report_results=MainData.objects.filter(report_version__in=ids)
        for i in rep_details['questions']:
        # i is a dict
            current_ques_sequence = all_ques_sequence.filter(parametertree=i['id']).values()[0]['sequence']
            i['sequence'] = current_ques_sequence
            for j in current_rep_results:
                if i['id'] == j.parametertree.id: #all 37  questions
                    for k in i['sub_questions']:
                        # k['current_value'] = None
                        if k['id'] == j.parameter.parameter_id:
                            k['current_value'] = j.value

        for i in rep_details['questions']:
            for j in i['sub_questions']:
                last_val = ''
                for k in last_report_results:
                    if i['id'] == k.parametertree.id and j['id'] == k.parameter.parameter_id:
                        last_val = last_val+' '+str(k.value)
                j['last_value'] = last_val


        # rep.pop('report')
        rep.pop('date_created')
        # rep.pop('report_result')
        # rep_result = ReportResultSerializer(instance.id).data
        # print(rep_result)
        rep['industry_name'] = Report.objects.filter(id=instance.report.id)[0].name
        rep['id'] = rep_details['id']
        print(Player.objects.filter(player_name=instance.company))
        try:
            rep['excel_link'] = Player.objects.filter(player_name=instance.company)[0].excel_link
        except:
            rep['excel_link'] = ''
        rep = {**rep_details, **rep}
        return rep

    class Meta:
        model = ReportVersion
        fields = "__all__"
        read_only_fields = ['id']


class AuditTableSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['form_name'] = instance.form_id.name
        rep['form_date'] = instance.date
        return rep

    class Meta:
        model = AuditTable
        fields = "__all__"


class AuditReportVersionSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep.pop('name')
        rep.pop('filled_count')
        rep.pop('is_submitted')
        date_created = instance.date_created.date()
        try:
            last_date_day = Player.objects.filter(player_name=instance.company)[0].last_date_day
        except:
            last_date_day = 23
        last_date = date_created.replace(day=last_date_day)
        rep['last_date'] = last_date
        rep['sector'] = Report.objects.filter(id = instance.report_id)[0].name
        rep['sub-sector'] = 'Industry'
        rep['submission_attempt_sub_maker'] = len(AuditTable.objects.filter(form_id = instance.id , user_level = 1))
        rep['submission_attempt_maker'] = len(AuditTable.objects.filter(form_id = instance.id, user_level = 2))
        rep['submission_attempt_checker'] = len(AuditTable.objects.filter(form_id = instance.id, user_level = 3))
        rep['submission_attempt_reviewer'] = len(AuditTable.objects.filter(form_id = instance.id, user_level = 4))
        final_reviewer_arr = AuditTable.objects.filter(form_id = instance.id, user_level = 5)
        rep['submission_attempt_final_reviewer'] = len(AuditTable.objects.filter(form_id = instance.id, user_level = 5))
        submission_date = last_date
        if (final_reviewer_arr):
            # submission_date = final_reviewer_arr[-1].date.date()
            submission_date = final_reviewer_arr.reverse()[0].date.date()
            if submission_date<=last_date:
                status = 'Ontime'
            else:
                status = 'Delayed'
        else:
            status = 'Delayed'
        rep['status']=status
        delay_days = 0
        if status=='Delayed':
            # delay_days = 31
            if submission_date>last_date:
                delay_days = (submission_date-last_date).days
                # delay_days = 2
            else:
                delay_days = 31
        rep['delay_days']=delay_days
        rep['submission_date'] = submission_date
        return rep

    class Meta:
        model = ReportVersion
        fields = "__all__"

# class SubQuestionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = sub_questionsModel
#         fields = "__all__"
#         read_only_fields = ['id']
#
#
# class QuestionSerializer(serializers.ModelSerializer):
#     sub_questions = SubQuestionSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = questionsModel
#         fields = "__all__"
#         read_only_fields = ['id']
#
#
# class insideFormSerializer(serializers.ModelSerializer):
#     questions = QuestionSerializer(many=True, read_only=True)
#
#     class Meta:
#         model =insideFormModel
#         fields = "__all__"
#         read_only_fields = ['id']
