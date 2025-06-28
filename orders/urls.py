from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, DishViewSet

router = DefaultRouter()
router.register(r'dishes', DishViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
	path('', include(router.urls))
]