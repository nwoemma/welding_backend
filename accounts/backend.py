from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


UserModel = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        
        try:
            # Case-insensitive email match
            user = UserModel.objects.get(Q(email__iexact=email))
            
            # Check password and user status
            if user.check_password(password):
                if self.user_can_authenticate(user):
                    return user
                print("DEBUG: User cannot authenticate (inactive or invalid status)")
            else:
                print("DEBUG: Password did not match")
        except UserModel.DoesNotExist:
            print("DEBUG: User not found")
            return None
        except Exception as e:
            print(f"DEBUG: Authentication error: {str(e)}")
        return None