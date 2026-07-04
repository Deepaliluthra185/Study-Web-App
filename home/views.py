from django.shortcuts import render, redirect
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
import json
import re
from .models import Paper, Question
from .gemini_utils import get_explanation, generate_mock_test_questions

class StudentRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email")

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = StudentRegisterForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    papers_count = Paper.objects.count()
    questions_count = Question.objects.count()
    chapters_count = Question.objects.values('chapter').distinct().count()
    featured_papers = Paper.objects.all()[:3]
    
    context = {
        'papers_count': papers_count,
        'questions_count': questions_count,
        'chapters_count': chapters_count,
        'featured_papers': featured_papers,
    }
    return render(request,'home.html', context)

@login_required
def papers(request):
    papers = Paper.objects.all()
    return render(request,'paper.html', {'papers': papers})


@login_required
def chapter_questions(request):
    questions = Question.objects.all()
    chapter = request.GET.get("chapter")
    board = request.GET.get("board")
    class_name = request.GET.get("class_name")
    subject = request.GET.get("subject")

    if chapter:
        from django.db.models import Q
        questions = questions.filter(Q(chapter__icontains=chapter) | Q(question_text__icontains=chapter) | Q(subject__icontains=chapter))
    if board:
        questions = questions.filter(board=board)
    if class_name:
        questions = questions.filter(class_name=class_name)
    if subject:
        questions = questions.filter(subject=subject)

    return render(
        request,
        "chapter_questions.html",
        {"questions": questions}
    )


@login_required
def chapters(request):
    from .models import UserProfile
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    board = request.GET.get("board", profile_obj.board)
    class_name = request.GET.get("class_name", profile_obj.class_name)
    subject = request.GET.get("subject", "Physics")

    questions = Question.objects.all()
    if board:
        questions = questions.filter(board=board)
    if class_name:
        questions = questions.filter(class_name=class_name)
    if subject:
        questions = questions.filter(subject=subject)

    chapters = questions.values_list(
        'chapter',
        flat=True
    ).distinct()

    # Get distinct options for filters from the database
    all_subjects = Question.objects.values_list('subject', flat=True).distinct()
    all_boards = Question.objects.values_list('board', flat=True).distinct()
    all_classes = Question.objects.values_list('class_name', flat=True).distinct()

    return render(
        request,
        'chapters.html',
        {
            'chapters': chapters,
            'selected_board': board,
            'selected_class': class_name,
            'selected_subject': subject,
            'all_subjects': all_subjects,
            'all_boards': all_boards,
            'all_classes': all_classes,
        }
    )


