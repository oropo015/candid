from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),  # Set the homepage view as the root URL
    path('start-exam/', views.start_exam, name='start_exam'),  # Add a new URL for starting the exam
    path('question/<int:question_id>/', views.question_view, name='question_view'),
    path('submit_answer/<int:question_id>/', views.submit_answer, name='submit_answer'),
    path('results/', views.results_view, name='results_view'),
    path('exam/restart/', views.restart_exam, name='restart_exam'),
    path('exam/certificate/', views.print_certificate, name='print_certificate'),
]
