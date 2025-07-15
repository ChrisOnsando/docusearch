from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from .models import Document
from rest_framework.parsers import MultiPartParser
import textract
from django.db.models import Q

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

@api_view(['GET'])
def search_documents(request):
    user = getattr(request, 'user_info', None)
    if not user:
        return Response({"error": "Unauthorized"}, status=401)

    query = request.GET.get('q', '')
    if not query:
        return Response({"error": "Search query missing"}, status=400)

    docs = Document.objects.filter(
        Q(text_content__icontains=query),
        uploader_email=user['email']
    )

    results = []
    for doc in docs:
        snippet_start = doc.text_content.lower().find(query.lower())
        snippet = (
            doc.text_content[snippet_start:snippet_start+200]
            if snippet_start != -1 else ''
        )
        results.append({
            "id": doc.id,
            "title": doc.title,
            "match_snippet": snippet,
            "uploaded_at": doc.uploaded_at
        })

    return Response(results)

