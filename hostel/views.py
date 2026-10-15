from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, Count
from .models import Hostel, HostelRoom, RoomAllocation
from .forms import HostelForm, HostelRoomForm, RoomAllocationForm


def hostel_overview(request):
    """Hostel overview dashboard showing buildings, room statistics, and occupancy"""
    hostels = Hostel.objects.annotate(
        room_count=Count('rooms'),
        total_beds=Sum('rooms__capacity'),
    ).all()

    total_buildings = hostels.count()
    total_rooms = HostelRoom.objects.count()
    total_capacity = HostelRoom.objects.aggregate(total=Sum('capacity'))['total'] or 0
    active_residents = RoomAllocation.objects.filter(status='Active').count()
    vacant_beds = max(0, total_capacity - active_residents)

    context = {
        'page_title': 'Hostel & Residential Life',
        'active_tab': 'hostel_overview',
        'hostels': hostels,
        'total_buildings': total_buildings,
        'total_rooms': total_rooms,
        'total_capacity': total_capacity,
        'active_residents': active_residents,
        'vacant_beds': vacant_beds,
    }
    return render(request, 'hostel/hostel_overview.html', context)


def hostel_add(request):
    """Add a hostel building"""
    if request.method == 'POST':
        form = HostelForm(request.POST)
        if form.is_valid():
            hostel = form.save()
            messages.success(request, f'Hostel building "{hostel.name}" added successfully!')
            return redirect('hostel:hostel_overview')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HostelForm()

    return render(request, 'hostel/hostel_form.html', {
        'form': form,
        'page_title': 'Add Hostel Building',
        'active_tab': 'hostel_overview',
        'action': 'Add',
    })


def hostel_edit(request, pk):
    """Edit hostel building"""
    hostel = get_object_or_404(Hostel, pk=pk)
    if request.method == 'POST':
        form = HostelForm(request.POST, instance=hostel)
        if form.is_valid():
            hostel = form.save()
            messages.success(request, f'Hostel "{hostel.name}" updated successfully!')
            return redirect('hostel:hostel_overview')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HostelForm(instance=hostel)

    return render(request, 'hostel/hostel_form.html', {
        'form': form,
        'hostel': hostel,
        'page_title': f'Edit {hostel.name}',
        'active_tab': 'hostel_overview',
        'action': 'Edit',
    })


def hostel_delete(request, pk):
    """Delete hostel building"""
    hostel = get_object_or_404(Hostel, pk=pk)
    if request.method == 'POST':
        name = hostel.name
        hostel.delete()
        messages.success(request, f'Hostel "{name}" deleted.')
        return redirect('hostel:hostel_overview')

    return render(request, 'hostel/hostel_confirm_delete.html', {
        'hostel': hostel,
        'page_title': 'Delete Hostel Building',
        'active_tab': 'hostel_overview',
    })


def room_list(request):
    """List of all hostel rooms with occupancy metrics"""
    hostel_id = request.GET.get('hostel', '')
    query = request.GET.get('q', '').strip()

    rooms = HostelRoom.objects.select_related('hostel').all()

    if hostel_id:
        rooms = rooms.filter(hostel_id=hostel_id)
    if query:
        rooms = rooms.filter(Q(room_number__icontains=query) | Q(hostel__name__icontains=query))

    hostels = Hostel.objects.all().order_by('name')

    context = {
        'page_title': 'Hostel Rooms Directory',
        'active_tab': 'hostel_rooms',
        'rooms': rooms,
        'hostels': hostels,
        'selected_hostel': hostel_id,
        'query': query,
    }
    return render(request, 'hostel/room_list.html', context)


def room_add(request):
    """Add a room to hostel"""
    if request.method == 'POST':
        form = HostelRoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Room {room.room_number} added to {room.hostel.name}!')
            return redirect('hostel:room_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HostelRoomForm()

    return render(request, 'hostel/room_form.html', {
        'form': form,
        'page_title': 'Add Hostel Room',
        'active_tab': 'hostel_rooms',
        'action': 'Add',
    })


def room_edit(request, pk):
    """Edit room"""
    room = get_object_or_404(HostelRoom, pk=pk)
    if request.method == 'POST':
        form = HostelRoomForm(request.POST, instance=room)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Room {room.room_number} updated successfully!')
            return redirect('hostel:room_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HostelRoomForm(instance=room)

    return render(request, 'hostel/room_form.html', {
        'form': form,
        'room': room,
        'page_title': f'Edit Room {room.room_number}',
        'active_tab': 'hostel_rooms',
        'action': 'Edit',
    })


def room_delete(request, pk):
    """Delete room"""
    room = get_object_or_404(HostelRoom, pk=pk)
    if request.method == 'POST':
        r_num = room.room_number
        room.delete()
        messages.success(request, f'Room {r_num} removed.')
        return redirect('hostel:room_list')

    return render(request, 'hostel/room_confirm_delete.html', {
        'room': room,
        'page_title': 'Delete Room',
        'active_tab': 'hostel_rooms',
    })


def allocation_list(request):
    """List of student hostel residents and bed allocations"""
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    allocations = RoomAllocation.objects.select_related('student', 'room', 'room__hostel').all()

    if query:
        allocations = allocations.filter(
            Q(student__student_name__icontains=query) |
            Q(student__admission_number__icontains=query) |
            Q(room__room_number__icontains=query)
        )
    if status_filter:
        allocations = allocations.filter(status=status_filter)

    context = {
        'page_title': 'Hostel Residents & Check-ins',
        'active_tab': 'hostel_residents',
        'allocations': allocations,
        'query': query,
        'status_filter': status_filter,
        'statuses': RoomAllocation.STATUS_CHOICES,
    }
    return render(request, 'hostel/allocation_list.html', context)


def allocation_add(request):
    """Check in student to a room"""
    if request.method == 'POST':
        form = RoomAllocationForm(request.POST)
        if form.is_valid():
            alloc = form.save()
            messages.success(request, f'{alloc.student.student_name} allocated to Room {alloc.room.room_number} ({alloc.room.hostel.name})!')
            return redirect('hostel:allocation_list')
        else:
            messages.error(request, 'Please correct the room allocation errors below.')
    else:
        form = RoomAllocationForm()

    return render(request, 'hostel/allocation_form.html', {
        'form': form,
        'page_title': 'Allocate Hostel Room',
        'active_tab': 'hostel_residents',
        'action': 'Add',
    })


def allocation_edit(request, pk):
    """Edit student room allocation or checkout"""
    alloc = get_object_or_404(RoomAllocation, pk=pk)
    if request.method == 'POST':
        form = RoomAllocationForm(request.POST, instance=alloc)
        if form.is_valid():
            alloc = form.save()
            messages.success(request, f'Stay record for {alloc.student.student_name} updated!')
            return redirect('hostel:allocation_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RoomAllocationForm(instance=alloc)

    return render(request, 'hostel/allocation_form.html', {
        'form': form,
        'alloc': alloc,
        'page_title': 'Edit Room Allocation',
        'active_tab': 'hostel_residents',
        'action': 'Edit',
    })


def allocation_delete(request, pk):
    """Delete room allocation record"""
    alloc = get_object_or_404(RoomAllocation, pk=pk)
    if request.method == 'POST':
        name = alloc.student.student_name
        alloc.delete()
        messages.success(request, f'Allocation for {name} removed.')
        return redirect('hostel:allocation_list')

    return render(request, 'hostel/allocation_confirm_delete.html', {
        'alloc': alloc,
        'page_title': 'Delete Allocation',
        'active_tab': 'hostel_residents',
    })
