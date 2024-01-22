class ProductService:

  def get_last_product_image(product):
    queryset = product.images.all().order_by('-created_at').first()
    last_product_image = queryset.image.name if queryset else None
    return last_product_image
