import json

from django.http import HttpResponse, JsonResponse

from django.views import generic
from django.views import View

from product.models import Variant

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Q

from product.models import *


@method_decorator(csrf_exempt, name='dispatch')
class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'
    
    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        print(context)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context
    
    def post(self, request, *args, **kwargs):
        image = request.FILES['image']
        title = request.POST.get("title")
        sku = request.POST.get("sku")
        description = request.POST.get("description")
        variants = json.loads(request.POST.get("product_variant"))
        prices = json.loads(request.POST.get("product_variant_prices"))

        if Product.objects.filter(sku=sku).exists():
            print("match")
            return JsonResponse(data={'error':'This Sku is already Exist!'}, status=400)

        product_obj = Product.objects.create(
            title = title,
            sku = sku,
            description = description
        )

        if image:
            ProductImage.objects.create(
                product_id = product_obj.id,
                file_path = image
            )
        if variants:
            for item in variants:
                variant_id = item.get('option')
                tags = item.get('tags')
                for tag in tags:
                    ProductVariant.objects.create(
                        variant_title = tag,
                        variant_id = variant_id,
                        product_id = product_obj.id
                    )
        if prices:
            for price_item in prices:
                title = price_item.get('title')
                titles = title.split('/')
                for var_title in titles:
                    if titles[0] is not "":
                        product_var_id_1 = ProductVariant.objects.get(product_id=product_obj.id, variant_title=titles[0].strip()).id
                    else:
                        product_var_id_1 = None
                    if titles[1] is not "":
                        product_var_id_2 = ProductVariant.objects.get(product_id=product_obj.id, variant_title=titles[1].strip()).id
                    else:
                        product_var_id_2 = None
                    if titles[2] is not "":
                        product_var_id_3 = ProductVariant.objects.get(product_id=product_obj.id, variant_title=titles[2].strip()).id
                    else:
                        product_var_id_3 = None

                price = price_item.get('price')
                stock = price_item.get('stock')

                ProductVariantPrice.objects.create(
                    product_variant_one_id = product_var_id_1,
                    product_variant_two_id = product_var_id_2,
                    product_variant_three_id = product_var_id_3,
                    product_id = product_obj.id,
                    price = price,
                    stock = stock,

                )

        return HttpResponse(status=200)

class ProductListView(generic.ListView):
    template_name = 'products/list.html'
    model = Product
    paginate_by = 5

    def get_queryset(self, **kwargs):
        title = self.request.GET.get("title")
        price_from = self.request.GET.get("price_from")
        price_to = self.request.GET.get("price_to")
        date = self.request.GET.get("date")
        variant_id = self.request.GET.get("variant")

        # Filtering product objs
        qs = Product.objects.all()
        
        if title:
            qs = qs.filter(title__contains=title)
        if price_from and price_to:
            qs = qs.filter(productvariantprice__price__range = (price_from, price_to))
        if variant_id:
            qs = qs.filter(
                Q(productvariantprice__product_variant_one_id = variant_id)|
                Q(productvariantprice__product_variant_two_id = variant_id)|
                Q(productvariantprice__product_variant_three_id = variant_id)
            )
        if date:
            qs = qs.filter(created_at__date = date)

        return qs.distinct()

    def get_context_data(self, **kwargs):
        if 'check' in self.request.GET:
            url = "csrfmiddlewaretoken" + self.request.get_full_path().split("csrfmiddlewaretoken")[-1]
        else:
            url = ''
        context = super().get_context_data(**kwargs)
        variants = ProductVariant.objects.all()
        context['variants'] = variants
        context['url'] = url
        return context
    