# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Answers(models.Model):
    answer_id = models.AutoField(primary_key=True)
    question = models.ForeignKey('Questions', models.DO_NOTHING)
    answer_text = models.CharField(max_length=500)
    is_correct = models.IntegerField(blank=True, null=True)
    answer_order = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'answers'


class AuditLogs(models.Model):
    log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    action = models.CharField(max_length=255)
    log_timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'audit_logs'


class Questions(models.Model):
    question_id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey('Quizzes', models.DO_NOTHING)
    question_text = models.TextField()
    question_type = models.CharField(max_length=3)
    points = models.IntegerField(blank=True, null=True)
    question_order = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'questions'


class QuizCategories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'quiz_categories'


class QuizCategoryMap(models.Model):
    pk = models.CompositePrimaryKey('quiz_id', 'category_id')
    quiz = models.ForeignKey('Quizzes', models.DO_NOTHING)
    category = models.ForeignKey(QuizCategories, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'quiz_category_map'


class Quizzes(models.Model):
    quiz_id = models.AutoField(primary_key=True)
    instructor = models.ForeignKey('Users', models.DO_NOTHING)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    time_limit = models.IntegerField(db_comment='Time limit in minutes')
    passing_score = models.IntegerField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'quizzes'


class Roles(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'roles'


class StudentAttempts(models.Model):
    attempt_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('Users', models.DO_NOTHING)
    quiz = models.ForeignKey(Quizzes, models.DO_NOTHING)
    start_time = models.DateTimeField(blank=True, null=True)
    submit_time = models.DateTimeField(blank=True, null=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    total_points = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_completed = models.IntegerField(blank=True, null=True)
    time_taken = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student_attempts'
        unique_together = (('student', 'quiz', 'start_time'),)


class StudentResponses(models.Model):
    response_id = models.AutoField(primary_key=True)
    attempt = models.ForeignKey(StudentAttempts, models.DO_NOTHING)
    question = models.ForeignKey(Questions, models.DO_NOTHING)
    selected_answer = models.ForeignKey(Answers, models.DO_NOTHING, blank=True, null=True)
    response_text = models.TextField(blank=True, null=True)
    is_correct = models.IntegerField(blank=True, null=True)
    points_earned = models.IntegerField(blank=True, null=True)
    graded_by = models.ForeignKey('Users', models.DO_NOTHING, db_column='graded_by', blank=True, null=True)
    graded_at = models.DateTimeField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'student_responses'
        unique_together = (('attempt', 'question'),)


class UserRoleMap(models.Model):
    pk = models.CompositePrimaryKey('user_id', 'role_id')
    user = models.ForeignKey('Users', models.DO_NOTHING)
    role = models.ForeignKey(Roles, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_role_map'


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(unique=True, max_length=150)
    email = models.CharField(unique=True, max_length=254)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    role = models.CharField(max_length=10)
    is_active = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'

class Roles(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50, unique=True)

    class Meta:
        managed = False
        db_table = 'roles'

class UserRoleMap(models.Model):
    user = models.ForeignKey('Users', models.DO_NOTHING)
    role = models.ForeignKey('Roles', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_role_map'
        unique_together = (('user', 'role'),)


class QuizCategories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)

    class Meta:
        managed = False
        db_table = 'quiz_categories'

class QuizCategoryMap(models.Model):
    quiz = models.ForeignKey('Quizzes', models.DO_NOTHING)
    category = models.ForeignKey('QuizCategories', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'quiz_category_map'
        unique_together = (('quiz', 'category'),)

class AuditLogs(models.Model):
    log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    action = models.CharField(max_length=255)
    log_timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'audit_logs'


class QuizAssignments(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(
        'Quizzes',
        on_delete=models.CASCADE,
        db_column='quiz_id'
    )
    student = models.ForeignKey(
        'Users',
        on_delete=models.CASCADE,
        db_column='student_id'
    )
    assigned_by = models.ForeignKey(
        'Users',
        on_delete=models.CASCADE,
        related_name='assigned_quizzes',
        db_column='assigned_by'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False   # IMPORTANT since table already exists
        db_table = 'quiz_assignments'
        unique_together = (('quiz', 'student'),)
