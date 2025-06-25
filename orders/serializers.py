from rest_framework import serializers

from validators import validate_order_cancelation, validate_status_transition
from .models import Dish, Order


class DishSerializer(serializers.ModelSerializer):
	class Meta:
		model = Dish
		fields = ['id', 'name', 'description', 'price', 'category']
		read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
	dishes = DishSerializer(many=True, read_only=True)
	dish_ids = serializers.PrimaryKeyRelatedField(
		many=True,
		queryset=Dish.objects.all(),
		write_only=True,
		source='dishes'
	)
	status = serializers.CharField(read_only=True)

	class Meta:
		model = Order
		fields = [
			'id', 'customer_name', 'dishes', 'dish_ids',
			'order_time', 'status', 'total_price'
		]
		read_only_fields = ['id', 'order_time', 'total_price']

	def create(self, validated_data):
		dishes = validated_data.pop('dishes', [])
		order = Order.objects.create(**validated_data)
		order.dishes.set(dishes)
		order.save()  # Для пересчета суммы
		return order


class OrderStatusSerializer(serializers.ModelSerializer):
	class Meta:
		model = Order
		fields = ['id', 'status']
		read_only_fields = ['id']

	def validate_status(self, value):
		instance = self.instance
		validate_status_transition(instance.status, value)
		return value


class OrderCancelSerializer(serializers.ModelSerializer):
	class Meta:
		model = Order
		fields = ['id']
		read_only_fields = ['id']

	def validate(self, attrs):
		validate_order_cancelation(self.instance.status)
		return attrs
