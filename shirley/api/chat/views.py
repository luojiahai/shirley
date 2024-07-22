import shirley
from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import permissions
from shirley.api.chat.serializers import ChatSerializer


config = shirley.Config()

class ChatViewSet(viewsets.ViewSet):
    serializer_class = ChatSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def list(self, request: Request, format=None):
        return Response(data='This is 🦈 Shirley. Use POST to chat.', status=status.HTTP_200_OK)

    def create(self, request: Request, format=None):
        prompt = request.data['prompt']
        generator = shirley.Generator(pretrained_model_path=config.pretrained_model_path)
        generated_text = generator.generate(prompt)
        return Response(data=generated_text, status=status.HTTP_200_OK)
