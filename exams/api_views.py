from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Exam, Subject, Mark
from .serializers import ExamSerializer, SubjectSerializer, MarkSerializer


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_exam_list_create(request):
    if request.method == 'GET':
        exams = Exam.objects.all().order_by('-start_date')
        return Response(ExamSerializer(exams, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = ExamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors, **serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_subject_list_create(request):
    if request.method == 'GET':
        subjects = Subject.objects.all().order_by('name')
        return Response(SubjectSerializer(subjects, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors, **serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_mark_list_create(request):
    if request.method == 'GET':
        exam_id = request.query_params.get('exam_id')
        subject_id = request.query_params.get('subject_id')
        marks = Mark.objects.select_related('student', 'subject', 'exam').all().order_by('-created_at')
        if exam_id:
            marks = marks.filter(exam_id=exam_id)
        if subject_id:
            marks = marks.filter(subject_id=subject_id)
        return Response(MarkSerializer(marks, many=True).data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = MarkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors, **serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
