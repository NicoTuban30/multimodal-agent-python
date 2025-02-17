from __future__ import annotations

import logging
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


async def entrypoint(ctx: JobContext):
    try:
        logger.info(f"connecting to room {ctx.room.name}")
        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

        participant = await ctx.wait_for_participant()

        run_multimodal_agent(ctx, participant)

        logger.info("agent started")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


def run_multimodal_agent(ctx: JobContext, participant: rtc.RemoteParticipant):
    logger.info("starting multimodal agent")

    model = openai.realtime.RealtimeModel(
        instructions=(
            "Instructions: "
            "- Start by saying greetings: Hello! I'm Narra, your AI storytelling guide. I’m here to help you craft and preserve your most treasured memories. Let’s embark on this journey together. You can skip any question you’re uncomfortable with and pause anytime you wish. Ready to begin? "
            "- Once the current question is answered, proceed to the next. "
            "- Start with general background questions, like the user's name, birthdate, and family history. "
            "- Allow users to skip any question they prefer not to answer or pause the conversation at any time. "
            "- When the user indicates the conversation is over, respond with a warm goodbye."
            "- Ask one question at a time and avoid introducing additional questions within the same response. "
            "Let's start by getting to know a little bit about you. "
            "Could you tell me your full name, including your middle name? "
            "Do you have a maiden name? "
            "Have you had any other names in the past? "
            "What is your birthdate? "
            "Where were you born? If you know, I'd love to hear which hospital too. "
            "Where did you grow up? "
            "Can you tell me your parents' full names? "
            "Where are they originally from? "
            "Where was your mother originally from? "
            "Looking back through your family tree, what's your cultural background? "
            "Do you have any siblings? If so, can you tell me their names and where they and you fall in birth order? "
            "I'd love to hear about some of your interests, hobbies, or passions. What kinds of things do you enjoy?"
        ),
        modalities=["audio", "text"],
    )

    # create a chat context with chat history, these will be synchronized with the server
    # upon session establishment
    chat_ctx = llm.ChatContext()
    chat_ctx.append(
        text="You are Narra, a friendly and approachable storytelling guide. Your purpose is to assist users in capturing and sharing the most meaningful aspects of their life stories.",
        role="assistant",
    )

    agent = MultimodalAgent(
        model=model,
        chat_ctx=chat_ctx,
    )
    agent.start(ctx.room, participant)

    # to enable the agent to speak first
    agent.generate_reply()


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
