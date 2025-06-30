from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from .models import Document
from rest_framework.parsers import MultiPartParser
import textract

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

@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_document(request):
    user = getattr(request, 'user_info', None)
    if not user:
        return Response({"error": "Unauthorized"}, status=401)

    uploaded_file = request.FILES.get('file')
    title = request.data.get('title')

    if not uploaded_file:
        return Response({"error": "No file provided"}, status=400)

    temp_path = f'/tmp/{uploaded_file.name}'
    with open(temp_path, 'wb+') as temp_file:
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)

    try:
        extracted_text = textract.process(temp_path).decode('utf-8')
    except Exception as e:
        extracted_text = "Could not extract text"

    doc = Document.objects.create(
        title=title or uploaded_file.name,
        file=uploaded_file,
        text_content=extracted_text,
        uploader_email=user['email']
    )

    return Response({"message": "Document Uploaded!", "doc_id": doc.id})
