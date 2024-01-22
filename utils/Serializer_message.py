from django.utils.translation import gettext as _

class SerializerMessage:
  """
  This class is used to create a generic message for the serializers
  overwriting the to_representation method
  """
  def generic_message( self, instance, resource, context):
    representation = {}
    operation = None
    if context['request'].method == 'POST': operation = 'create'
    elif context['request'].method == 'DELETE': operation = 'delete'
    elif context['request'].method == 'PUT': operation = 'update'
    elif context['request'].method == 'PATCH': operation = 'update'
    else: operation = 'read'
    representation['message'] = _("%s %s successfully") % (resource, operation)
    representation['data'] = instance
    return representation
  
  def to_representation(self, instance):
    context = self.context
    instance = super().to_representation(instance)
    resource = self.Meta.model.__name__
    return self.generic_message(instance, resource, context)