from rest_framework import serializers
from .models import Transaction, Goal
from decimal import Decimal
from datetime import datetime, time as time_cls, date as date_cls


class TransactionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    type = serializers.ChoiceField(choices=['income', 'expense'])
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    category = serializers.CharField(max_length=150)
    description = serializers.CharField(allow_blank=True, required=False)
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
        })
        return data


class GoalSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=100)
    target_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    current_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    due_date = serializers.DateField()

    def create(self, validated_data):
        user = self.context['request'].user
        dd = validated_data.pop('due_date')
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
        })
        return data
