from rest_framework import serializers
from .models import Transaction, Goal

class TransactionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    user = serializers.CharField()
    type = serializers.ChoiceField(choices=['income', 'expense'])
    amount = serializers.FloatField()
    category = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    created_at = serializers.DateTimeField()

    def create(self, validated_data):
        return Transaction(**validated_data).save()

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class GoalSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    user = serializers.CharField()
    title = serializers.CharField()
    target_amount = serializers.FloatField()
    current_amount = serializers.FloatField()
    due_date = serializers.DateField()

    def create(self, validated_data):
        return Goal(**validated_data).save()

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
