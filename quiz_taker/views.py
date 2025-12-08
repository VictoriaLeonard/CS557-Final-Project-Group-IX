from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout as django_logout
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import time

from .models import (
    Users, Quizzes, Questions, Answers,
    StudentAttempts, StudentResponses,
    QuizCategories, QuizCategoryMap,
    AuditLogs
)


def get_user_by_credentials(username, password):
    """Authenticate against your custom Users table."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT user_id, username, role 
            FROM users 
            WHERE username = %s AND password_hash = %s AND is_active = 1
        """, [username, password])
        row = cursor.fetchone()

    if row:
        return {
            "user_id": row[0],
            "username": row[1],
            "role": row[2],
        }
    return None


def get_user_by_id(user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT user_id, username, role 
            FROM users 
            WHERE user_id = %s
        """, [user_id])
        row = cursor.fetchone()

    if row:
        return {
            "user_id": row[0],
            "username": row[1],
            "role": row[2],
        }
    return None


def login_required_custom(view_func):
    def wrapper(request, *args, **kwargs):
        if "user_id" not in request.session:
            messages.error(request, "You must be logged in.")
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


@csrf_exempt
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")    # student or instructor

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect("register")

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, role, is_active)
                    VALUES (%s, %s, %s, %s, 1)
                """, [username, email, password, role])

            messages.success(request, f"Account created for {username}. Please log in.")
            return redirect("login")

        except Exception as e:
            messages.error(request, f"Error creating account: {e}")
            return redirect("register")

    return render(request, "users/register.html")


@csrf_exempt
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = get_user_by_credentials(username, password)

        if user:
            request.session["user_id"] = user["user_id"]
            request.session["username"] = user["username"]
            request.session["role"] = user["role"]

            messages.success(request, f"Welcome back, {user['username']}!")

            # Redirect based on role
            if user["role"] == "instructor":
                return redirect("instructor_home")
            else:
                return redirect("student_home")

        messages.error(request, "Invalid username or password.")
        return redirect("login")

    return render(request, "users/login.html")


def logout_view(request):
    django_logout(request)  # clears session
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect("login")


@login_required_custom
def instructor_home(request):
    user = get_user_by_id(request.session["user_id"])
    return render(request, "teachers/home.html", {"users": user})


@login_required_custom
def student_home(request):
    user = get_user_by_id(request.session["user_id"])
    return render(request, "students/home.html", {"users": user})


# Default home redirector
@login_required_custom
def home_view(request):
    role = request.session.get("role")
    if role == "instructor":
        return redirect("instructor_home")
    return redirect("student_home")

def instructor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get("role") != "instructor":
            messages.error(request, "Instructor access required.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper


@instructor_required
def create_quiz(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        time_limit = request.POST.get("time_limit")
        passing = request.POST.get("passing_score")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        instructor_id = request.session["user_id"]

        # Insert quiz
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO quizzes (instructor_id, title, description, time_limit, passing_score, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [instructor_id, title, description, time_limit, passing, start_date, end_date])

        messages.success(request, "Quiz created successfully!")
        return redirect("instructor_quizzes")

    return render(request, "quiz/instructor/create_quiz.html")


@instructor_required
def instructor_quizzes(request):
    instructor_id = request.session["user_id"]
    quizzes = Quizzes.objects.filter(instructor_id=instructor_id)
    return render(request, "quiz/instructor/my_quizzes.html", {"quizzes": quizzes})


@instructor_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quizzes, pk=quiz_id)

    if request.method == "POST":
        text = request.POST.get("question_text")
        qtype = request.POST.get("question_type")
        points = request.POST.get("points")

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO questions (quiz_id, question_text, question_type, points)
                VALUES (%s, %s, %s, %s)
            """, [quiz_id, text, qtype, points])

        messages.success(request, "Question added.")
        return redirect("add_question", quiz_id=quiz_id)

    questions = Questions.objects.filter(quiz_id=quiz_id)

    return render(request, "quiz/instructor/add_question.html", {
        "quiz": quiz,
        "questions": questions
    })


@instructor_required
def add_answers(request, question_id):
    question = get_object_or_404(Questions, pk=question_id)

    if request.method == "POST":
        answer_text = request.POST.get("answer_text")
        is_correct = request.POST.get("is_correct") == "on"

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO answers (question_id, answer_text, is_correct)
                VALUES (%s, %s, %s)
            """, [question_id, answer_text, is_correct])

        messages.success(request, "Answer added.")
        return redirect("add_answers", question_id=question_id)

    answers = Answers.objects.filter(question_id=question_id)

    return render(request, "quiz/instructor/add_answers.html", {
        "question": question,
        "answers": answers
    })


