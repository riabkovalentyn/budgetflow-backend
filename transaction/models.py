from mongoengine import (
    Document,
    StringField,
    IntField,
    DateTimeField,
    DecimalField,
)
from datetime import datetime


class Transaction(Document):
    meta = {'collection': 'transactions'}

    user_id = IntField(required=True)  # Django auth user id
    type = StringField(required=True, choices=('income', 'expense'))
    amount = DecimalField(precision=2, required=True)
    category = StringField(required=True, max_length=150)
    description = StringField(default='')
    created_at = DateTimeField(default=datetime.utcnow)


class Goal(Document):
    meta = {'collection': 'goals'}

    user_id = IntField(required=True)
    title = StringField(required=True, max_length=100)
    target_amount = DecimalField(precision=2, required=True)
    current_amount = DecimalField(precision=2, default=0)
    due_date = DateTimeField(required=True)