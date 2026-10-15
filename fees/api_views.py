from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import FeeRecord
from .serializers import FeeRecordSerializer


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_fee_list_create(request):
    if request.method == 'GET':
        status_filter = request.query_params.get('status', '').strip()
        fee_type = request.query_params.get('type', '').strip()
        student_id = request.query_params.get('student_id', '').strip()

        fees = FeeRecord.objects.select_related('student').all().order_by('-due_date')
        if status_filter:
            fees = fees.filter(status=status_filter)
        if fee_type:
            fees = fees.filter(fee_type=fee_type)
        if student_id:
            fees = fees.filter(student_id=student_id)

        serializer = FeeRecordSerializer(fees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = FeeRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors, **serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def api_fee_detail_update_delete(request, id):
    try:
        fee = FeeRecord.objects.select_related('student').get(id=id)
    except FeeRecord.DoesNotExist:
        return Response({'error': 'Fee record not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(FeeRecordSerializer(fee).data, status=status.HTTP_200_OK)

    elif request.method in ['PUT', 'PATCH']:
        partial = (request.method == 'PATCH')
        serializer = FeeRecordSerializer(fee, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors, **serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        fee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
