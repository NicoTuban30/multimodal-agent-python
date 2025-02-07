from __future__ import annotations

import logging
import os
import json
from dotenv import load_dotenv

from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai


load_dotenv(dotenv_path=".env")
logger = logging.getLogger("my-worker")
logger.setLevel(logging.INFO)


# Define path for storing user conversation history
USER_DATA_PATH = "user_data.json"


def load_user_data():
    if os.path.exists(USER_DATA_PATH):
        with open(USER_DATA_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.warning("File user_data.json is empty or corrupt. Resetting data.")
                return {}
    return {}


def save_user_data(user_data):
    with open(USER_DATA_PATH, 'w') as f:
        json.dump(user_data, f)


async def entrypoint(ctx: JobContext):
    try:
        logger.info(f"Connecting to room {ctx.room.name}")
        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

        participant = await ctx.wait_for_participant()

        # Wait until the participant publishes an audio track
        if not participant.get_tracks(kind=rtc.TrackKind.AUDIO):
            logger.warning(f"Participant {participant.identity} has no microphone track. Waiting for track...")
            await participant.wait_for_track(kind=rtc.TrackKind.AUDIO, timeout=10)  # Wait for up to 10 seconds

        run_multimodal_agent(ctx, participant)

        logger.info("Agent started")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


def run_multimodal_agent(ctx: JobContext, participant: rtc.RemoteParticipant):
    logger.info("Starting multimodal agent")

    user_data = load_user_data()
    user_id = participant.identity

    questions = [
        "Could you tell me your full name, including your middle name?",
        "Do you have a maiden name?",
        "Have you had any other names in the past?",
        "What is your birthdate?",
        "Where were you born? If you know, I'd love to hear which hospital too.",
        "Where did you grow up?",
        "Can you tell me your parents' full names?",
        "Where are they originally from?",
        "Where was your mother originally from?",
        "Looking back through your family tree, what's your cultural background?",
        "Do you have any siblings? If so, can you tell me their names and where they and you fall in birth order?",
        "I'd love to hear about some of your interests, hobbies, or passions. What kinds of things do you enjoy?"
    ]

    user_info = user_data.get(user_id, {'asked_questions': []})
    remaining_questions = [q for q in questions if q not in user_info['asked_questions']]

    if not remaining_questions:
        logger.info(f"User {user_id} has already answered all questions. Ending session.")
        return

    instructions = (
        "Instructions: "
        "- Start by saying greetings: Hello! I'm Narra, your AI storytelling guide. "
        "I’m here to help you craft and preserve your most treasured memories. "
        "Let’s embark on this journey together. You can skip any question you’re uncomfortable with and pause anytime you wish. Ready to begin? "
        "- Ask one question at a time and avoid introducing additional questions within the same response. "
        f"{' '.join(remaining_questions)}"
    )

    model = openai.realtime.RealtimeModel(
        instructions=instructions,
        modalities=["audio", "text"],
    )

    chat_ctx = llm.ChatContext()
    chat_ctx.append(
        text="You are Narra, a friendly and approachable storytelling guide. "
             "Your purpose is to assist users in capturing and sharing the most meaningful aspects of their life stories.",
        role="assistant",
    )

    agent = MultimodalAgent(
        model=model,
        chat_ctx=chat_ctx,
    )
    agent.start(ctx.room, participant)

    # Wait for user input before generating a reply
    async def wait_for_audio_input():
        try:
            logger.info(f"Waiting for participant {participant.identity} to speak...")
            transcript = await participant.wait_for_transcription()
            logger.info(f"Received transcript: {transcript}")
            agent.generate_reply()
        except Exception as e:
            logger.error(f"Error waiting for user input: {e}")

    ctx.loop.create_task(wait_for_audio_input())

    save_user_data(user_data)


def process_transcript(text):
    """
    Process the transcript text using OpenAI and return a response.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an AI assistant."},
                      {"role": "user", "content": text}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error processing transcript: {str(e)}"


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
