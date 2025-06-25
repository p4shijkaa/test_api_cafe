from rest_framework import serializers
from .models import Dish, Order
from .validators import validate_other_cancelation, validate_status_transition