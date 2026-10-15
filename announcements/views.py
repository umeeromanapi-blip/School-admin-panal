from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Announcement
from .forms import AnnouncementForm


def announcement_list(request):
    """Notice board list view with search, filter by audience, priority, and category"""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    audience = request.GET.get('audience', '').strip()
    priority = request.GET.get('priority', '').strip()

    notices = Announcement.objects.all()

    if query:
        notices = notices.filter(Q(title__icontains=query) | Q(content__icontains=query))
    if category:
        notices = notices.filter(category=category)
    if audience:
        notices = notices.filter(audience=audience)
    if priority:
        notices = notices.filter(priority=priority)

    total_count = Announcement.objects.count()
    active_count = Announcement.objects.filter(is_active=True).count()
    urgent_count = Announcement.objects.filter(priority='urgent', is_active=True).count()

    context = {
        'page_title': 'Notice Board & Announcements',
        'active_tab': 'announcements',
        'notices': notices,
        'query': query,
        'category_filter': category,
        'audience_filter': audience,
        'priority_filter': priority,
        'total_count': total_count,
        'active_count': active_count,
        'urgent_count': urgent_count,
        'categories': Announcement.CATEGORY_CHOICES,
        'audiences': Announcement.AUDIENCE_CHOICES,
        'priorities': Announcement.PRIORITY_CHOICES,
    }
    return render(request, 'announcements/announcement_list.html', context)


def announcement_detail(request, pk):
    """View single announcement detail"""
    notice = get_object_or_404(Announcement, pk=pk)
    return render(request, 'announcements/announcement_detail.html', {
        'page_title': notice.title,
        'active_tab': 'announcements',
        'notice': notice,
    })


def announcement_add(request):
    """Create a new announcement"""
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            notice = form.save()
            messages.success(request, f'Notice "{notice.title}" published successfully!')
            return redirect('announcements:announcement_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AnnouncementForm()

    return render(request, 'announcements/announcement_form.html', {
        'form': form,
        'page_title': 'Publish Notice',
        'active_tab': 'announcements',
        'action': 'Add',
    })


def announcement_edit(request, pk):
    """Edit announcement"""
    notice = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=notice)
        if form.is_valid():
            notice = form.save()
            messages.success(request, f'Notice "{notice.title}" updated successfully!')
            return redirect('announcements:announcement_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AnnouncementForm(instance=notice)

    return render(request, 'announcements/announcement_form.html', {
        'form': form,
        'notice': notice,
        'page_title': f'Edit Notice',
        'active_tab': 'announcements',
        'action': 'Edit',
    })


def announcement_delete(request, pk):
    """Delete announcement"""
    notice = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        title = notice.title
        notice.delete()
        messages.success(request, f'Notice "{title}" was deleted.')
        return redirect('announcements:announcement_list')

    return render(request, 'announcements/announcement_confirm_delete.html', {
        'notice': notice,
        'page_title': 'Delete Notice',
        'active_tab': 'announcements',
    })