@instructor_required
def toggle_quiz_status(request, quiz_id):
    quiz = get_object_or_404(Quizzes, pk=quiz_id)
    quiz.is_active = 0 if quiz.is_active else 1
    quiz.save()

    messages.info(request, "Quiz activation status changed.")
    return redirect("instructor_quizzes")


@instructor_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quizzes, pk=quiz_id)
    quiz.delete()
    messages.success(request, "Quiz deleted.")
    return redirect("instructor_quizzes")


@instructor_required
def quiz_attempts(request, quiz_id):
    attempts = StudentAttempts.objects.filter(quiz_id=quiz_id)
    quiz = get_object_or_404(Quizzes, pk=quiz_id)

    return render(request, "quiz/instructor/quiz_attempts.html", {
        "quiz": quiz,
        "attempts": attempts
    })


def available_quizzes(request):
    quizzes = Quizzes.objects.filter(is_active=1)
    return render(request, "quiz/student/available_quizzes.html", {"quizzes": quizzes})


def quiz_preview(request, quiz_id):
    quiz = get_object_or_404(Quizzes, pk=quiz_id)
    questions = Questions.objects.filter(quiz_id=quiz_id)
    total_points = sum(q.points or 0 for q in questions)

    return render(request, "quiz/student/quiz_preview.html", {
        "quiz": quiz,
        "questions": questions,
        "total_points": total_points
    })


def start_quiz(request, quiz_id):
    student_id = request.session["user_id"]

    # Create attempt
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO student_attempts (student_id, quiz_id, total_points)
            VALUES (%s, %s, (
                SELECT COALESCE(SUM(points),0) FROM questions WHERE quiz_id=%s
            ))
        """, [student_id, quiz_id, quiz_id])

    attempt_id = StudentAttempts.objects.filter(student_id=student_id, quiz_id=quiz_id).latest("attempt_id").attempt_id

    return redirect("take_quiz", attempt_id=attempt_id, question_number=1)


def take_quiz(request, attempt_id, question_number):
    attempt = get_object_or_404(StudentAttempts, pk=attempt_id)
    quiz_id = attempt.quiz_id

    questions = list(Questions.objects.filter(quiz_id=quiz_id).order_by("question_order", "question_id"))

    # Out of bounds check
    if question_number < 1 or question_number > len(questions):
        return redirect("quiz_preview", quiz_id=quiz_id)

    question = questions[question_number - 1]
    answers = Answers.objects.filter(question_id=question.question_id)

    # Save answer if POST
    if request.method == "POST":
        chosen = request.POST.get("answer")

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO student_responses (attempt_id, question_id, selected_answer_id)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE selected_answer_id = VALUES(selected_answer_id)
            """, [attempt_id, question.question_id, chosen])

        # Next question
        return redirect("take_quiz", attempt_id=attempt_id, question_number=question_number + 1)

    return render(request, "quiz/student/take_quiz.html", {
        "question": question,
        "answers": answers,
        "question_number": question_number,
        "total_questions": len(questions),
        "attempt_id": attempt_id
    })


def submit_quiz(request, attempt_id):
    attempt = get_object_or_404(StudentAttempts, pk=attempt_id)

    # Calculate score (your trigger also handles this)
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE student_attempts
            SET score = (
                SELECT SUM(
                    CASE WHEN a.is_correct = 1 THEN q.points ELSE 0 END
                )
                FROM student_responses sr
                JOIN answers a ON sr.selected_answer_id = a.answer_id
                JOIN questions q ON sr.question_id = q.question_id
                WHERE sr.attempt_id = %s
            ),
            is_completed = 1,
            submit_time = NOW()
            WHERE attempt_id = %s
        """, [attempt_id, attempt_id])

    messages.success(request, "Quiz submitted!")
    return redirect("view_results", attempt_id=attempt_id)


def view_results(request, attempt_id):
    attempt = get_object_or_404(StudentAttempts, pk=attempt_id)
    responses = StudentResponses.objects.filter(attempt_id=attempt_id)

    return render(request, "quiz/student/view_results.html", {
        "attempt": attempt,
        "responses": responses
    })


def quiz_history(request):
    student_id = request.session["user_id"]
    attempts = StudentAttempts.objects.filter(student_id=student_id)
    return render(request, "quiz/student/quiz_history.html", {"attempts": attempts})

@login_required
def dashboard_redirect(request):
    if request.user.role == "instructor":
        return redirect("instructor_dashboard")
    else:
        return redirect("student_dashboard")


def quiz_start(request, quiz_id):
    quiz = get_object_or_404(Quizzes, pk=quiz_id)

    # Convert minutes from DB to seconds for timer logic
    duration_seconds = quiz.time_limit * 60

    end_time = time.time() + duration_seconds
    request.session["quiz_end_time"] = end_time

    return redirect("quiz_question", quiz_id=quiz_id, number=1)