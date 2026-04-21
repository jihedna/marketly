"""Chatbot UI + JSON endpoint."""
from __future__ import annotations

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST

from .models import ChatConversation, ChatMessage
from .provider import SUGGESTED_PROMPTS, get_provider


@method_decorator(login_required, name="dispatch")
class ChatbotHomeView(View):
    template_name = "chatbot/home.html"

    def get(self, request, conv_id: int | None = None):
        conversations = ChatConversation.objects.filter(user=request.user)
        conversation = None
        if conv_id:
            conversation = get_object_or_404(ChatConversation, pk=conv_id, user=request.user)
        elif conversations.exists():
            conversation = conversations.first()
        chat_messages = conversation.messages.all() if conversation else []
        return render(
            request,
            self.template_name,
            {
                "conversations": conversations,
                "conversation": conversation,
                "chat_messages": chat_messages,
                "suggestions": SUGGESTED_PROMPTS,
            },
        )


@login_required
def new_conversation(request):
    conv = ChatConversation.objects.create(user=request.user)
    return redirect("chatbot:conversation", conv_id=conv.pk)


@login_required
@require_POST
def send_message(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON.")
    prompt = (payload.get("message") or "").strip()
    conv_id = payload.get("conversation_id")
    if not prompt:
        return HttpResponseBadRequest("Empty message.")

    if conv_id:
        conv = get_object_or_404(ChatConversation, pk=conv_id, user=request.user)
    else:
        conv = ChatConversation.objects.create(
            user=request.user,
            title=(prompt[:60] + ("…" if len(prompt) > 60 else "")),
        )

    ChatMessage.objects.create(conversation=conv, role="user", content=prompt)

    history = [
        {"role": m.role, "content": m.content}
        for m in conv.messages.exclude(pk=None).order_by("created_at")
    ]
    reply = get_provider().reply(history=history, prompt=prompt)
    ChatMessage.objects.create(conversation=conv, role="assistant", content=reply.content)
    conv.save()  # bumps updated_at
    return JsonResponse(
        {
            "conversation_id": conv.pk,
            "conversation_title": conv.title,
            "reply": reply.content,
        }
    )
