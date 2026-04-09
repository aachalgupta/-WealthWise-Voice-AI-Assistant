# WealthWise Voice AI Assistant

An agentic voice AI assistant for a financial advisory firm with 5 nodes and 3 tools. Built with LiveKit, LangGraph, GPT-4o, and Deepgram handles real-time voice conversations, answers company FAQs, and books appointments on Google Calendar.

---

## What It Does

- Answers questions about WealthWise Advisory services, fees, and booking process using RAG 
- Books 30-minute discovery call appointments on Google Calendar with Google Meet link
- Handles real-time voice conversations via LiveKit with STT (Deepgram) and TTS (Deepgram)
- Sends email confirmations and calendar invites to clients automatically
- Detects user sentiment and adjusts tone accordingly
- Auto-escalates to a human advisor after repeated failures or complaints
- Blocks unsafe or abusive input before it reaches the AI

---

## Tech Stack
- Voice input STT/output TTS: Deepgram
- Voice infrastructure: LiveKit
- LLM: OpenAI
- Agent framework: LangGraph
- Vector database: Qdrant
- Calendar: Google Calendar API

---

## Architecture

```
User (voice)
    ↓
LiveKit (STT via Deepgram)
    ↓
LangGraph Pipeline
    ├── Guardrail node       — blocks unsafe input
    ├── Sentiment node       — detects user mood
    ├── Intent node          — routes to correct handler
    ├── Answer node          — GPT-4o with tool calling
    │       ├── search_knowledge_base tool  (Qdrant RAG)
    │       ├── check_available_slots tool  (Google Calendar)
    │       └── book_appointment_tool tool  (Google Calendar)
    └── Escalation node      — human handoff after failures
    ↓
LiveKit (TTS via Deepgram)
    ↓
User (voice)
```
---

## How Appointments Work

1. User says they want to book
2. Bot fetches available 30-minute slots for today and tomorrow
3. User picks a slot
4. Bot collects name, email, and phone number in one message
5. Bot confirms all details
6. Google Calendar event is created with a Google Meet link
7. Email invite is sent to the user automatically

Appointments are only accepted for today and tomorrow. Requests for later dates are declined with an explanation.

---

