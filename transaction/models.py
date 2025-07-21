from django.db import models
from django.contrib.auth.models import User
from mongoengine import Document, StringField, IntField, DateTimeField, ReferenceField

class User(Document):
    id = StringField(primary_key=True)
    username = StringField(required=True)
    password = StringField(required=True)

class Transaction(models.Model):
    id = StringField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length = 10, choices = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=150)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.type}"

class Goal(models.Model):
    id = StringField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.title}  ({self.user.username})"