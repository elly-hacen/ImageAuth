from django.contrib import admin
from .models import User, Image, Metadata, AnalysisResult, UploadLog
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'created_at', 'is_staff')
    search_fields = ('username', 'email')

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('filename', 'user', 'upload_time', 'status')
    list_filter = ('status', 'upload_time')
    search_fields = ('filename', 'user__username')

@admin.register(Metadata)
class MetadataAdmin(admin.ModelAdmin):
    list_display = ('tag', 'value', 'image')
    search_fields = ('tag', 'value')

@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('prediction', 'confidence_score', 'analyzed_at', 'image')
    list_filter = ('prediction', 'analyzed_at')

@admin.register(UploadLog)
class UploadLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'timestamp', 'ip_address')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'ip_address')
