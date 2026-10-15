from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from .models import Vehicle, Route, TransportAllocation
from .forms import VehicleForm, RouteForm, TransportAllocationForm


def transport_dashboard(request):
    """Transport overview, routes, and fleet status"""
    routes = Route.objects.select_related('vehicle').annotate(
        passenger_count=Count('assigned_students')
    ).all()

    total_vehicles = Vehicle.objects.count()
    active_vehicles = Vehicle.objects.filter(status='Active').count()
    total_routes = routes.count()
    total_passengers = TransportAllocation.objects.filter(is_active=True).count()

    context = {
        'page_title': 'School Transport & Fleet',
        'active_tab': 'transport_dashboard',
        'routes': routes,
        'total_vehicles': total_vehicles,
        'active_vehicles': active_vehicles,
        'total_routes': total_routes,
        'total_passengers': total_passengers,
    }
    return render(request, 'transport/transport_dashboard.html', context)


def vehicle_list(request):
    """Fleet vehicles directory"""
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    vehicles = Vehicle.objects.all()
    if query:
        vehicles = vehicles.filter(Q(vehicle_number__icontains=query) | Q(driver_name__icontains=query) | Q(vehicle_model__icontains=query))
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)

    context = {
        'page_title': 'Fleet Vehicles',
        'active_tab': 'transport_vehicles',
        'vehicles': vehicles,
        'query': query,
        'status_filter': status_filter,
        'statuses': Vehicle.STATUS_CHOICES,
    }
    return render(request, 'transport/vehicle_list.html', context)


def vehicle_add(request):
    """Add a new vehicle"""
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f'Vehicle {vehicle.vehicle_number} registered successfully!')
            return redirect('transport:vehicle_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VehicleForm()

    return render(request, 'transport/vehicle_form.html', {
        'form': form,
        'page_title': 'Register Vehicle',
        'active_tab': 'transport_vehicles',
        'action': 'Add',
    })


def vehicle_edit(request, pk):
    """Edit vehicle"""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            vehicle = form.save()
            messages.success(request, f'Vehicle {vehicle.vehicle_number} updated successfully!')
            return redirect('transport:vehicle_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VehicleForm(instance=vehicle)

    return render(request, 'transport/vehicle_form.html', {
        'form': form,
        'vehicle': vehicle,
        'page_title': f'Edit Vehicle {vehicle.vehicle_number}',
        'active_tab': 'transport_vehicles',
        'action': 'Edit',
    })


def vehicle_delete(request, pk):
    """Delete vehicle"""
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        num = vehicle.vehicle_number
        vehicle.delete()
        messages.success(request, f'Vehicle {num} deleted from fleet.')
        return redirect('transport:vehicle_list')

    return render(request, 'transport/vehicle_confirm_delete.html', {
        'vehicle': vehicle,
        'page_title': 'Delete Vehicle',
        'active_tab': 'transport_vehicles',
    })


def route_add(request):
    """Create a new route"""
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            route = form.save()
            messages.success(request, f'Route "{route.route_name}" created successfully!')
            return redirect('transport:transport_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RouteForm()

    return render(request, 'transport/route_form.html', {
        'form': form,
        'page_title': 'Create Bus Route',
        'active_tab': 'transport_dashboard',
        'action': 'Add',
    })


def route_edit(request, pk):
    """Edit route"""
    route = get_object_or_404(Route, pk=pk)
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            route = form.save()
            messages.success(request, f'Route "{route.route_name}" updated!')
            return redirect('transport:transport_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RouteForm(instance=route)

    return render(request, 'transport/route_form.html', {
        'form': form,
        'route': route,
        'page_title': f'Edit {route.route_name}',
        'active_tab': 'transport_dashboard',
        'action': 'Edit',
    })


def route_delete(request, pk):
    """Delete route"""
    route = get_object_or_404(Route, pk=pk)
    if request.method == 'POST':
        name = route.route_name
        route.delete()
        messages.success(request, f'Route "{name}" deleted.')
        return redirect('transport:transport_dashboard')

    return render(request, 'transport/route_confirm_delete.html', {
        'route': route,
        'page_title': 'Delete Route',
        'active_tab': 'transport_dashboard',
    })


def allocation_list(request):
    """List student transport pass allocations"""
    query = request.GET.get('q', '').strip()
    route_filter = request.GET.get('route', '').strip()

    allocations = TransportAllocation.objects.select_related('student', 'route', 'route__vehicle').all()

    if query:
        allocations = allocations.filter(
            Q(student__student_name__icontains=query) |
            Q(student__admission_number__icontains=query) |
            Q(pickup_stop__icontains=query)
        )
    if route_filter:
        allocations = allocations.filter(route_id=route_filter)

    routes = Route.objects.all().order_by('route_name')

    context = {
        'page_title': 'Student Transport Passes',
        'active_tab': 'transport_passes',
        'allocations': allocations,
        'routes': routes,
        'route_filter': route_filter,
        'query': query,
    }
    return render(request, 'transport/allocation_list.html', context)


def allocation_add(request):
    """Issue new transport pass"""
    if request.method == 'POST':
        form = TransportAllocationForm(request.POST)
        if form.is_valid():
            alloc = form.save()
            messages.success(request, f'Transport pass issued to {alloc.student.student_name} ({alloc.route.route_name})!')
            return redirect('transport:allocation_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TransportAllocationForm()

    return render(request, 'transport/allocation_form.html', {
        'form': form,
        'page_title': 'Issue Transport Pass',
        'active_tab': 'transport_passes',
        'action': 'Add',
    })


def allocation_edit(request, pk):
    """Edit transport pass"""
    alloc = get_object_or_404(TransportAllocation, pk=pk)
    if request.method == 'POST':
        form = TransportAllocationForm(request.POST, instance=alloc)
        if form.is_valid():
            alloc = form.save()
            messages.success(request, f'Pass for {alloc.student.student_name} updated successfully!')
            return redirect('transport:allocation_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TransportAllocationForm(instance=alloc)

    return render(request, 'transport/allocation_form.html', {
        'form': form,
        'alloc': alloc,
        'page_title': 'Edit Transport Pass',
        'active_tab': 'transport_passes',
        'action': 'Edit',
    })


def allocation_delete(request, pk):
    """Delete transport pass"""
    alloc = get_object_or_404(TransportAllocation, pk=pk)
    if request.method == 'POST':
        name = alloc.student.student_name
        alloc.delete()
        messages.success(request, f'Transport pass for {name} removed.')
        return redirect('transport:allocation_list')

    return render(request, 'transport/allocation_confirm_delete.html', {
        'alloc': alloc,
        'page_title': 'Delete Transport Pass',
        'active_tab': 'transport_passes',
    })
