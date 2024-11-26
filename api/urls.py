from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers
from .views import *

# Initialize the router
router = routers.DefaultRouter()

# Register viewsets with the router
router.register('products', ProductViewSet, basename='products')
router.register('collections', CollectionViewSet, basename='collections')
router.register('carts', CartViewSet, basename='cart')
router.register('orders', OrderViewSet, basename='order')


# Register Nested Routers here
product_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')
product_router.register('images', ProductImageViewSet,
                        basename='product-images')

cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_router.register('items', CartItemViewSet, basename='cart-items')
# Define the URL patterns
urlpatterns = [
    path('', include(router.urls)),
    path('', include(product_router.urls)),
    path('', include(cart_router.urls)),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

    # Custom URLs for Cart and Order retrieval/deletion
    path('cart/<uuid:pk>/',
         CartViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='cart-detail'),
    path('order/<uuid:pk>/', OrderViewSet.as_view(
        {'get': 'retrieve', 'delete': 'destroy'}), name='order-detail'),

]
