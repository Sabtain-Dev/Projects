from django.urls import path
from finance.views import RegisterView, DashboardView, TransactionCreateView, TransactionListView, GoalCreateView, GoalDeleteView, export_transactions_csv

urlpatterns = [
    path('', RegisterView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('transaction/add/', TransactionCreateView.as_view(), name='transaction-add'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('goal/add/', GoalCreateView.as_view(), name='goal-add'),
    path('goal/delete/<int:pk>/', GoalDeleteView.as_view(), name='goal-delete'),
    path('export-transactions/', export_transactions_csv, name='export_transactions'),

]