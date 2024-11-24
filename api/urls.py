from django.urls import path, include
from .views import *
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

router = routers.DefaultRouter()
router.register('products', ProductViewSet, basename='products')
router.register('collections', CollectionViewSet)
router.register('carts', CartViewSet, basename='cart')
router.register('cart-items', CartItemViewSet, basename='cart-item')
router.register('orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('cart/<uuid:pk>/', CartViewSet.as_view(
        {'get': 'retrieve', 'delete': 'destroy'}), name='cart-detail'),
    path('order/<uuid:pk>/', OrderViewSet.as_view(
        {'get': 'retrieve', 'delete': 'destroy'}), name='order-detail'),
]
