from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from . import serializers, models
from rest_framework.response import Response


class ParameterLCView(ListCreateAPIView):
    serializer_class = serializers.ParameterSerializer
    queryset = models.Parameter.objects


class ParameterRUDView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ParameterSerializer
    queryset = models.Parameter.objects
    lookup_field = "id"
    lookup_url_kwarg = "id"


class CompanyLCView(ListCreateAPIView):
    serializer_class = serializers.CompanySerializer
    queryset = models.Company.objects


class CompanyRUDView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.CompanySerializer
    queryset = models.Company.objects
    lookup_field = "id"
    lookup_url_kwarg = "id"


class ParameterTreeLCView(ListCreateAPIView):
    serializer_class = serializers.ParameterTreeSerializer
    queryset = models.ParameterTree.objects

    def create(self, request, *args, **kwargs):
        data = request.data
        new_parametertree = models.ParameterTree.objects.create(summate=data['summate'], question=data['question'])
        new_parametertree.save()
        for param in data['sub_questions']:
            parameter_obj = models.Parameter.objects.get(id=param['id'])
            new_parametertree.parameters.add(parameter_obj)
        serializer = serializers.ParameterTreeSerializer(new_parametertree)
        return Response(serializer.data)


class ParameterTreeRUDView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ParameterTreeSerializer
    queryset = models.ParameterTree.objects
    lookup_field = "id"
    lookup_url_kwarg = "id"


class ReportLCView(ListCreateAPIView):
    serializer_class = serializers.ReportSerializer
    queryset = models.Report.objects

    def create(self, request, *args, **kwargs):
        data = request.data
        new_report = models.Report.objects.create(name=data['name'], frequency=data['frequency'], cutoff=data['cutoff'])

        new_report.save()
        for param in data['parameters']:
            parameter_obj = models.ParameterTree.objects.get(id=param['id'])
            new_report.parameters.add(parameter_obj)
        for comp in data['companies']:
            comp_obj = models.Company.objects.get(id=comp['id'])
            new_report.companies.add(comp_obj)
        serializer = serializers.ReportSerializer(new_report)
        return Response(serializer.data)


class ReportRUDView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ReportSerializer
    queryset = models.Report.objects
    lookup_field = "id"
    lookup_url_kwarg = "id"


class ReportVersionLCView(ListCreateAPIView):
    serializer_class = serializers.ReportVersionSerializer
    queryset = models.ReportVersion.objects

    def create(self, request, *args, **kwargs):
        data = request.data
        report_obj=models.Report.objects.get(id=data['report'])
        new_report_ver = models.ReportVersion.objects.create(name=data["name"], report=report_obj)
        new_report_ver.save()
        for repres in data['report_result']:
            repres_obj = models.ReportResult.objects.get(id=repres['id'])
            new_report_ver.report_result.add(repres_obj)
        # report_obj = models.Report.objects.get(id=data['report'])
        # new_report_ver.report.add(report_obj)
        serializer = serializers.ReportVersionSerializer(new_report_ver)
        return Response(serializer.data)


class ReportVersionRUDView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ReportVersionSerializer
    queryset = models.ReportVersion.objects
    lookup_field = "id"
    lookup_url_kwarg = "id"


class ReportResultLCView(ListCreateAPIView):
    serializer_class = serializers.ReportResultSerializer
    queryset = models.ReportResult.objects


class ReportResultRUDView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ReportResultSerializer
    queryset = models.ReportResult.objects
    lookup_field = "id"
    lookup_url_kwarg = "id"


class SubQuestionLCView(ListCreateAPIView):
    serializer_class = serializers.SubQuestionSerializer
    queryset = models.sub_questionsModel.objects


class SubQuestionRUDView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.SubQuestionSerializer
    queryset = models.sub_questionsModel.objects
    lookup_field = "id"
    lookup_url_kwarg = "id"


class QuestionLCView(ListCreateAPIView):
    serializer_class = serializers.QuestionSerializer
    queryset = models.questionsModel.objects

    def create(self, request, *args, **kwargs):
        data = request.data
        new_question = models.questionsModel.objects.create(aggregate=data["aggregate"], question=data["question"])
        new_question.save()
        for sub in data["sub_questions"]:
            sub_question_obj = models.sub_questionsModel.objects.get(current_value=sub["current_value"],
                                                                     last_value=sub["last_value"],
                                                                     sub_question=sub["sub_question"])
            new_question.sub_questions.add(sub_question_obj)
        serializer = serializers.QuestionSerializer(new_question)
        return Response(serializer.data)


class QuestionRUDView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.QuestionSerializer
    queryset = models.questionsModel.objects
    lookup_field = "id"
    lookup_url_kwarg = "id"


class insideFormLCView(ListCreateAPIView):
    serializer_class = serializers.insideFormSerializer
    queryset = models.insideFormModel.objects

    def create(self, request, *args, **kwargs):
        data = request.data
        new_insideForm = models.insideFormModel.objects.create(company=data['company'],
                                                               deadline_days=data['deadline_days'],
                                                               filled_count=data['filled_count'],
                                                               name=data['name'], question_count=data['question_count'],
                                                               schedule=data['schedule'],
                                                               is_submitted=data['is_submitted'],
                                                               current_instance=data['current_instance'])
        new_insideForm.save()
        for i in data['questions']:
            # print(i['sub_questions'][0])
            # questions_obj = models.questionsModel.objects.get(aggregate=i['aggregate'], question=i['question'],
            #                                                   sub_questions=i['sub_questions'][0])
            questions_obj = models.questionsModel.objects.get(id=i['id'])
            new_insideForm.questions.add(questions_obj)
            serializer = serializers.insideFormSerializer(new_insideForm)
        return Response(serializer.data)

