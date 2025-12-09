from django.contrib import admin
from .models import *

# Register your models here.
models_to_register = [Answers, Questions, Quizzes, StudentAttempts,
                      StudentResponses, Users, Roles, QuizCategories,
                      AuditLogs]
admin.site.register(models_to_register)