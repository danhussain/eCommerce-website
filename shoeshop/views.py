from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext, loader
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Profile, Product, Cart
from rest_framework import viewsets
from .serializers import UserSerializer, ProfileSerializer, ProductSerializer, CartSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CartViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

def login_view(request):
	context = {}

	if(request.method == 'POST'):
		u = request.POST.get('username')
		p = request.POST.get('password')

		if(u is "" or p is ""):
			context['error'] = "Error! Please enter a value in each field."
		else:
			user = authenticate(username=u, password=p)
			if user is not None:
				login(request, user)
				request.session['username'] = u
				return HttpResponseRedirect('/shoeshop/products')
			else:
				context['error'] = "Error! Invalid login."

	return render(request, "shoeshop/login_view.html", context)

def logout_view(request):
	logout(request)
	request.session.flush()
	return HttpResponseRedirect('/shoeshop')

def register(request):
	context = {}

	if(request.method == 'POST'):
		f = request.POST['fName']
		l = request.POST['lName']
		e = request.POST['email']
		u = request.POST['username']
		ph = request.POST['phone']
		a = request.POST['address']
		p = request.POST['password']
		cp = request.POST['confirmPassword']

		if(f is "" or l is "" or e is "" or u is "" or ph is "" or a is "" or p is "" or cp is ""):
			context['error'] = "Error! Please enter a value in each field."
		elif(p != cp):
			context['error'] = "Error! Passwords do not match."
		else:
			Users = User.objects.all()
			if(Users.exists()==False):
				u = User.objects.create_user(first_name=f, last_name=l, email=e, username=u, password=p)
				u.profile.phone = ph
				u.profile.address = a
				u.save()
				return HttpResponseRedirect('/shoeshop')
			else:
				try:
					u = User.objects.create_user(first_name=f, last_name=l, email=e, username=u, password=p)
					u.profile.phone = ph
					u.profile.address = a
					u.save()
					return HttpResponseRedirect('/shoeshop')
				except IntegrityError:
					context['error'] = "Error! Email address already exists."


	return render(request, 'shoeshop/register.html', context)

def products(request):
	products = Product.objects.all()
	incart = False

	if 'username' in request.session:
		username = request.session['username']
		user = User.objects.get(username=username)

		if 'add' in request.GET:
			product = request.GET['add']
			product_obj = Product.objects.get(pk=product)
			cart = Cart.objects.filter(user_id=user.id)
			if cart.filter(product_id=product).exists():
				incart = True

			if incart==False:
				cart = Cart(user_id=user.id,product_id=product,total_price=product_obj.price)
				cart.save()


	return render(request, "shoeshop/products.html", {'Products':products})

def cart(request):
	context = {}
	final_price=0

	if 'username' in request.session:
		username = request.session['username']
		user = User.objects.get(username=username)
		cart = Cart.objects.filter(user_id=user.id)
		context['Carts'] = cart
		for c in cart:
			final_price += c.total_price
		context['Final'] = final_price

		if 'remove' in request.GET:
			product = request.GET['remove']
			cart = cart.filter(product_id=product).delete()
			return render(request, "shoeshop/cart.html", context)

		if 'add' in request.GET:
			product = request.GET['add']
			cart = cart.filter(product_id=product).get()
			cart.quantity = cart.quantity+1
			cart.total_price = cart.quantity * cart.product.price
			cart.save()
			return render(request, "shoeshop/cart.html", context)

		if 'delete' in request.GET:
			product = request.GET['delete']
			cart = cart.filter(product_id=product).get()
			cart.quantity = cart.quantity-1
			if cart.quantity <= 0:
				cart.quantity = 1
			cart.total_price = cart.quantity * cart.product.price
			cart.save()
			return render(request, "shoeshop/cart.html", context)

		if 'checkout' in request.GET:
			message = ""
			if(cart.exists()==False):
				return render(request, "shoeshop/cart.html", {'error':"Error! Cart is empty."})
			else:
				for c in cart:
					message += "Product Name: " + c.product.name + "\n" + "Price: " + str(c.product.price) + "\n" + "Size: " + str(c.product.size) + "\n" + "Colour: " + c.product.colour + "\n" + "Quantity: " + str(c.quantity) + "\n" + "Total Price: " + str(c.total_price) + "\n \n"
				message += "\n Final Price: " + str(final_price)
				send_mail("Your order...", message, "shoeshopgang@gmail.com", [user.email], fail_silently=False)
				cart = cart.delete()
				return render(request, "shoeshop/checkout.html", {})

	return render(request, "shoeshop/cart.html", context)
