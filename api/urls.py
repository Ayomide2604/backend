from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

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

    # JWT authentication token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Custom URLs for Cart and Order retrieval/deletion
    path('cart/<uuid:pk>/',
         CartViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='cart-detail'),
    path('order/<uuid:pk>/', OrderViewSet.as_view(
        {'get': 'retrieve', 'delete': 'destroy'}), name='order-detail'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
