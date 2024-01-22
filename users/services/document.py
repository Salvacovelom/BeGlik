from users.models import UserDocument 

class DocumentService:
  def get_last_user_doc( user, document_type ):
    last_user_doc = UserDocument.undeleted_objects.filter(user=user).order_by('-created_at') .first()
    return last_user_doc if last_user_doc else None
  
  def get_internal_name( user_id, document_type ):
    last_user_doc = DocumentService.get_last_user_doc( user_id, document_type )    
    last_user_doc_number = int(last_user_doc.document.name.split('_')[-1]) if last_user_doc else 0    
    return str(user_id) + "_" + document_type + "_" + str(last_user_doc_number + 1)