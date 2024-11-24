from django.urls import path, include
from . import views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView


router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
