from rest_framework.response import Response 
from rest_framework.decorators import api_view
from db.models import Session, Streamer, Message
from .serializers import SessionSerializer, StreamerSerializer, MessageSerializer

@api_view(['GET'])
def dropdownMenuData(request):
    sessions = Session.objects.all()
    serializer = SessionSerializer(sessions, many=True)
    return Response(serializer.data)