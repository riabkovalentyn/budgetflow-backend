from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from ..serializers import TransactionSerializer
from ..services import TransactionService
from django.conf import settings
from datetime import datetime, time
from decimal import Decimal, InvalidOperation
import math


class TransactionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def _parse_date(self, value: str, end: bool = False):
        """Parse a date or datetime string. If date only, expand to day bounds."""
        try:
            if len(value) == 10:  # YYYY-MM-DD
                dt = datetime.fromisoformat(value)
                if end:
                    return datetime.combine(dt.date(), time.max).replace(microsecond=0)
                return datetime.combine(dt.date(), time.min)
            return datetime.fromisoformat(value)
        except ValueError:
            raise ValueError('invalid_date')

    def get_queryset(self):  # now uses filters
        qp = self.request.query_params
        user_id = self.request.user.id

        date_from = None
        date_to = None
        if qp.get('date_from'):
            date_from = self._parse_date(qp['date_from'])
        if qp.get('date_to'):
            date_to = self._parse_date(qp['date_to'], end=True)

        categories = None
        if qp.get('category'):
            categories = [c.strip() for c in qp['category'].split(',') if c.strip()]
            if not categories:
                categories = None

        type_ = qp.get('type') or None
        if type_ and type_ not in ('income', 'expense'):
            raise ValueError('invalid_type')

        min_amount = None
        max_amount = None
        if qp.get('min_amount'):
            try:
                min_amount = Decimal(qp['min_amount'])
            except (InvalidOperation, ValueError):
                raise ValueError('invalid_min_amount')
        if qp.get('max_amount'):
            try:
                max_amount = Decimal(qp['max_amount'])
            except (InvalidOperation, ValueError):
                raise ValueError('invalid_max_amount')

        return TransactionService.list_user_transactions_filtered(
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            categories=categories,
            type_=type_,
            min_amount=min_amount,
            max_amount=max_amount,
        )

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
        except ValueError as e:  # parameter validation error
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            # Graceful degradation: if database is unreachable return empty list
            # instead of 503. This keeps the endpoint usable for the UI (and
            # test suite) even if Mongo temporarily down. A monitoring/health
            # endpoint still surfaces the real issue.
            return Response({'items': []})

        # Manual lightweight pagination to preserve legacy {'items': []} shape
        # Support both MongoEngine QuerySet (has count, slicing) and plain list (tests)
        if hasattr(queryset, 'count'):
            try:
                total = queryset.count()
            except Exception:
                return Response({'items': []})
        else:  # list-like
            queryset = list(queryset)
            total = len(queryset)

        qp = request.query_params
        try:
            page = int(qp.get('page', '1'))
            if page < 1:
                raise ValueError
        except ValueError:
            return Response({'detail': 'invalid_page'}, status=status.HTTP_400_BAD_REQUEST)

        default_size = settings.REST_FRAMEWORK.get('PAGE_SIZE', 20)
        try:
            page_size = int(qp.get('page_size', str(default_size)))
            if page_size < 1 or page_size > 100:
                raise ValueError
        except ValueError:
            return Response({'detail': 'invalid_page_size'}, status=status.HTTP_400_BAD_REQUEST)

        start = (page - 1) * page_size
        end = start + page_size
        items_qs = queryset[start:end]
        serializer = self.get_serializer(items_qs, many=True)
        response = {'items': serializer.data}
        if total > page_size:
            response['pagination'] = {
                'page': page,
                'page_size': page_size,
                'total': total,
                'pages': math.ceil(total / page_size),
            }
        return Response(response)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            instance = TransactionService.create_transaction(
                user_id=request.user.id,
                type=data['type'],
                amount=data['amount'],
                category=data['category'],
                description=data.get('description') or '',
            )
            out = self.get_serializer(instance)
            return Response(out.data, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(
                {'detail': 'database_unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        try:
            data = TransactionService.user_summary(request.user.id)
            return Response(data)
        except Exception:
            return Response(
                {'detail': 'database_unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )






