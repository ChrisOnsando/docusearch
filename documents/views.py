from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def profile_view(request):
    user_info = getattr(request, 'user_info', None)
    if user_info:
        return Response({
            "message": "Authenticated",
            "uid": user_info.get("uid"),
            "email": user_info.get("email"),
        })
    return Response({"error": "Not authenticated"}, status=401)

