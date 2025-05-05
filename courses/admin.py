from django.contrib import admin
from .models import (
    Category, Course, Module, TextContent, FileContent, 
    ImageContent, VideoContent, Enrollment, Progress
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

class ModuleInline(admin.StackedInline):
    model = Module
    extra = 0

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'instructor', 'status', 'created']
    list_filter = ['status', 'created', 'category', 'instructor']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'description']

@admin.register(TextContent)
class TextContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order', 'created']

@admin.register(FileContent)
class FileContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order', 'created']

@admin.register(ImageContent)
class ImageContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'caption', 'order', 'created']

@admin.register(VideoContent)
class VideoContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'duration', 'order', 'created']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'completed']
    list_filter = ['completed', 'enrolled_at']
    search_fields = ['student__username', 'course__title']

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'module', 'completed', 'last_accessed']
    list_filter = ['completed', 'last_accessed']
    search_fields = ['student__username', 'course__title', 'module__title']
