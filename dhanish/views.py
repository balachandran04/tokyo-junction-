from django.shortcuts import render, get_object_or_404,redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import Product

def home(request):
    return render(request,'index.html')

def addtocart(request):
    return render(request, 'addtocart.html')

# views.py
from django.shortcuts import render
from .models import Product, Category

def category_view(request, category_id):
   
    category = Category.objects.get(id=category_id)
    
    products = Product.objects.filter(categories=category)
    return render(request, 'index.html', {'products': products, 'selected_category': category})

def product_list(request):

    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})

def product_detail(request, id):

    product = get_object_or_404(Product, id=id)
    return render(request, 'product_detail.html', {'product': product})



def user_registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful!")
            return redirect('home')  
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})
# views.py
from django.shortcuts import redirect, get_object_or_404
from .models import Product

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    # Convert Decimal price to float before storing in session
    request.session['product_id'] = product.id
    request.session['product_name'] = product.name
    request.session['product_price'] = float(product.price)  
    
    return redirect('checkout')  

def checkout(request):
    # Retrieve product data from session
    product_id = request.session.get('product_id')
    product_name = request.session.get('product_name')
    product_price = request.session.get('product_price')  # This will be a float

    # Fetch the full product data if available
    product = get_object_or_404(Product, pk=product_id) if product_id else None

    return render(request, 'checkout.html', {
        'product': product,
        'product_name': product_name,
        'product_price': product_price
    })
from django.http import JsonResponse
def addtocart(request, product_id):
    product = Product.objects.get(id=product_id)  # Get the product from the database
    
    # Use session-based cart if you don't want to use a database-based cart
    cart = request.session.get('cart', {})

    if product_id in cart:
        cart[product_id] += 1  # If product is already in cart, increase quantity
    else:
        cart[product_id] = 1  # Add the product with quantity 1 if it's not in the cart

    request.session['cart'] = cart  # Save cart to session
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cart_size': len(cart)})
    
    return redirect('cart')  




def view_cart(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    total_price = 0

    for product in products:
        quantity = cart.get(str(product.id), 0)
        total_item_price = product.price * quantity
        total_price += total_item_price
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': total_item_price,
        })

    return render(request, 'view_cart.html', {'cart_items': cart_items, 'cart_total': total_price})

def remove_from_cart(request, product_id):
    # Get the cart from the session
    cart = request.session.get('cart', {})

    if product_id in cart:
        del cart[product_id]  


    request.session['cart'] = cart

    return redirect('home')