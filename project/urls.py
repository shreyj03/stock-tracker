# project/urls.py
# Shrey Jain, shreyj@bu.edu, 4/27/2026
# URL mappings for the stock portfolio tracker application.

from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.MainPageView.as_view(), name='main'),
    path('stocks/', views.StockListView.as_view(), name='stock-list'),
    path('stocks/<int:pk>/', views.StockDetailView.as_view(), name='stock-detail'),
    path('profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('watchlist/<int:pk>/', views.WatchlistDetailView.as_view(), name='watchlist-detail'),
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    path('login/', auth_views.LoginView.as_view(template_name='project/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='main'), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('transactions/add/', views.AddTransactionView.as_view(), name='add-transaction'),
    path('transactions/<int:pk>/delete/', views.DeleteTransactionView.as_view(), name='delete-transaction'),
    path('profile/<int:pk>/edit/', views.EditProfileView.as_view(), name='edit-profile'),
    path('stocks/<int:stock_pk>/watch/', views.AddToWatchlistView.as_view(), name='add-watchlist'),
    path('watchlist/<int:pk>/delete/', views.DeleteWatchlistView.as_view(), name='delete-watchlist'),
]