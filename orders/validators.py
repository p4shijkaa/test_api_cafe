from rest_framework.validators import ValidationError
from .models import Order


def validate_status_transition(old_status, new_status):
	allowed_transitions = Order.STATUS_TRANSITIONS.get(old_status, [])
	if new_status not in allowed_transitions:
		raise ValidationError(
			f"Недопустимый переход статуса: с '{old_status}' на '{new_status}'"
		)


def validate_order_cancelation(status):
	if status != 'pending':
		raise ValidationError(
			"Заказ можно отменить только в статусе 'В обработке'"
		)
