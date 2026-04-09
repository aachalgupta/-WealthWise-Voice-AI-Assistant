"""
agent.py
WealthWise Advisory - Agentic Voice AI Assistant
"""

import os
import json
import asyncio
import logging
from typing import TypedDict, Optional, Annotated
import operator

from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from langchain_core.tools import tool

from typing import AsyncIterable
from livekit.agents.voice import ModelSettings
from livekit.agents import llm as agents_llm  
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import deepgram, silero, openai as lk_openai
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from calendar_utils import get_available_slots, book_appointment
import yaml

with open("prompts.yaml", "r") as f:
    PROMPTS = yaml.safe_load(f)

load_dotenv()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ── Config ───────────────────────────────────────────────
QDRANT_URL         = os.getenv("QDRANT_URL")
QDRANT_API_KEY     = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY     = os.getenv("OPENAI_API_KEY")
DEEPGRAM_API_KEY   = os.getenv("DEEPGRAM_API_KEY")

COLLECTION_NAME  = "wealthwise_faqs"
EMBEDDING_MODEL  = "text-embedding-3-small"
LLM_MODEL        = "gpt-4o"
CLASSIFIER_MODEL = "gpt-4o-mini" 
TOP_K            = 3
MAX_FAILURES     = 2

# ── Clients ──────────────────────────────────────────────
openai_client = OpenAI(api_key=OPENAI_API_KEY)
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# ── Intent Categories ────────────────────────────────────
INTENT_CATEGORIES = [
    "company_info",     # what is WealthWise, services, fees, location
    "book_appointment", # user wants to book / schedule a call
    "check_slots",      # user wants to know available times
    "complaint",        # user is frustrated or complaining
    "greeting",         # hi, hello, good morning
    "goodbye",          # bye, thank you, that's all
    "off_topic",        # unrelated to finance or company
]


