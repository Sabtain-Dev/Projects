from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
import csv

from finance.forms import RegisterForm, TransactionForm, GoalForm
from .models import Transaction, Goal


# -------------------- REGISTER VIEW -------------------- #
class RegisterView(View):

    def get(self, request, *args, **kwargs):
        form = RegisterForm()
        return render(request, 'finance/register.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')

        return render(request, 'finance/register.html', {'form': form})


# -------------------- DASHBOARD VIEW -------------------- #
class DashboardView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        transactions = Transaction.objects.filter(
            user=request.user
        ).order_by('-date')[:5]

        goals = Goal.objects.filter(
            user=request.user
        ).order_by('deadline')

        total_income = Transaction.objects.filter(
            user=request.user,
            transaction_type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_expense = Transaction.objects.filter(
            user=request.user,
            transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0

        net_balance = total_income - total_expense
        remaining_balance = net_balance

        goal_progress = []

        for goal in goals:
            if remaining_balance >= goal.target_amount:
                progress = 100
                remaining_balance -= goal.target_amount

            elif remaining_balance > 0:
                progress = (remaining_balance / goal.target_amount) * 100
                remaining_balance = 0

            else:
                progress = 0

            goal_progress.append({
                'goal': goal,
                'progress': round(progress, 2)
            })

        context = {
            'transactions': transactions,
            'goals': goals,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_balance': net_balance,
            'goal_progress': goal_progress,
        }

        return render(request, 'finance/dashboard.html', context)


# -------------------- TRANSACTION CREATE -------------------- #
class TransactionCreateView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        form = TransactionForm()
        return render(request, 'finance/transaction_form.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = TransactionForm(request.POST)

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')

        return render(request, 'finance/transaction_form.html', {'form': form})


# -------------------- TRANSACTION LIST -------------------- #
class TransactionListView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        transactions = Transaction.objects.filter(
            user=request.user
        ).order_by('-date')

        return render(request, 'finance/transaction_list.html', {
            'transactions': transactions
        })


# -------------------- GOAL CREATE -------------------- #
class GoalCreateView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        form = GoalForm()
        return render(request, 'finance/goal_form.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = GoalForm(request.POST)

        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('dashboard')

        return render(request, 'finance/goal_form.html', {'form': form})


# -------------------- GOAL DELETE -------------------- #
class GoalDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):
        goal = get_object_or_404(Goal, pk=pk, user=request.user)
        goal.delete()
        return redirect('dashboard')


# -------------------- EXPORT TRANSACTIONS TO CSV -------------------- #
@login_required
def export_transactions_csv(request):

    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)

    # Headers (Match your table)
    writer.writerow(['Date', 'Title', 'Amount', 'Type'])

    for transaction in transactions:

        # Convert to Credit / Debit like your UI
        if transaction.transaction_type == "income":
            tx_type = "Credit"
        elif transaction.transaction_type == "expense":
            tx_type = "Debit"
        else:
            tx_type = "-"

        writer.writerow([
            transaction.date,
            transaction.title,
            transaction.amount,
            tx_type
        ])

    return response