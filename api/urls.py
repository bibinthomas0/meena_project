from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, SellerRegisterView, BuyerRegisterView, LoginView, 
    SellerLoginView, BuyerLoginView,UserRegisterView,
    WishlistView, CartView, CartUpdateView, CartDeleteView, OrderCreateView, OrderCancelView, product_detail, product_list_create
)


urlpatterns = [
    # Authentication and Registration Routes
    path('seller/register/', SellerRegisterView.as_view(), name='seller-register'),
    path('buyer/register/', BuyerRegisterView.as_view(), name='buyer-register'),
    path('login/', LoginView.as_view(), name='login'),
    path('seller/login/', SellerLoginView.as_view(), name='seller-login'),
    path('buyer/login/', BuyerLoginView.as_view(), name='buyer-login'),
    path('user/register/', UserRegisterView.as_view(), name='user_register'),
    path("wishlist/", WishlistView.as_view(), name="wishlist"),
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/update/", CartUpdateView.as_view(), name="cart-update"),
    path("cart/delete/", CartDeleteView.as_view(), name="cart-delete"),
    path("order/create/", OrderCreateView.as_view(), name="order-create"),
    path("order/cancel/<int:pk>/", OrderCancelView.as_view(), name="order-cancel"),

    path('api/products/', product_list_create, name='product-list-create'),
    path('api/products/<int:pk>/', product_detail, name='product-detail'),
]
api_router = DefaultRouter()
api_router.register(r'categories', CategoryViewSet, basename='category')