# ════════════════════════════════════════════════════════
# TOOL 1 — SEARCH KNOWLEDGE BASE (Qdrant RAG)
# GPT-4o calls this to answer company and financial queries
# ════════════════════════════════════════════════════════
@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the WealthWise Advisory knowledge base for answers to
    company information, services, fees, financial planning, mutual funds,
    tax planning, insurance, and investment queries.
    Use this tool whenever the user asks any question about WealthWise or finances.
    """
    log.info(f"[Tool: search_knowledge_base] Query: {query}")

    embedding_response = openai_client.embeddings.create(
        input=query,
        model=EMBEDDING_MODEL
    )
    query_vector = embedding_response.data[0].embedding

    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=TOP_K,
    ).points

    if not results:
        return "No relevant information found in the knowledge base."

    context = "\n\n".join(
        [f"Q: {r.payload['question']}\nA: {r.payload['answer']}" for r in results]
    )
    log.info(f"[Tool: search_knowledge_base] Found {len(results)} results")
    return context


# ════════════════════════════════════════════════════════
# TOOL 2 — CHECK AVAILABLE SLOTS (Google Calendar)
# GPT-4o calls this when user asks for available times
# ════════════════════════════════════════════════════════
@tool
def check_available_slots(preferred_day: str = "any") -> str:
    """
    Fetch available appointment slots from WealthWise's Google Calendar.
    preferred_day options:
      - "any"       : next available slots across today and tomorrow
      - "today"     : only today's slots
      - "tomorrow"  : only tomorrow's slots
    Use "tomorrow" if the user says they are busy today or prefers tomorrow.
    We only take appointments for today and tomorrow — nothing beyond that.
    """
    log.info(f"[Tool: check_available_slots] preferred_day={preferred_day}")
    try:
        slots = get_available_slots(num_slots=3, day_filter=preferred_day)
        
        if not slots:
            if preferred_day == "today":
                return "No slots available today. Tomorrow's slots may be available — would you like to check?"
            elif preferred_day == "tomorrow":
                return "No slots available tomorrow either. Our calendar is fully booked for today and tomorrow. Please try again tomorrow morning when new slots open up, or call 1800-XXX-XXXX for urgent queries."
            else:
                return "No slots available today or tomorrow. Our calendar is fully booked. Please try again tomorrow morning when new slots open up, or call 1800-XXX-XXXX for urgent queries."

        slot_list = "\n".join([f"Slot {i+1}: {s['display']}" for i, s in enumerate(slots)])
        check_available_slots._cached_slots = slots
        return f"Available appointment slots:\n{slot_list}"
    except Exception as e:
        log.error(f"[Tool: check_available_slots] Error: {e}")
        return "Unable to fetch slots right now. Please call our helpline at 1800-XXX-XXXX."

check_available_slots._cached_slots = []


# ════════════════════════════════════════════════════════
# TOOL 3 — BOOK APPOINTMENT (Google Calendar)
# GPT-4o calls this after collecting user details
# ════════════════════════════════════════════════════════
@tool
def book_appointment_tool(
    name:          str,
    email:         str,
    phone:         str,
    slot_number:   int,
) -> str:
    """
    Book an appointment for the user on WealthWise's Google Calendar.
    Use this tool ONLY after you have collected:
    1. User's full name
    2. User's email address
    3. User's phone number
    4. Which slot number they chose (1, 2, or 3) from check_available_slots

    This will create a calendar event and send an email invite to the user.
    """
    log.info(f"[Tool: book_appointment_tool] Booking for {name} | {email} | {phone} | Slot {slot_number}")

    try:
        slots = check_available_slots._cached_slots
        if not slots:
            slots = get_available_slots(num_slots=3)
            check_available_slots._cached_slots = slots

        if slot_number < 1 or slot_number > len(slots):
            return f"Invalid slot number. Please choose between 1 and {len(slots)}."

        chosen_slot = slots[slot_number - 1]

        confirmation = book_appointment(
            name=name,
            email=email,
            phone=phone,
            slot_start=chosen_slot["start_iso"],
            slot_end=chosen_slot["end_iso"],
            slot_display=chosen_slot["display"],
        )

        log.info(f"[Tool: book_appointment_tool] Booked successfully: {confirmation}")
        return (
            f"Appointment booked successfully!\n"
            f"Client: {confirmation['name']}\n"
            f"Time: {confirmation['slot_display']}\n"
            f"Email invite sent to: {confirmation['email']}\n"
            f"Google Meet link: {confirmation.get('meet_link', 'Will be shared via email')}"
        )
    except Exception as e:
        log.error(f"[Tool: book_appointment_tool] Error: {e}")
        return "I was unable to book the appointment due to a technical issue. Please call our helpline at 1800-XXX-XXXX."


# ── Register all tools ───────────────────────────────────
TOOLS = [search_knowledge_base, check_available_slots, book_appointment_tool]


# ════════════════════════════════════════════════════════
# AGENT STATE
# ════════════════════════════════════════════════════════
class VoiceAgentState(TypedDict):
    transcript:           Optional[str]
    intent:               Optional[str]
    is_safe:              bool
    sentiment:            Optional[str]
    final_answer:         Optional[str]
    conversation_history: list[dict]
    failed_attempts:      int
    should_end:           bool
    should_continue:      bool
    escalated:            bool
    # Booking state — persists across turns
    booking_name:         Optional[str]
    booking_email:        Optional[str]
    booking_phone:        Optional[str]
    booking_in_progress:  bool


# ── Helper: GPT-4o classifier ────────────────────────────
def classify(system_prompt: str, user_content: str) -> str:
    res = openai_client.chat.completions.create(
        model=CLASSIFIER_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_content},
        ],
        temperature=0,
        max_tokens=20,
    )
    return res.choices[0].message.content.strip().lower()


# ════════════════════════════════════════════════════════
# NODE 1 — GUARDRAIL
# Blocks harmful, abusive, or completely irrelevant input
# ════════════════════════════════════════════════════════
def guardrail_node(state: VoiceAgentState) -> VoiceAgentState:
    transcript = state.get("transcript", "")
    log.info(f"[guardrail_node] Checking: {transcript}")
    print(f"ACTIVATED: guardrail_node")

    result = classify(PROMPTS["guardrail"], transcript)

    if "unsafe" in result:
        log.info("[guardrail_node] UNSAFE — blocking")
        return {
            **state,
            "is_safe":        False,
            "final_answer":   "I'm sorry, I'm not able to help with that. I'm here to assist you with financial advisory services and appointment booking only.",
            "should_continue": False,
            "should_end":     False,
        }

    return {**state, "is_safe": True}


# ════════════════════════════════════════════════════════
# NODE 2 — SENTIMENT DETECTION
# Detects user mood and adjusts response tone
# ════════════════════════════════════════════════════════
def sentiment_node(state: VoiceAgentState) -> VoiceAgentState:
    transcript = state.get("transcript", "")
    history    = state.get("conversation_history", [])
    context    = "\n".join([f"{m['role']}: {m['content']}" for m in history[-4:]])

    sentiment = classify(PROMPTS["sentiment"], f"History:\n{context}\n\nLatest: {transcript}")

    if sentiment not in ["positive", "neutral", "frustrated"]:
        sentiment = "neutral"

    log.info(f"[sentiment_node] Sentiment: {sentiment}")
    print(f"ACTIVATED: sentiment_node -> {sentiment}")
    return {**state, "sentiment": sentiment}


# ════════════════════════════════════════════════════════
# NODE 3 — INTENT DETECTION
# Classifies and routes the query
# ════════════════════════════════════════════════════════
def intent_node(state: VoiceAgentState) -> VoiceAgentState:
    transcript = state.get("transcript", "")

    # ── TEMP DEBUG
    # print(f"DEBUG intent_node | booking_in_progress = {state.get('booking_in_progress')}")
    # print(f"DEBUG intent_node | booking_name = {state.get('booking_name')}")
    # print(f"DEBUG intent_node | booking_email = {state.get('booking_email')}")
    # print(f"DEBUG intent_node | booking_phone = {state.get('booking_phone')}")
    # print(f"DEBUG intent_node | full state keys = {list(state.keys())}")

    # ── Skip classifier if booking is already underway ──
    if state.get("booking_in_progress"):
        log.info("[intent_node] Booking in progress — skipping classifier")
        print("ACTIVATED: intent_node -> book_appointment (in progress)")
        return {**state, "intent": "book_appointment"}

    log.info(f"[intent_node] Classifying: {transcript}")

    intent = classify(
        PROMPTS["intent"].format(intent_categories=", ".join(INTENT_CATEGORIES)),
        transcript
    )

    if intent not in INTENT_CATEGORIES:
        intent = "off_topic"

    log.info(f"[intent_node] Intent: {intent}")
    print(f"ACTIVATED: intent_node -> {intent}")

    if intent == "goodbye":
        return {
            **state, "intent": intent,
            "final_answer":   "Thank you for calling WealthWise Advisory. It was a pleasure speaking with you. Have a wonderful day and we hope to speak with you soon!",
            "should_end":     True,
            "should_continue": False,
        }

    if intent == "greeting":
        return {
            **state, "intent": intent,
            "final_answer":   "Hello and welcome to WealthWise Advisory! I can help you learn about our financial services or book an appointment with one of our expert advisors. How can I assist you today?",
            "should_continue": False,
            "should_end":     False,
        }

    if intent == "off_topic":
        return {
            **state, "intent": intent,
            "final_answer":   "I can only assist with financial advisory queries and appointment booking. Could you please ask me something related to our services or your financial goals?",
            "should_continue": False,
            "should_end":     False,
        }
    
    if intent == "book_appointment":
        return {**state, "intent": intent, "booking_in_progress": True}

    return {**state, "intent": intent}


# ════════════════════════════════════════════════════════
# NODE 4 — ANSWER GENERATION (with Tool Calling)
# GPT-4o decides which tool to call based on intent
# ════════════════════════════════════════════════════════
def answer_node(state: VoiceAgentState) -> VoiceAgentState:
    if state.get("final_answer"):
        return {**state, "should_continue": False}

    transcript = state.get("transcript", "")
    print(f"ACTIVATED: answer_node")
    history    = state.get("conversation_history", [])
    sentiment  = state.get("sentiment", "neutral")
    intent     = state.get("intent", "")

    tone = {
        "frustrated": "The user seems frustrated. Be extra empathetic, patient and apologetic.",
        "positive":   "The user is in a good mood. Be warm and enthusiastic.",
        "neutral":    "Use a calm, professional and helpful tone.",
    }.get(sentiment, "Use a calm professional tone.")

    system_prompt = PROMPTS["answer"].format(
    tone=tone,
    intent=intent,
    booking_name=state.get("booking_name", "not yet collected"),
    booking_email=state.get("booking_email", "not yet collected"),
    booking_phone=state.get("booking_phone", "not yet collected"),
    )

    # Build messages with full conversation history
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-8:]:
        content = msg["content"]
        if isinstance(content, list):
            content = " ".join([c if isinstance(c, str) else c.get("text", "") for c in content])
        messages.append({"role": msg["role"], "content": str(content)})
    messages.append({"role": "user", "content": str(transcript)})

    # GPT-4o with tool calling
    tool_schemas = [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.args_schema.schema() if hasattr(t, 'args_schema') and t.args_schema else {"type": "object", "properties": {}},
            }
        }
        for t in TOOLS
    ]

    response = openai_client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=tool_schemas,
        tool_choice="auto",
        temperature=0.3,
        max_tokens=150,
    )

    response_message = response.choices[0].message

    # Handle tool calls
    if response_message.tool_calls:
        messages.append(response_message)

        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            print(f"TOOL CALL: {tool_name} with args: {tool_args}")
            log.info(f"[answer_node] GPT-4o calling tool: {tool_name} with args: {tool_args}")

            # Execute the tool
            tool_result = ""
            if tool_name == "search_knowledge_base":
                tool_result = search_knowledge_base.invoke(tool_args)
            elif tool_name == "check_available_slots":
                tool_result = check_available_slots.invoke({})
            elif tool_name == "book_appointment_tool":
                tool_result = book_appointment_tool.invoke(tool_args)

            log.info(f"[answer_node] Tool result: {tool_result[:200]}")
            print(f"TOOL RESULT: {tool_result[:100]}...")

            messages.append({
                "role":         "tool",
                "tool_call_id": tool_call.id,
                "content":      str(tool_result),
            })

        # Get final answer after tool execution
        final_response = openai_client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=150,
        )
        answer = final_response.choices[0].message.content.strip()
    else:
        answer = response_message.content.strip() if response_message.content else ""

    log.info(f"[answer_node] Final answer: {answer}")

    # ── Extract and persist booking details from conversation ──
    if state.get("booking_in_progress"):
        extraction_response = openai_client.chat.completions.create(
            model=CLASSIFIER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """Extract booking details from the conversation history.
    Return ONLY a JSON object with these exact keys:
    {
    "name": "full name or null",
    "email": "email address or null", 
    "phone": "phone number or null",
    "slot_number": 1 or 2 or 3 or null
    }
    Return null for any detail not yet clearly provided by the user.
    Return ONLY the JSON, no other text."""
                },
                {
                    "role": "user",
                    "content": str(messages)
                }
            ],
            temperature=0,
            max_tokens=100,
        )
        try:
            extracted = json.loads(extraction_response.choices[0].message.content.strip())
            if extracted.get("name"):
                state = {**state, "booking_name": extracted["name"]}
            if extracted.get("email"):
                state = {**state, "booking_email": extracted["email"]}
            if extracted.get("phone"):
                state = {**state, "booking_phone": extracted["phone"]}
            log.info(f"[answer_node] Extracted booking details: {extracted}")
            print(f"EXTRACTED: {extracted}")
        except Exception as e:
            log.warning(f"[answer_node] Could not extract booking details: {e}")
    # ── End extraction ──

    # Only complaints and booking technical failures should escalate
    failed_attempts = state.get("failed_attempts", 0)

    failure_phrases = [
        "don't have that information",
        "don't have information",
        "couldn't find",
        "could not find",
        "not able to find",
        "no information",
        "i'm not sure",
        "i am not sure",
        "unable to find",
        "not in our knowledge",
        "outside my knowledge",
        "i don't have details",
        "i do not have details",
    ]

    is_failure = (
        not answer or
        any(phrase in answer.lower() for phrase in failure_phrases)
    )

    ESCALATABLE_INTENTS = ["complaint"]

    booking_failed = (
        state.get("intent") in ["book_appointment", "check_slots"] and (
            "technical issue" in answer.lower() or
            "unable to book" in answer.lower() or
            "unable to fetch" in answer.lower()
        )
    )

    if (is_failure and state.get("intent") in ESCALATABLE_INTENTS) or booking_failed:
        failed_attempts += 1
    elif not is_failure:
        failed_attempts = 0

    updated_history = history + [
        {"role": "user",      "content": transcript},
        {"role": "assistant", "content": answer},
    ]

    return {
        **state,
        "final_answer":         answer,
        "failed_attempts":      failed_attempts,
        "conversation_history": updated_history,
        "should_continue":      False,
        "booking_name":         state.get("booking_name"),
        "booking_email":        state.get("booking_email"),
        "booking_phone":        state.get("booking_phone"),
    }


# ════════════════════════════════════════════════════════
# NODE 5 — ESCALATION
# Auto-escalates to human advisor after MAX_FAILURES
# ════════════════════════════════════════════════════════
def escalation_node(state: VoiceAgentState) -> VoiceAgentState:
    failed_attempts = state.get("failed_attempts", 0)
    print(f"ACTIVATED: escalation_node")

    if failed_attempts >= MAX_FAILURES:
        log.info(f"[escalation_node] Escalating after {failed_attempts} failures")
        return {
            **state,
            "final_answer": "I've been unable to find the information you need. Let me connect you with one of our human financial advisors who can assist you better. Please hold on and someone will be with you shortly.",
            "escalated":    True,
            "should_end":   True,
        }

    return {**state, "escalated": False}


# ════════════════════════════════════════════════════════
# ROUTING
# ════════════════════════════════════════════════════════
def after_guardrail(state: VoiceAgentState) -> str:
    next_node = "escalation" if not state.get("is_safe", True) else "sentiment"
    print(f"ROUTING: guardrail -> {next_node}")
    return next_node

def after_intent(state: VoiceAgentState) -> str:
    next_node = "escalation" if state.get("final_answer") else "answer"
    print(f"ROUTING: intent -> {next_node}")
    return next_node

def after_answer(state: VoiceAgentState) -> str:
    return "escalation"

def after_escalation(state: VoiceAgentState) -> str:
    return END


# ════════════════════════════════════════════════════════
# BUILD LANGGRAPH
# ════════════════════════════════════════════════════════
def build_agent_graph():
    graph = StateGraph(VoiceAgentState)

    graph.add_node("guardrail",  guardrail_node)
    graph.add_node("sentiment",  sentiment_node)
    graph.add_node("intent",     intent_node)
    graph.add_node("answer",     answer_node)
    graph.add_node("escalation", escalation_node)

    graph.add_edge(START, "guardrail")
    graph.add_conditional_edges("guardrail",  after_guardrail)
    graph.add_edge("sentiment", "intent")
    graph.add_conditional_edges("intent",     after_intent)
    graph.add_edge("answer",    "escalation")
    graph.add_conditional_edges("escalation", after_escalation)

    return graph.compile()


agent_graph = build_agent_graph()


# ════════════════════════════════════════════════════════
# PROCESS ONE TURN
# ════════════════════════════════════════════════════════
async def process_turn(
    transcript:      str,
    history:         list[dict],
    failed_attempts: int,
    booking_name:    Optional[str] = None,
    booking_email:   Optional[str] = None,
    booking_phone:   Optional[str] = None,
    booking_in_progress: bool = False,   
) -> tuple[str, list[dict], int, bool, bool, Optional[str], Optional[str], Optional[str]]:

    print(f"\nNEW TURN: {transcript[:50]}...")
    init_state: VoiceAgentState = {
        "transcript":           transcript,
        "intent":               None,
        "is_safe":              True,
        "sentiment":            "neutral",
        "final_answer":         None,
        "conversation_history": history,
        "failed_attempts":      failed_attempts,
        "should_end":           False,
        "should_continue":      True,
        "escalated":            False,
        "booking_name":         booking_name,
        "booking_email":        booking_email,
        "booking_phone":        booking_phone,
        "booking_in_progress": booking_in_progress, 
    }

    result = await asyncio.to_thread(agent_graph.invoke, init_state)

    return (
        result["final_answer"],
        result["conversation_history"],
        result["failed_attempts"],
        result.get("should_end", False),
        result.get("escalated", False),
        result.get("booking_name"),
        result.get("booking_email"),
        result.get("booking_phone"),
        result.get("booking_in_progress", False),
    )


# ════════════════════════════════════════════════════════
# LIVEKIT AGENT
# ════════════════════════════════════════════════════════
class WealthWiseVoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""You are a helpful voice assistant..."""
        )
        self.conversation_history: list[dict] = []
        self.failed_attempts:      int         = 0
        self.booking_name:         Optional[str] = None
        self.booking_email:        Optional[str] = None
        self.booking_phone:        Optional[str] = None
        self.booking_in_progress: bool = False 

    async def llm_node(self, chat_ctx, tools, model_settings):
        log.info("[llm_node] TRIGGERED")
        # Extract last user message from LiveKit chat context
        transcript = ""
        for msg in reversed(chat_ctx.items):
            if hasattr(msg, "role") and str(msg.role) == "user":
                content = msg.content
                if isinstance(content, list):
                    transcript = " ".join(
                        c if isinstance(c, str) else getattr(c, "text", "")
                        for c in content
                    )
                else:
                    transcript = str(content)
                break

        log.info(f"[llm_node] Transcript received: {transcript}")

        if not transcript:
            yield "I'm sorry, I didn't catch that. Could you please repeat?"
            return

        # ── TEMP DEBUG ──
        print(f"DEBUG llm_node | self.booking_in_progress = {self.booking_in_progress}")
        print(f"DEBUG llm_node | self.booking_name = {self.booking_name}")

        (
            answer,
            self.conversation_history,
            self.failed_attempts,
            should_end,
            escalated,
            self.booking_name,
            self.booking_email,
            self.booking_phone,
            self.booking_in_progress, 
        ) = await process_turn(
            transcript,
            self.conversation_history,
            self.failed_attempts,
            self.booking_name,
            self.booking_email,
            self.booking_phone,
            self.booking_in_progress,
        )

        log.info(f"[llm_node] Answer: {answer}")
        yield answer

# ════════════════════════════════════════════════════════
# ENTRYPOINT
# ════════════════════════════════════════════════════════
async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    log.info("WealthWise Voice Agent connected")

    agent = WealthWiseVoiceAgent()

    session = AgentSession(
        stt=deepgram.STT(api_key=DEEPGRAM_API_KEY),
        llm=lk_openai.LLM(model="gpt-4o-mini", api_key=OPENAI_API_KEY),  
        tts=deepgram.TTS(
            api_key=DEEPGRAM_API_KEY,
            model="aura-2-thalia-en",
        ),
        vad=silero.VAD.load(
        min_speech_duration=0.3,
        min_silence_duration=1.5,
        activation_threshold=0.65,
    ),
    allow_interruptions=True,
    min_endpointing_delay=1.5,
    )

    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(),
    )

    # Your LangGraph handles the greeting
    greeting, agent.conversation_history, agent.failed_attempts, _, _, _, _, _, agent.booking_in_progress = await process_turn(
        transcript="Hello",
        history=[],
        failed_attempts=0,
    )

    await session.say(greeting)


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint)
    )
