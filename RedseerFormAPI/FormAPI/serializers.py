import datetime

from rest_framework import serializers
from .models import Parameter, Company, ParameterTree, Report, ReportVersion, ReportResult, sub_questionsModel, \
    questionsModel, insideFormModel


class ParameterSerializer(serializers.ModelSerializer):
    sub_question = serializers.CharField(source='question')

    class Meta:
        model = Parameter
        fields = ['id', 'sub_question']
        read_only_fields = ['id']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name']
        read_only_fields = ['id']


class ParameterTreeSerializer(serializers.ModelSerializer):
    aggregate = serializers.BooleanField(source='summate')
    # parameters = ParameterSerializer(many=True, read_only=True)
    sub_questions = ParameterSerializer(source='parameters', many=True, read_only=True)

    class Meta:
        model = ParameterTree
        fields = ['id', 'aggregate', 'question', 'sub_questions']
        read_only_fields = ['id']


class ReportSerializer(serializers.ModelSerializer):
    # parameters = ParameterTreeSerializer(many=True, read_only=True)
    companies = CompanySerializer(many=True, read_only=True)
    questions = ParameterTreeSerializer(source='parameters', many=True, read_only=True)
    deadline = serializers.IntegerField(source='cutoff')
    schedule = serializers.CharField(source='frequency')

    def to_representation(self, instance):
        rep = super(ReportSerializer, self).to_representation(instance)
        time_codes = {'1': "Weekly", '2': "Monthly", '3': "Quarterly"}
        schedule_val = time_codes[rep['schedule']]
        rep['schedule'] = schedule_val
        rep['question_count'] = len(rep['questions'])
        rep['company'] = [d['name'] for d in rep['companies'] if 'name' in d]
        rep.pop('companies')
        rep['filled_count'] = Report.objects.count()
        rep['last_modified_date'] = datetime.date.today()
        rep['is_submitted'] = False
        rep['current_instance'] = {
            'id': rep['id'],
            'created_at': datetime.date.today()
        }
        return rep

    class Meta:
        model = Report
        fields = ['id', 'name', 'companies', 'schedule', 'questions', 'deadline']
        read_only_fields = ['id']


class ReportResultSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        rep = super(ReportResultSerializer, self).to_representation(instance)
        rep['current_value'] = rep['value']
        repResult_quersyset = ReportResult.objects.filter(parametertree=instance.parametertree,
                                                          parameter=instance.parameter)
        # all values with same subquestion sorted by date
        value_list = [x.value for x in repResult_quersyset]
        if rep['value'] == value_list[0]:
            last_val = 'null'
        else:
            if rep['value'] in value_list:
                curr_index = value_list.index(rep['value'])
                last_val = value_list[curr_index-1]
            else:
                last_val = '0'
        rep['last_value'] = last_val
        rep.pop('value')
        return rep

    class Meta:
        model = ReportResult
        fields = "__all__"
        read_only_fields = ['id']


class ReportVersionSerializer(serializers.ModelSerializer):
    report_result = ReportResultSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['current_instance'] = {
            'id': rep['id'],
            'created_at': rep['date_created']
        }
        rep['is_submitted'] = False
        rep['last_modified_date'] = datetime.date.today()
        rep_details = ReportSerializer(instance.report).data
        for i in rep_details['questions']:
            # i is a dict
            for j in rep['report_result']:
                if i['id'] == str(j['parametertree']):
                    for k in i['sub_questions']:
                        if k['id'] == str(j['parameter']):
                            k['last_value'] = j['last_value']
                            k['current_value'] = j['current_value']

        # print(rep["report_result"][0]["parametertree"])
        # add_here = rep_details['questions'][0]['sub_questions'][0]
        # add_here['last_value'] = "0"
        rep.pop('report')
        rep.pop('date_created')
        rep.pop('report_result')
        # print(add_here)
        # rep_result = ReportResultSerializer(instance.id).data
        # print(rep_result)
        rep = {**rep_details, **rep}
        return rep

    class Meta:
        model = ReportVersion
        fields = "__all__"
        read_only_fields = ['id']


class SubQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = sub_questionsModel
        fields = "__all__"
        read_only_fields = ['id']


class QuestionSerializer(serializers.ModelSerializer):
    sub_questions = SubQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = questionsModel
        fields = "__all__"
        read_only_fields = ['id']


class insideFormSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model =insideFormModel
        fields = "__all__"
        read_only_fields = ['id']
