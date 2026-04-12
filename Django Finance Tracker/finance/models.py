from django.db import models
from django.contrib.auth.models import User


# -------------------- TRANSACTION MODEL -------------------- #
class Transaction(models.Model):

    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateField()
    category = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title} - {self.amount}"


# -------------------- GOAL MODEL -------------------- #
class Goal(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField()

    def progress_percentage(self):
        """
        Safe progress calculation for dashboard
        """
        if self.target_amount > 0:
            return (self.current_amount / self.target_amount) * 100
        return 0

    def is_completed(self):
        """
        Helper method to check if goal is completed
        """
        return self.current_amount >= self.target_amount

    def __str__(self):
        status = "✅" if self.is_completed() else "⏳"
        return f"{status} {self.name}"