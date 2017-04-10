from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.login_view, name='login_view'),
    url(r'^register$', views.register, name='register'),
    url(r'^products$', views.products, name='products'),
    url(r'^cart$', views.cart, name='cart'),
    url(r'^logout_view$', views.logout_view, name='logout_view'),
    url(r'^checkout$', views.cart, name='checkout'),
]
