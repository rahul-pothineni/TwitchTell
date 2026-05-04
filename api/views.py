from rest_framework.response import Response 
from rest_framework.decorators import api_view
from db.models import Session, Streamer, Message
from .serializers import SessionSerializer, StreamerSerializer, MessageSerializer

#get all sessions for the drop down menu
@api_view(['GET'])
def sessionData(request):
    sessions = Session.objects.all()
    serializer = SessionSerializer(sessions, many=True)
    return Response(serializer.data)

#get the streamers accosiated with the session passed in url
@api_view(['GET'])
def streamerData(request, curSessionId):
    curSession = Session.objects.get(id = curSessionId)
    streamers = Streamer.objects.filter(session=curSession)
    serializer = StreamerSerializer(streamers, many=True)
    return Response(serializer.data)

#get the messages accosiated with the session and streamer name passed in url
@api_view(['GET'])
def messageData(request, curSessionId, curStreamerName):
    curSession = Session.objects.get(id = curSessionId)
    streamer = Streamer.objects.get(session=curSession, username=curStreamerName)
    messages = Message.objects.filter(streamer=streamer)
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)