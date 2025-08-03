# In middleware.py
class AuthenticationDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        print(f"Auth Header: {auth_header}")
        
        response = self.get_response(request)
        
        if response.status_code == 401:
            print(f"Failed auth attempt for {request.path}")
            
        return response