from django.urls import path
from . import views

urlpatterns = [
    # -----------------------------
    # Instructor Routes
    # -----------------------------
    path('instructor/quizzes/', views.instructor_quizzes, name='instructor_quizzes'),
    path('instructor/quizzes/create/', views.create_quiz, name='create_quiz'),
    path('instructor/quizzes/<int:quiz_id>/questions/add/', views.add_question, name='add_question'),
    path('instructor/questions/<int:question_id>/answers/add/', views.add_answers, name='add_answers'),
    path('instructor/quizzes/<int:quiz_id>/toggle/', views.toggle_quiz_status, name='toggle_quiz_status'),
    path('instructor/quizzes/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('instructor/quizzes/<int:quiz_id>/attempts/', views.quiz_attempts, name='quiz_attempts'),

    # -----------------------------
    # Student Routes
    # -----------------------------
    path('student/quizzes/', views.available_quizzes, name='available_quizzes'),
    path('student/quizzes/<int:quiz_id>/preview/', views.quiz_preview, name='quiz_preview'),
    path('student/quizzes/<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),

    # Take Quiz
    path('student/attempt/<int:attempt_id>/question/<int:question_number>/',
         views.take_quiz, name='take_quiz'),

    # Submit Quiz
    path('student/attempt/<int:attempt_id>/submit/',
         views.submit_quiz, name='submit_quiz'),

    # View Results
    path('student/attempt/<int:attempt_id>/results/',
         views.view_results, name='view_results'),

    # Quiz History
    path('student/history/', views.quiz_history, name='quiz_history'),

    path("dashboard/", views.dashboard_redirect, name="dashboard"),
]
