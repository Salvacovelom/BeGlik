from products.models import Category

class CategoryService:
  def delete_category( id: int ):
    """
    This method is used to delete a category
    """
    queryset = Category.objects.get(id=id)
    Category.delete(queryset)
