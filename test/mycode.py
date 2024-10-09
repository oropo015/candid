from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from .models import Question, Answer, ExamResult

def start_exam(request):
    # Reset the session variables for a new exam
    request.session['correct_answers'] = 0
    request.session['total_questions'] = Question.objects.count()

    first_question = Question.objects.first()  # Get the first question
    if first_question:
        return redirect('question_view', question_id=first_question.id)
    else:
        return render(request, 'exam/exam.html')  # Handle no questions
    


def question_view(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    answers = question.answers.all()  # Use the related name 'answers'
    return render(request, 'exam/exam.html', {'question': question, 'answers': answers})

def submit_answer(request, question_id):
    # Ensure the session variables are initialized
    if 'correct_answers' not in request.session:
        request.session['correct_answers'] = 0
    if 'total_questions' not in request.session:
        request.session['total_questions'] = Question.objects.count()

    selected_answer = request.POST.get('answer')

    if not selected_answer:
        # If no answer is selected, redirect back to the same question
        return HttpResponseRedirect(f'/exam/question/{question_id}/')

    question = get_object_or_404(Question, pk=question_id)
    selected_answer_obj = get_object_or_404(Answer, pk=selected_answer)

    # Check if the selected answer is correct and update the score
    if selected_answer_obj.is_correct:  # Assuming the Answer model has 'is_correct'
        request.session['correct_answers'] += 1

    next_question_id = get_next_question_id(question_id)

    if next_question_id:
        return HttpResponseRedirect(f'/exam/question/{next_question_id}/')
    else:
        # Calculate and save the final score
        correct_answers = request.session['correct_answers']
        total_questions = request.session['total_questions']
        
        # Handle division by zero error
        if total_questions == 0:
            score_percentage = 0  # No questions, no score
        else:
            score_percentage = (correct_answers / total_questions) * 100

        # Save the result to the ExamResult model
        ExamResult.objects.create(
            student_name=request.user.username,
            score=score_percentage,
            passed=score_percentage >= 50  # Assuming passing is 50%
        )

        # Clear session data after exam is finished
        request.session['correct_answers'] = 0
        request.session['total_questions'] = 0

        return redirect('/exam/results/')


def get_next_question_id(current_question_id):
    """Retrieve the next question ID after the current question."""
    next_question = Question.objects.filter(id__gt=current_question_id).first()
    return next_question.id if next_question else None

def results_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            # Use the student_name field instead of user
            latest_result = ExamResult.objects.filter(student_name=request.user.username).order_by('-id').first()
            if latest_result:
                score = latest_result.score
                passed = latest_result.passed
            else:
                score = 0
                passed = False
        else:
            score = 0
            passed = False

        return render(request, 'exam/result.html', {
            'score': score,
            'passed': passed
        })
    else:
        return redirect('/')  # Redirect to home or another page if not GET request
    

def restart_exam(request):
    # Reset the session variables for the exam
    request.session['correct_answers'] = 0
    request.session['total_questions'] = Question.objects.count()

    # Redirect to the first question
    first_question = Question.objects.first()
    if first_question:
        return redirect('question_view', question_id=first_question.id)
    else:
        return redirect('/')  # Redirect to homepage if there are no questions

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from fpdf import FPDF
from .models import Question, Answer, ExamResult

# Other views like start_exam, question_view, etc.

class PDF(FPDF):
    def header(self):
        # Add the title of the certificate
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Certificate of Achievement', ln=True, align='C')

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_certificate_body(self, student_name, score):
        # Add student details and passing message
        self.ln(20)  # Move 20 units down from the header
        self.set_font('Arial', '', 12)
        self.cell(0, 10, f'Congratulations {student_name}!', ln=True, align='C')
        self.ln(10)
        self.cell(0, 10, f'You have successfully passed the exam with a score of {score}%.', ln=True, align='C')
        self.ln(10)
        self.cell(0, 10, 'Keep up the great work!', ln=True, align='C')

def print_certificate(request):
    # Check if the user passed the exam
    latest_result = ExamResult.objects.filter(student_name=request.user.username).order_by('-id').first()

    if latest_result and latest_result.passed:
        # Create a PDF certificate
        pdf = PDF()
        pdf.add_page()
        pdf.add_certificate_body(request.user.username, latest_result.score)

        # Prepare the HTTP response with PDF headers
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="certificate.pdf"'

        # Output the generated PDF to the response
        pdf.output(response, 'F')

        return response
    else:
        return HttpResponse("You haven't passed the exam yet!", status=400)
