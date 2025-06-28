from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Dish, Order
from .serializers import (
	DishSerializer,
	OrderSerializer,
	OrderStatusSerializer,
	OrderCancelSerializer
)


class DishViewSet(viewsets.ModelViewSet):
	queryset = Dish.objects.all()
	serializer_class = DishSerializer
	filterset_fields = ['category']
	search_fields = ['name']

	def destroy(self, request, *args, **kwargs):
		instance = self.get_object()

		active_orders = Order.objects.exclude(
			status__in=['completed', 'canceled']
		).filter(dishes=instance)

		if active_orders.exists():
			return Response(
				{"detail": "Нельзя удалить блюдо, используемое в активных заказах"},
				status=status.HTTP_400_BAD_REQUEST
			)

		return super().destroy(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
	queryset = Order.objects.all()
	serializer_class = OrderSerializer
	filterset_fields = ['status']
	search_fields = ['customer_name']

	def get_serializer_class(self):
		if self.action == 'update_status':
			return OrderStatusSerializer
		if self.action == 'cancel_order':
			return OrderCancelSerializer
		return super().get_serializer_class()

	@action(detail=True, methods=['patch'], url_path='update-status')
	def update_status(self, request, pk=None):
		order = self.get_object()
		serializer = self.get_serializer(order, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data)

	@action(detail=True, methods=['post'], url_path='cancel')
	def cancel_order(self, request, pk=None):
		order = self.get_object()
		serializer = self.get_serializer(order, data=request.data)
		serializer.is_valid(raise_exception=True)
		order.status = 'canceled'
		order.save()
		return Response({'status': 'Заказ отменен'}, status=status.HTTP_200_OK)

	def destroy(self, request, *args, **kwargs):
		order = self.get_object()
		if order.status != 'pending':
			return Response(
				{"detail": "Можно удалять только заказы в статусе 'В обработке'"},
				status=status.HTTP_400_BAD_REQUEST
			)
		return super().destroy(request, *args, **kwargs)
