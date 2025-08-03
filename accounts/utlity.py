import random
from .models import User
def set_username(first_name, last_name):
    """Generate a unique username from first and last name"""
    base_username = f"{first_name.lower()}_{last_name.lower()}" if last_name else first_name.lower()
    username = base_username
    counter = 1
    
    while User.objects.filter(username=username).exists():
        username = f"{base_username}_{counter}"
        counter += 1
    
    return username