from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, InstructorProfile

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False

class InstructorProfileInline(admin.StackedInline):
    model = InstructorProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [StudentProfileInline, InstructorProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_student', 'is_instructor', 'is_staff')
    list_filter = ('is_student', 'is_instructor', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Rôles', {'fields': ('is_student', 'is_instructor', 'bio', 'profile_picture')}),
    )

admin.site.register(User, CustomUserAdmin)