@login_required
def explain_question_api(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    explanation = get_explanation(question.question_text, question.subject)
    return JsonResponse({"explanation": explanation})


@login_required
def mock_tests(request):
    from .models import UserProfile
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    # Group by chapter and get counts, filtering by user's targeted board and class
    chapter_stats = Question.objects.filter(
        board=profile_obj.board,
        class_name=profile_obj.class_name
    ).values('chapter', 'subject', 'board', 'class_name').annotate(q_count=Count('id')).order_by('-q_count')

    tests = []
    for i, stat in enumerate(chapter_stats):
        tests.append({
            'id': i + 1,
            'chapter': stat['chapter'],
            'subject': stat['subject'],
            'board': stat['board'],
            'class_name': stat['class_name'],
            'question_count': stat['q_count'],
            'duration': stat['q_count'] * 2,  # 2 mins per question
        })
    
    # Also get all distinct subjects from database for filtering tabs
    subjects = Question.objects.values_list('subject', flat=True).distinct()
    
    return render(request, 'mock_tests.html', {
        'tests': tests,
        'subjects': subjects,
    })


@login_required
def profile(request):
    from .models import UserProfile
    profile_obj, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            streak = data.get('streak')
            board = data.get('board')
            class_name = data.get('class_name')

            if name:
                request.user.username = name
            if email:
                request.user.email = email
            request.user.save()

            if board:
                profile_obj.board = board
            if class_name:
                profile_obj.class_name = class_name
            if streak is not None:
                try:
                    profile_obj.streak = int(streak)
                except ValueError:
                    pass
            profile_obj.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    questions_count = Question.objects.count()
    chapters_count = Question.objects.values('chapter').distinct().count()
    papers_count = Paper.objects.count()
    
    context = {
        'questions_count': questions_count,
        'chapters_count': chapters_count,
        'papers_count': papers_count,
        'profile': profile_obj,
    }
    return render(request, 'profile.html', context)


@login_required
def night_before(request):
    if request.method == 'POST':
        exam_type = request.POST.get('exam_type', 'School Board')
        class_year = request.POST.get('class_year', '10th Grade')
        subject = request.POST.get('subject', 'Physics')
        prep_state = request.POST.get('prep_state', 'Starting Out')
        focus_hours = request.POST.get('focus_hours', '4')
        exam_date = request.POST.get('exam_date', '')

        # Format exam_date into readable format
        from datetime import datetime
        exam_date_formatted = "Tomorrow"
        if exam_date:
            try:
                dt = datetime.strptime(exam_date, "%Y-%m-%d")
                exam_date_formatted = dt.strftime("%B %d, %Y")
            except Exception:
                # If date is corrupted or has extra digits from automated inputs, try to sanitize
                import re
                match = re.search(r'(\d{4})-(\d{2})-(\d{2})', exam_date)
                if match:
                    try:
                        dt = datetime.strptime(match.group(0), "%Y-%m-%d")
                        exam_date_formatted = dt.strftime("%B %d, %Y")
                    except Exception:
                        exam_date_formatted = exam_date
                else:
                    exam_date_formatted = exam_date

        # Fetch matching questions from database based on subject
        questions = Question.objects.filter(subject__icontains=subject)[:3]
        if not questions:
            questions = Question.objects.filter(subject__icontains='Physics')[:3]

        context = {
            'sprint_active': True,
            'exam_type': exam_type,
            'class_year': class_year,
            'subject': subject,
            'prep_state': prep_state,
            'focus_hours': focus_hours,
            'exam_date': exam_date_formatted,
            'questions': questions,
        }
        return render(request, 'night_before.html', context)

    return render(request, 'night_before.html', {'sprint_active': False})


@login_required
def start_mock_test(request):
    chapter = request.GET.get("chapter", "")
    return render(request, 'start_mock_test.html', {'chapter': chapter})


@login_required
def start_mock_test_api(request):
    chapter = request.GET.get("chapter", "")
    
    # Fetch questions from database for this chapter
    questions = Question.objects.filter(chapter=chapter)
    if not questions:
        questions = Question.objects.all()[:10]  # Fallback
    
    questions_list = [q.question_text for q in questions]
    
    try:
        raw_response = generate_mock_test_questions(chapter, questions_list)
        # Parse JSON
        text = raw_response.strip()
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        test_data = json.loads(text)
        return JsonResponse(test_data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def chat_support_api(request):
    if request.method != 'POST':
        return JsonResponse({"error": "POST required"}, status=400)
    
    try:
        data = json.loads(request.body)
        question_text = data.get('question_text', '')
        history = data.get('history', [])
        message = data.get('message', '')
        
        system_instruction = (
            "You are an empathetic, supportive therapist, teacher, and academic counselor for students "
            "who are feeling stressed, anxious, or depressed about their studies, exams, or personal challenges. "
            "Address the student's emotional concern with utmost care, and help explain academic concepts "
            "or offer comforting guidance. Balance being a patient, clear teacher and a warm, supportive counselor. "
            "Always maintain a gentle, reassuring, non-judgmental tone. If the student shows severe signs of distress, "
            "encourage them to reach out to a trusted professional, family member, or school authority, while remaining supportive."
        )
        
        prompt_parts = [system_instruction]
        if question_text:
            prompt_parts.append(f"Context Question: {question_text}\n")
        
        for turn in history:
            role_name = "Student" if turn['role'] == 'user' else "Therapist/Tutor"
            prompt_parts.append(f"{role_name}: {turn['text']}")
            
        prompt_parts.append(f"Student: {message}")
        prompt_parts.append("Therapist/Tutor:")
        
        full_prompt = "\n".join(prompt_parts)
        
        from .gemini_utils import client
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        
        return JsonResponse({"response": response.text})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
