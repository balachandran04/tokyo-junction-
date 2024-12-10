from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='home'), 
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('addtocart/<int:product_id>/', views.addtocart, name='add-to-cart'),
    path('category/<int:category_id>/', views.category_view, name='category_view'), 
    path('register/', views.user_registration, name='register'), 
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/', views.view_cart, name='cart'), 
    path('removefromcart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),  # New URL for removing
]

# Only serve static files if we're in development mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
