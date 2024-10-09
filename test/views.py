from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from fpdf import FPDF
from .models import Question, Answer, ExamResult

def homepage(request):
    passing_score = 50  # Define the passing score, e.g., 50%
    
    if request.method == 'POST':
        # Get the candidate's name from the form
        candidate_name = request.POST.get('candidate_name')
        
        # Save candidate name to session
        request.session['candidate_name'] = candidate_name

        # Redirect to the start of the exam
        return redirect('start_exam')
    
    return render(request, 'exam/homepage.html', {'passing_score': passing_score})

def start_exam(request):
    # Check if the candidate name exists in the session
    if 'candidate_name' not in request.session:
        return redirect('homepage')  # Redirect to homepage if no candidate name

    # Reset the session variables for a new exam
    request.session['correct_answers'] = 0
    request.session['total_questions'] = Question.objects.count()

    # Get candidate name from the session
    candidate_name = request.session.get('candidate_name', 'Candidate')

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

def print_certificate(request):
    # Retrieve candidate name from the session
    candidate_name = request.session.get('candidate_name', 'Candidate')

    # Check if the user passed the exam
    latest_result = ExamResult.objects.filter(student_name=request.user.username).order_by('-id').first()

    if latest_result and latest_result.passed:
        # Create a PDF certificate in landscape mode
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()

        # Add a border
        pdf.set_draw_color(50, 50, 100)  # Set border color
        pdf.rect(10, 10, 277, 190)  # Draw a rectangle for the border

        # Add the certificate title
        pdf.set_font('Arial', 'B', 24)
        pdf.set_text_color(0, 102, 204)  # Set title color
        pdf.cell(0, 20, 'Certificate of Achievement', ln=True, align='C')

        # Add a line under the title
        pdf.ln(5)  # Move a little bit down after the title
        pdf.set_line_width(1)
        pdf.line(15, 30, 282, 30)  # A horizontal line below the title

        # Add some space
        pdf.ln(20)

        # Add the recipient's name (Candidate's name from the session)
        pdf.set_font('Arial', 'B', 20)
        pdf.set_text_color(0, 0, 0)  # Set text color to black
        pdf.cell(0, 10, f'This certificate is proudly presented to', ln=True, align='C')
        pdf.ln(10)
        pdf.cell(0, 10, f'{candidate_name}', ln=True, align='C')

        # Add a line under the candidate's name
        pdf.ln(5)
        pdf.set_line_width(0.5)
        pdf.line(100, pdf.get_y(), 210, pdf.get_y())  # Line for the candidate's name

        # Add some space
        pdf.ln(15)

        # Add the body content (score and congratulations message)
        pdf.set_font('Arial', '', 16)
        pdf.cell(0, 10, f'for successfully passing the exam with a score of {latest_result.score:.2f}%.', ln=True, align='C')
        pdf.ln(10)
        pdf.cell(0, 10, 'Your hard work and dedication are truly commendable.', ln=True, align='C')

        # Add some more space
        pdf.ln(30)

        # Add signature and date lines
        pdf.set_font('Arial', 'I', 14)
        pdf.cell(0, 10, '______________________________', ln=False, align='L')
        pdf.cell(0, 10, '______________________________', ln=True, align='R')
        pdf.cell(0, 10, 'Authorized Signature', ln=False, align='L')
        pdf.cell(0, 10, 'Date', ln=True, align='R')

        # Prepare the HTTP response with PDF headers
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="certificate.pdf"'

        # Output the generated PDF to the response
        pdf_output = pdf.output(dest='S').encode('latin1')  # Generate the PDF content as a string
        response.write(pdf_output)

        return response
    else:
        return HttpResponse("You haven't passed the exam yet!", status=400)
