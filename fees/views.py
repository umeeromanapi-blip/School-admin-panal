from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from .models import FeeRecord
from .forms import FeeRecordForm
from students.models import Student
import datetime


def fee_list_view(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    type_filter = request.GET.get('type', '').strip()

    records = FeeRecord.objects.select_related('student').order_by('-due_date')

    if query:
        records = records.filter(
            Q(student__student_name__icontains=query) |
            Q(student__admission_number__icontains=query)
        )
    if status_filter:
        records = records.filter(status=status_filter)
    if type_filter:
        records = records.filter(fee_type=type_filter)

    total = records.count()
    total_due    = records.aggregate(t=Sum('amount_due'))['t'] or 0
    total_paid   = records.aggregate(t=Sum('amount_paid'))['t'] or 0
    total_unpaid = total_due - total_paid

    paginator = Paginator(records, 12)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_title': 'Fee Management',
        'active_tab': 'fees',
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'total': total,
        'total_due': total_due,
        'total_paid': total_paid,
        'total_unpaid': total_unpaid,
        'fee_statuses': FeeRecord.STATUS_CHOICES,
        'fee_types': FeeRecord.FEE_TYPE_CHOICES,
    }
    return render(request, 'fees/fee_list.html', context)


def fee_create_view(request):
    if request.method == 'POST':
        form = FeeRecordForm(request.POST)
        if form.is_valid():
            record = form.save()
            messages.success(request, f"Fee record for '{record.student.student_name}' created successfully!")
            return redirect('fees:fee_list')
        messages.error(request, "Please correct the errors below.")
    else:
        form = FeeRecordForm(initial={'due_date': datetime.date.today()})

    context = {
        'page_title': 'Add Fee Record',
        'active_tab': 'fees',
        'form': form,
        'action_mode': 'create',
    }
    return render(request, 'fees/fee_form.html', context)


def fee_update_view(request, id):
    record = get_object_or_404(FeeRecord, id=id)
    if request.method == 'POST':
        form = FeeRecordForm(request.POST, instance=record)
        if form.is_valid():
            r = form.save()
            messages.success(request, f"Fee record for '{r.student.student_name}' updated!")
            return redirect('fees:fee_list')
        messages.error(request, "Please fix the errors below.")
    else:
        form = FeeRecordForm(instance=record)

    context = {
        'page_title': f'Edit Fee — {record.student.student_name}',
        'active_tab': 'fees',
        'form': form,
        'record': record,
        'action_mode': 'update',
    }
    return render(request, 'fees/fee_form.html', context)


def fee_delete_view(request, id):
    record = get_object_or_404(FeeRecord, id=id)
    if request.method == 'POST':
        name = record.student.student_name
        record.delete()
        messages.success(request, f"Fee record for '{name}' deleted.")
        return redirect('fees:fee_list')
    context = {
        'page_title': 'Confirm Delete Fee Record',
        'active_tab': 'fees',
        'record': record,
    }
    return render(request, 'fees/fee_confirm_delete.html', context)
