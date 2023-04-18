from django.urls import path, include
from . import views
from rest_framework import routers


router = routers.DefaultRouter()
router.register('roles', views.RoleView)
router.register('users', views.UserView)
router.register('customers', views.CustomerView)
router.register('categories', views.CategoryView)
router.register('suppliers', views.SupplierView)
router.register('products', views.ProductView)
router.register('transactions', views.TransactionView)
router.register('transaction-items', views.Transaction_ItemView)


urlpatterns = [
    path('register-user/', views.CustomUserView.register_user),
    path('login/', views.CustomUserView.login),
    path('current-user/', views.CustomUserView.current_user),
    path('profile_view/', views.CustomUserView.user_profile),
    path('update-profile/', views.CustomUserView.update_profile),
    path('refresh-token/', views.CustomUserView.refresh_token),
    path('logout/', views.CustomUserView.logout),
    path('forgot_password/', views.CustomUserView.forgot_password),
    path('reset_password/', views.CustomUserView.reset_password),
    path('get_products/', views.CustomView.get_products_category_supplier),
    path('get_product_detail/', views.CustomView.get_product_detail),
    path('get_transaction_customer/', views.CustomView.get_transaction_customer),
    path('get_transaction_item_detail/', views.CustomView.get_transaction_item_detail),
    path('get_users_role/', views.CustomView.get_users_role),
    path('update_users/<int:pk>', views.CustomView.update_users),
    path('get_current_user/', views.CustomView.get_current_user),
    path('count_customers/', views.CustomView.count_customers),
    path('total_users/', views.CustomView.total_users),
    path('count_products/', views.CustomView.count_products),
    path('count_suppliers/', views.CustomView.count_suppliers),
    path('count_transactions/', views.CustomView.count_transactions),
    path('', include(router.urls)),
]