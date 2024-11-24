from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from .models import Product, Cart, CartItem, Order, Address, Wishlist, WishlistItem,OrderItem
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.utils import timezone
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import logging

# User Registration
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# User Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse('Invalid credentials')
    return render(request, 'login.html')

# User Logout (Built-in Django logout)
from django.contrib.auth import logout

def user_logout(request):
    logout(request)
    return redirect('home')



def home(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user)
    else:
        orders = []  

    products = Product.objects.all()
    return render(request, 'index.html', {'products': products, 'orders': orders})

# views.py

from django.shortcuts import render, get_object_or_404
from .models import Product

def product_details(request, id):
    # Get the product with the given id, or return a 404 error if not found
    product = get_object_or_404(Product, id=id)
    
    # Pass the product object to the template
    return render(request, 'product_details.html', {'product': product})

# Add product to cart
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem,Size


from .forms import ProductForm
from django.contrib import messages

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # Get the selected size
        size_id = request.POST.get('size')
        size = get_object_or_404(Size, id=size_id)

        # Check if the selected size is in stock
        if size in product.sizes.all():  # Make sure the size is available for this product
            if product.is_in_stock():
                # Reduce stock and proceed with adding to cart (you can handle cart logic here)
                quantity = 1  # For simplicity, assuming the user selects 1 quantity
                product.reduce_stock(quantity)
                
                # Here you can add the product to the user's cart (model logic for cart needed)
                # Example: Cart.add_product(product, size, quantity)
                messages.success(request, f"{product.name} in size {size.name} has been added to your cart!")
                return redirect('cart')  # Redirect to the cart or another page after adding to the cart
            else:
                messages.error(request, 'Sorry, this product is out of stock.')
        else:
            messages.error(request, f"Sorry, size {size.name} is not available for this product.")
    
    form = ProductForm()
    return render(request, 'product_details.html', {'product': product, 'form': form})
# View cart
@login_required
def view_cart(request):
    # Retrieve the user's cart
    cart = get_object_or_404(Cart, user=request.user)
    
    # Get all items in the user's cart
    items = CartItem.objects.filter(cart=cart)
    
    # Calculate the total price of the cart
    total_price = sum(item.product.price * item.quantity for item in items)
    
    # Return the rendered template with cart items and total price
    return render(request, 'cart.html', {'items': items, 'cart': cart, 'total_price': total_price})
@login_required
def remove_from_cart(request, cart_item_id):
    try:
        cart_item = CartItem.objects.get(id=cart_item_id)
        cart_item.delete()
        messages.success(request, f"{cart_item.product.name} has been removed from your cart.")
    except CartItem.DoesNotExist:
        messages.error(request, "The item could not be found in your cart.")

    return redirect('cart')

# Checkout view
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Address, Cart, CartItem, Order, OrderItem

@login_required
def checkout(request):
    if request.method == 'POST':
      
        if request.user.is_authenticated:
            address_id = request.POST.get('address_id')
            address = Address.objects.get(id=address_id, user=request.user)
        
        
        else:
            street_address = request.POST.get('street_address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            postal_code = request.POST.get('postal_code')
            phone = request.POST.get('phone')

            # Create a new address for the guest
            address = Address.objects.create(
                user=None,  # Guest user
                street_address=street_address,
                city=city,
                state=state,
                postal_code=postal_code,
                phone=phone
            )

        # Get cart items for the user (whether logged in or not)
        cart = Cart.objects.get(user=request.user) if request.user.is_authenticated else None
        cart_items = CartItem.objects.filter(cart=cart)

        # Calculate total price
        total_price = sum(item.total_price() for item in cart_items)

        # Create the order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            shipping_address=address,
            total_price=total_price,
            payment_method='COD',
            order_date=timezone.now()
        )

        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price_at_time_of_order=cart_item.product.price
            )
            # Reduce product stock
            cart_item.product.reduce_stock(cart_item.quantity)

        # Clear cart after the order is placed
        if cart:
            cart.items.all().delete()

        return redirect('order_summary', order_id=order.id)

    # For logged-in users, fetch their saved addresses
    if request.user.is_authenticated:
        addresses = request.user.addresses.all()
    else:
        addresses = []

    return render(request, 'checkout.html', {'addresses': addresses})

# Order summary view
@login_required
def order_summary(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, 'order_summary.html', {'order': order})

# Add product to wishlist
@login_required
def add_to_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)

    return redirect('wishlist')

# View wishlist
@login_required
def view_wishlist(request):
    wishlist = Wishlist.objects.get(user=request.user)
    items = WishlistItem.objects.filter(wishlist=wishlist)
    return render(request, 'wishlist.html', {'items': items})

# Remove item from wishlist
@login_required
def remove_from_wishlist(request, wishlist_item_id):
    wishlist_item = WishlistItem.objects.get(id=wishlist_item_id)
    wishlist_item.delete()
    return redirect('wishlist')


@login_required
def add_address(request):
    if request.method == 'POST':
        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        phone_number = request.POST.get('phone_number')

        Address.objects.create(
            user=request.user,
            street_address=street_address,
            city=city,
            postal_code=postal_code,
            country=country,
            phone_number=phone_number
        )
        return redirect('checkout')

    return render(request, 'add_address.html')
@login_required

@login_required
def order_status(request, order_id):
    # Get the order by ID, ensuring it belongs to the logged-in user
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Render the order status template
    return render(request, 'order_status.html', {'order': order})

logger = logging.getLogger(__name__)
def send_order_email(order_details):
    try:
        print("hi")
        # Prepare email
        order_date = order_details.get('order_date')
        products = order_details.get('products')

        subject = 'New Order Received'
        recipient = 'balachantran8@gmail.com'
        message = render_to_string('order_email.html', {
            'order_date': order_date,
            'products': products,
        })

        # Send email
        email = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [recipient]
        )
        email.content_subtype = "html"  # Send as HTML
        email.send()
        logger.info("Email sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

from django.core.mail import send_mail

def test_email():
    send_mail(
        'Test Email',
        'This is a test email.',
        settings.EMAIL_HOST_USER,
        ['balachantran8@gmail.com'],
        fail_silently=False,
    )




def place_order(request):
    # Example order details
    order_details = {
        'order_date': '2024-11-22',
        'products': [
            {
                'image_url': 'https://fastly.picsum.photos/id/13/2500/1667.jpg?hmac=SoX9UoHhN8HyklRA4A3vcCWJMVtiBXUg0W4ljWTor7s',
                'name': 'Product 1',
                'price': 19.99
            },
            {
                'image_url': 'https://fastly.picsum.photos/id/9/5000/3269.jpg?hmac=cZKbaLeduq7rNB8X-bigYO8bvPIWtT-mh8GRXtU3vPc',
                'name': 'Product 2',
                'price': 29.99
            }
        ]
    }
    send_order_email(order_details)
    return HttpResponse('Order placed successfully!')