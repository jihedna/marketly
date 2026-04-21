"""Chat provider abstraction — swap the mock for a real LLM later."""
from __future__ import annotations

from dataclasses import dataclass


SUGGESTED_PROMPTS = [
    "Build a 90-day plan to grow our SaaS with $10k/month ad budget.",
    "Suggest 5 content pillars for a sustainable fashion brand.",
    "How should I allocate $20k/month across Meta and Google for lead gen?",
    "Give me 10 headline variations for our spring product launch.",
    "What KPIs should I track for a B2B demand generation campaign?",
]


@dataclass
class ChatReply:
    content: str
    provider: str = "mock"


class ChatProvider:
    """Interface for pluggable providers."""

    def reply(self, *, history: list[dict], prompt: str) -> ChatReply:
        raise NotImplementedError


class MockMarketingProvider(ChatProvider):
    """Deterministic marketing-flavoured mock, structured for readability."""

    def reply(self, *, history: list[dict], prompt: str) -> ChatReply:
        p = prompt.lower().strip()

        if any(k in p for k in ("budget", "allocate", "spend", "$")):
            content = (
                "Here's a starting allocation for a balanced growth mix:\n\n"
                "• 45% — Paid acquisition (Google + Meta)\n"
                "• 20% — Creative production & testing\n"
                "• 15% — Content & SEO\n"
                "• 10% — Lifecycle email + CRM\n"
                "• 10% — Analytics, experimentation, MarTech\n\n"
                "Review monthly and reweight toward your best-performing channels."
            )
        elif any(k in p for k in ("launch", "new product", "rollout")):
            content = (
                "A launch plan I recommend:\n\n"
                "1. Pre-launch (weeks 1-2): waitlist, teaser content, PR outreach.\n"
                "2. Launch week: coordinated email, paid, PR, and community push.\n"
                "3. Post-launch (weeks 2-6): retargeting, UGC, case studies, lifecycle flows.\n\n"
                "Track: waitlist conversion, launch-day revenue, 30-day repeat rate."
            )
        elif any(k in p for k in ("kpi", "metric", "measure")):
            content = (
                "Track a tight, outcome-focused KPI set:\n\n"
                "• Acquisition: CAC, CPL, CVR by channel\n"
                "• Engagement: CTR, landing page CVR, scroll depth\n"
                "• Retention: 30/60/90-day repeat rate, churn\n"
                "• Economics: ROAS, MER (marketing efficiency ratio), LTV:CAC"
            )
        elif any(k in p for k in ("headline", "copy", "slogan")):
            content = (
                "Headline patterns that convert:\n\n"
                "• Outcome + timeframe: 'Grow pipeline 2× in 90 days'\n"
                "• Proof: 'Used by 12,000 marketers'\n"
                "• Objection kill: 'No credit card, cancel anytime'\n"
                "• Curiosity: 'The 4-line email that books demos'\n"
                "• Direct benefit: 'Launch campaigns in minutes, not weeks'"
            )
        elif any(k in p for k in ("content", "pillars", "calendar", "seo")):
            content = (
                "Try these pillars and adapt to your brand:\n\n"
                "1. Education (how-to, frameworks)\n"
                "2. Behind-the-scenes (team, craft)\n"
                "3. Proof (case studies, stats, testimonials)\n"
                "4. Lifestyle & culture\n"
                "5. Product deep-dives\n\n"
                "Cadence: 3-4 posts/week per core channel, 1 long-form/week."
            )
        else:
            content = (
                "Great question. A strong marketing plan typically covers:\n\n"
                "• A clear objective tied to a business outcome\n"
                "• Audience insights and positioning\n"
                "• Channel mix with budget and milestones\n"
                "• Creative briefs and content calendar\n"
                "• KPIs and an experiment backlog\n\n"
                "Share your industry, budget, and goal and I'll tailor it further."
            )
        return ChatReply(content=content, provider="mock")


def get_provider() -> ChatProvider:
    return MockMarketingProvider()
