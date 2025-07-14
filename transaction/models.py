from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_lenght = 10, choices = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharFireld(max_length=150)
    description = models.CharField(max_length=255)
    crated_at = models.DateTimeField(auto_now_add=True)


class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
