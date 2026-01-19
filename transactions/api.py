# transactions/api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction
from .serializers import TransactionSerializer


class TransactionListAPI(APIView):
    """API: получить список транзакций текущего пользователя"""

    def get(self, request):
        qs = Transaction.objects.filter(user=request.user)
        serializer = TransactionSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
