from django.urls import include,path
from home import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('paper/', views.papers, name='paper'),
    # path('search/', views.search_papers, name='search'),
    path("questions/", views.chapter_questions, name="questions"),
    path('chapters/', views.chapters, name='chapters'),
    path('explain/<int:question_id>/', views.explain_question_api, name='explain_question'),
    path('mock/', views.mock_tests, name='mock_tests'),
    path('mock/start/', views.start_mock_test, name='start_mock_test'),
    path('mock/start/api/', views.start_mock_test_api, name='start_mock_test_api'),
    path('chat-support/', views.chat_support_api, name='chat_support_api'),
    path('profile/', views.profile, name='profile'),
    path('night-before/', views.night_before, name='night_before'),
]