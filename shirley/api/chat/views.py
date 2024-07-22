import shirley
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import permissions
from shirley.api.chat.serializers import ChatSerializer


config = shirley.Config()

class ChatView(APIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAdminUser]

    def get(self, request: Request, format=None):
        return Response('This is 🦈 Shirley. Use POST to chat.')

    def post(self, request: Request, format=None):
        prompt = request.data['prompt']
        generator = shirley.Generator(pretrained_model_path=config.pretrained_model_path)
        generated_text = generator.generate(prompt)
        return Response(generated_text)
