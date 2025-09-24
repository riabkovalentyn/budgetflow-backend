from mongoengine import (
    Document,
    StringField,
    IntField,
    DateTimeField,
    DecimalField,
)
from datetime import datetime


class Transaction(Document):
    meta = {
        'collection': 'transactions',
        'indexes': [
            {'fields': ['user_id', '-created_at'], 'name': 'user_created_desc'},
            {'fields': ['user_id', 'category'], 'name': 'user_category'},
            {'fields': ['user_id', 'type'], 'name': 'user_type'},
        ],
    }

    user_id = IntField(required=True)  # Django auth user id
    type = StringField(required=True, choices=('income', 'expense'))
    amount = DecimalField(precision=2, rounding='ROUND_HALF_UP', required=True)
    category = StringField(required=True, max_length=150)
    description = StringField(default='')
    created_at = DateTimeField(default=datetime.utcnow)


class Goal(Document):
    meta = {
        'collection': 'goals',
        'indexes': [
            {'fields': ['user_id', 'title'], 'name': 'user_title'},
            {'fields': ['user_id', '-due_date'], 'name': 'user_due_desc'},
        ],
    }

    user_id = IntField(required=True)
    title = StringField(required=True, max_length=100)
    # Make fields optional to be compatible with simplified frontend goals
    target_amount = DecimalField(precision=2, rounding='ROUND_HALF_UP', required=False, null=True)
    current_amount = DecimalField(precision=2, rounding='ROUND_HALF_UP', default=0)
    due_date = DateTimeField(required=False, null=True)
    # Frontend-specific fields
    description = StringField(default='')
    image = StringField(default='/vercel.svg')


class BankConnection(Document):
    meta = {
        'collection': 'bank_connections',
        'indexes': [
            {'fields': ['user_id', 'provider_id'], 'name': 'user_provider', 'unique': True},
            {'fields': ['status'], 'name': 'status_only'},
        ],
    }

    user_id = IntField(required=True)
    provider_id = StringField(required=True)
    provider_name = StringField(required=True)
    status = StringField(required=True, choices=(
        'connected', 'pending', 'error', 'disconnected'
    ), default='pending')
    last_synced_at = DateTimeField(default=None)


class BankSyncSchedule(Document):
    meta = {
        'collection': 'bank_sync_schedules',
        'indexes': [
            {'fields': ['user_id'], 'name': 'user_only', 'unique': True},
            {'fields': ['next_run_at'], 'name': 'next_run'},
        ],
    }

    user_id = IntField(required=True)
    enabled = IntField(default=0)  # 0/1 to keep it simple in Mongo
    interval_hours = IntField(default=2)
    next_run_at = DateTimeField(default=None)
