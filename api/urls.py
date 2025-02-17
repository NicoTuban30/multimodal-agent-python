from django.urls import path
from .views import save_transcript, get_transcripts, process_chat

urlpatterns = [
    path("save_transcript/", save_transcript, name="save_transcript"),
    path("get_transcripts/", get_transcripts, name="get_transcripts"),
    path("process_chat/", process_chat, name="process_chat"),
]
