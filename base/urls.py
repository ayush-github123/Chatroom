from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('room', views.roomDisplay, name='roomDisplay'),
    path('room/<str:pk>/', views.room, name='room'),
    path('create-room', views.createRoom, name="create-room"),
    path('update-room/<str:pk>', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>', views.deleteRoom, name="delete-room"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('register', views.registration, name="register"),
    path('delete-message/<str:pk>', views.deleteMessage, name="delete-message"),
    path('user-profile/<str:pk>/', views.userProfile, name="user-profile"),
    path('blog-page', views.blog_page, name="blog-page"),
    path('create-blog', views.Createblog, name="Createblog"),
    path('about', views.about, name="about"),
]
