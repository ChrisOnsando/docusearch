from django.http import JsonResponse
from firebase_auth import verify_firebase_token

class FirebaseAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            id_token = auth_header.split(" ")[1]
            user = verify_firebase_token(id_token)
            if user:
                request.user_info = user
            else:
                return JsonResponse({"error": "Invalid Firebase token"}, status=401)
        return self.get_response(request)
