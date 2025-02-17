import json
import logging
import sys
import os

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from agent.agent import process_transcript  # Importing from the root directory
from .serializers import TranscriptSerializer  # Importing the TranscriptSerializer
from .models import Transcript  # Importing the Transcript model

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

logger = logging.getLogger(__name__)


@api_view(["POST"])
def save_transcript(request):
    """
    Save a transcript entry to the database.
    """
    try:
        # Extract the data from the request
        data = request.data
        
        # Ensure the necessary fields are present
        user = data.get("user")
        message = data.get("message")
        timestamp = data.get("timestamp")
        
        if not user or not message or not timestamp:
            return Response({"status": "error", "message": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new Transcript instance and save it
        transcript = Transcript(user=user, message=message, timestamp=timestamp)
        transcript.save()

        # Optionally log this for debugging purposes
        logger.info(f"Transcript saved: {transcript}")

        return Response({"status": "success", "message": "Transcript saved"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        # Log any errors that occur
        logger.error(f"Error saving transcript: {e}")
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
def get_transcripts(request):
    """
    Retrieve all saved transcripts ordered by timestamp.
    """
    transcripts = Transcript.objects.all().order_by("-timestamp")
    serializer = TranscriptSerializer(transcripts, many=True)
    return Response(serializer.data)


@csrf_exempt
def process_chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            text = data.get("message", "")

            if not text:
                return JsonResponse({"error": "No message provided"}, status=400)

            response = process_transcript(text)  # Call agent function
            return JsonResponse({"response": response})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Only POST method allowed"}, status=405)
