from django.shortcuts import get_object_or_404, render
from . import models

def basket_middleware(get_response):
    def middleware(request):
        if "basket_id" in request.session:
            basket_id = request.session["basket_id"]
            basket = models.Basket.objects.get(id=basket_id)
            #basket = get_object_or_404(models.Basket, pk=request.GET.get("basket_id"))
            request.basket = basket
        else:
            request.basket = None

        response = get_response(request)
        return response

    return middleware
