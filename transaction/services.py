"""Service layer for transaction domain operations.

This abstracts MongoEngine direct access away from views to improve testability
and prepare for possible future storage changes.
"""
from __future__ import annotations
from typing import Iterable, Sequence
from datetime import datetime
from decimal import Decimal
from .models import Transaction, Goal
from django.core.cache import cache


class TransactionService:
    @staticmethod
    def list_user_transactions(
        user_id: int, limit: int | None = None
    ) -> Iterable[Transaction]:
        """Return recent user transactions optionally limited.

        Legacy helper retained for any existing callers.
        """
        qs = Transaction.objects(user_id=user_id).order_by('-created_at')
        if limit:
            qs = qs[:limit]
        return qs

    @staticmethod
    def list_user_transactions_filtered(
        *,
        user_id: int,
        date_from=None,
        date_to=None,
        categories: Sequence[str] | None = None,
        type_: str | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
    ) -> Iterable[Transaction]:
        """Return filtered transactions ordered newest first.

        All filter arguments are optional. categories can be a sequence of
        category strings. Amount filters are inclusive.
        """
        qs = Transaction.objects(user_id=user_id)
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__lte=date_to)
        if categories:
            qs = qs.filter(category__in=list(categories))
        if type_:
            qs = qs.filter(type=type_)
        if min_amount is not None:
            qs = qs.filter(amount__gte=min_amount)
        if max_amount is not None:
            qs = qs.filter(amount__lte=max_amount)
        return qs.order_by('-created_at')

    @staticmethod
    def create_transaction(
        user_id: int,
        *,
        type: str,
        amount,
        category: str,
        description: str = "",
    ) -> Transaction:
        tx = Transaction(
            user_id=user_id,
            type=type,
            amount=amount,
            category=category,
            description=description or "",
            created_at=datetime.utcnow(),
        )
        tx.save()
        return tx

    @staticmethod
    def user_summary(user_id: int) -> dict:
        """Return aggregated income/expense/net for a user.

        Cached for 30 seconds to reduce aggregation cost.
        """
        cache_key = f"tx_summary:{user_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": "$type",
                    "total": {"$sum": "$amount"},
                }
            },
        ]
        # Direct MongoEngine access to underlying collection
        coll = Transaction._get_collection()  # pylint: disable=protected-access
        totals = {"income": 0, "expense": 0}
        try:
            for row in coll.aggregate(pipeline):  # pragma: no branch - simple loop
                t = row.get("_id")
                if t in totals:
                    totals[t] = float(row.get("total", 0))
        except Exception:  # pragma: no cover - defensive
            pass
        result = {
            "totalIncome": totals["income"],
            "totalExpense": totals["expense"],
            "net": totals["income"] - totals["expense"],
        }
        cache.set(cache_key, result, timeout=30)
        return result


class GoalService:
    @staticmethod
    def list_user_goals(user_id: int) -> Iterable[Goal]:
        return Goal.objects(user_id=user_id)

    @staticmethod
    def create_goal(
        user_id: int,
        *,
        title: str,
        target_amount=None,
        current_amount=None,
        due_date=None,
        description: str = "",
        image: str = "/vercel.svg",
    ) -> Goal:
        goal = Goal(
            user_id=user_id,
            title=title,
            target_amount=target_amount,
            current_amount=current_amount or 0,
            due_date=due_date,
            description=description or "",
            image=image or "/vercel.svg",
        )
        goal.save()
        return goal
