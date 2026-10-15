from django import forms
from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'category', 'audience', 'priority', 'published_date', 'is_pinned', 'is_active', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Midterm Examination Schedule Released', 'id': 'id_title'}),
            'category': forms.Select(attrs={'class': 'form-control', 'id': 'id_category'}),
            'audience': forms.Select(attrs={'class': 'form-control', 'id': 'id_audience'}),
            'priority': forms.Select(attrs={'class': 'form-control', 'id': 'id_priority'}),
            'published_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_published_date'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_is_pinned'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_is_active'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Write complete notice details here...', 'id': 'id_content'}),
        }
