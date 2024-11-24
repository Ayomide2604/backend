from django.urls import path, include
import views
from rest_framework import routers
router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)


urlpatterns = [
    path('api/', include(router.urls)),

]
