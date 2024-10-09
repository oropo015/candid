from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Question, Answer, ExamResult, Certificate

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')
    inlines = [AnswerInline]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'text', 'is_correct')
    list_filter = ('question', 'is_correct')
    search_fields = ('text',)

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'student_name', 'score', 'passed')
    list_filter = ('passed',)
    search_fields = ('student_name',)

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'exam_result', 'issue_date')
    list_filter = ('issue_date',)
    search_fields = ('user__username',)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)