from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import AttendanceRecord
from .serializers import AttendanceRecordSerializer


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_attendance_list_create(request):
    if request.method == 'GET':
        date_filter = request.query_params.get('date', '').strip()
        class_filter = request.query_params.get('class', '').strip()
        records = AttendanceRecord.objects.select_related('student').all().order_by('-date')
        if date_filter:
            records = records.filter(date=date_filter)
        if class_filter:
            records = records.filter(student__student_class__iexact=class_filter)
        serializer = AttendanceRecordSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = AttendanceRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors, **serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def api_attendance_detail_update_delete(request, id):
    try:
        record = AttendanceRecord.objects.select_related('student').get(id=id)
    except AttendanceRecord.DoesNotExist:
        return Response({'error': 'Attendance record not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(AttendanceRecordSerializer(record).data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        partial = (request.method == 'PATCH')
        serializer = AttendanceRecordSerializer(record, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors, **serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
