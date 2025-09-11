from rest_framework import serializers
from .models import Transaction, Goal
from decimal import Decimal
from datetime import datetime, time as time_cls, date as date_cls


class TransactionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    type = serializers.ChoiceField(choices=(('income', 'income'), ('expense', 'expense')))
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    category = serializers.CharField(max_length=150)
    description = serializers.CharField(allow_blank=True, required=False, max_length=255)
    created_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        user = self.context['request'].user
        doc = Transaction(
            user_id=user.id,
            **validated_data,
        )
        doc.save()
        return doc

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update({
            'id': str(instance.id),
            'type': instance.type,
            'amount': float(instance.amount) if instance.amount is not None else 0.0,
            'category': instance.category,
            'description': getattr(instance, 'description', ''),
            'created_at': instance.created_at.isoformat() if getattr(instance, 'created_at', None) else None,
            # Frontend expects 'date' string
            'date': instance.created_at.date().isoformat() if getattr(instance, 'created_at', None) else None,
        })
        return data


class GoalSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=100)
    # Optional fields to match frontend
    target_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0, required=False)
    current_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, min_value=0)
    due_date = serializers.DateField(required=False)
    description = serializers.CharField(allow_blank=True, required=False, max_length=255)
    image = serializers.CharField(allow_blank=True, required=False, max_length=255)

    def create(self, validated_data):
        user = self.context['request'].user
        dd = validated_data.pop('due_date', None)
        if isinstance(dd, date_cls):
            due_dt = datetime.combine(dd, time_cls(0, 0))
        else:
            due_dt = dd
        doc = Goal(
            user_id=user.id,
            due_date=due_dt,
            **validated_data,
        )
        doc.save()
        return doc

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update({
            'id': str(instance.id),
            'title': instance.title,
            'target_amount': float(instance.target_amount) if instance.target_amount is not None else 0.0,
            'current_amount': float(getattr(instance, 'current_amount', Decimal('0'))),
            'due_date': instance.due_date.date().isoformat() if getattr(instance, 'due_date', None) else None,
            'description': getattr(instance, 'description', ''),
            'image': getattr(instance, 'image', '/vercel.svg'),
        })
        return data


class BankProviderSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()


class BankConnectionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    providerId = serializers.CharField(source='provider_id')
    providerName = serializers.CharField(source='provider_name')
    status = serializers.ChoiceField(choices=(
        ('connected', 'connected'), ('pending', 'pending'), ('error', 'error'), ('disconnected', 'disconnected')
    ))
    lastSyncedAt = serializers.DateTimeField(source='last_synced_at', required=False, allow_null=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Convert id and dates to expected shapes
        data['id'] = str(instance.id)
        if getattr(instance, 'last_synced_at', None):
            data['lastSyncedAt'] = instance.last_synced_at.isoformat()
        else:
            data['lastSyncedAt'] = None
        return data


class BankSyncScheduleSerializer(serializers.Serializer):
    enabled = serializers.BooleanField()
    intervalHours = serializers.IntegerField(source='interval_hours')
    nextRunAt = serializers.DateTimeField(source='next_run_at', required=False, allow_null=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if getattr(instance, 'next_run_at', None):
            data['nextRunAt'] = instance.next_run_at.isoformat()
        else:
            data['nextRunAt'] = None
        return data
