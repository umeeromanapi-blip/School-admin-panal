from rest_framework import serializers
from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    audience_display = serializers.CharField(source='get_audience_display', read_only=True)

    class Meta:
        model = Announcement
        fields = [
            'id',
            'title',
            'category',
            'category_display',
            'content',
            'audience',
            'audience_display',
            'priority',
            'priority_display',
            'is_pinned',
            'is_active',
            'published_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
