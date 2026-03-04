from django.urls import path

from . import views

urlpatterns = [path("", views.index, name="index"),
	       path("index.html", views.index, name="index"),
	       path('UserLogin.html', views.UserLogin, name="UserLogin"),
	       path('UserLoginAction', views.UserLoginAction, name="UserLoginAction"),
	       path('AddUser.html', views.AddUser, name="AddUser"),
	       path('AddUserAction', views.AddUserAction, name="AddUserrAction"),
	       path('AdminLogin.html', views.AdminLogin, name="AdminLogin"), 
	       path('AdminLoginAction', views.AdminLoginAction, name="AdminLoginAction"),
	       path('SendCommand', views.SendCommand, name="SendCommand"), 
	       path('SendCommandAction', views.SendCommandAction, name="SendCommandAction"),
	       path('ViewHistory', views.ViewHistory, name="ViewHistory"),
	       path('Graph', views.Graph, name="Graph"),
	       path('ExtensionGraph', views.ExtensionGraph, name="ExtensionGraph"),
]