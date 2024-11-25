from django.urls import path, include
from rest_framework import routers
from .views import *

# Initialize the router
router = routers.DefaultRouter()

# Register viewsets with the router
router.register('products', ProductViewSet, basename='products')
router.register('collections', CollectionViewSet, basename='collections')
router.register('carts', CartViewSet, basename='cart')
router.register('cart-items', CartItemViewSet, basename='cart-item')
router.register('orders', OrderViewSet, basename='order')

# Define the URL patterns
urlpatterns = [
    path('', include(router.urls)),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    # Custom URLs for Cart and Order retrieval/deletion
    path('cart/<uuid:pk>/',
         CartViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='cart-detail'),
    path('order/<uuid:pk>/', OrderViewSet.as_view(
        {'get': 'retrieve', 'delete': 'destroy'}), name='order-detail'),

]
