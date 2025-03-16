from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CategoryListCreateView,BuyerOrdersView, EnquiryStatusUpdateView,
   
    WishlistView, CartView, CartUpdateView, CartDeleteView, OrderCreateView, product_detail, product_list_create, validate_token
)
from .views import RegisterAPIView, LoginAPIView, ListUsersAPIView, UpdateUserAPIView, DeleteUserAPIView,EnquiryViewSet
from .views import SellerOrdersView, UpdateOrderItemStatusView,OrderItemStatusUpdateAPIView

enquiry_list = EnquiryViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

urlpatterns = [
    # Authentication and Registration Routes
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('users/<str:user_type>/', ListUsersAPIView.as_view(), name='list_users'),
    path('user/update/', UpdateUserAPIView.as_view(), name='update_user'),
    path('user/delete/<int:user_id>/', DeleteUserAPIView.as_view(), name='delete_user'),
    path("wishlist/", WishlistView.as_view(), name="wishlist"),
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/update/", CartUpdateView.as_view(), name="cart-update"),
    path("cart/delete/", CartDeleteView.as_view(), name="cart-delete"),
    path("order/create/", OrderCreateView.as_view(), name="order-create"),
    path('order-items/<int:order_item_id>/update-status/', OrderItemStatusUpdateAPIView.as_view(), name='order-item-status-update'),
    path('products/', product_list_create, name='product-list-create'),
    path('products/<int:pk>/', product_detail, name='product-detail'),
    path('seller/orders/', SellerOrdersView.as_view(), name='seller-orders'),
    path('enquiries/', enquiry_list, name='enquiry'), 
    path('buyer/orders/', BuyerOrdersView.as_view(), name='buyer-orders'),
    path('order-item/<int:order_item_id>/update-status/', UpdateOrderItemStatusView.as_view(), name='update-order-item-status'),
     path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
     path('enquiries/<int:pk>/status/', EnquiryStatusUpdateView.as_view({'put': 'update'}), name='enquiry-status-update'),
      path('validate-token/', validate_token, name='validate-token'),  

]
 