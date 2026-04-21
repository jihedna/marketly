"""Static catalog of marketing solutions seeded into the DB and shown in the UI."""
from __future__ import annotations

from django.utils.translation import gettext_lazy as _

MARKETING_SOLUTIONS = [
    {
        "slug": "social-media",
        "icon": "📱",
        "title": _("Social media strategy"),
        "tagline": _("Grow audiences across every platform with intent."),
        "overview": _(
            "A full-funnel social strategy that turns passive scrollers into loyal "
            "customers, with content pillars, influencer collaborations, and paid "
            "amplification."
        ),
        "benefits": [
            _("Clear content pillars and calendar"),
            _("Platform-specific creative briefs"),
            _("Influencer & UGC shortlists"),
            _("Monthly performance reviews"),
        ],
        "process": [
            _("Audit current channels and competitors"),
            _("Define personas and content pillars"),
            _("Produce creative and schedule"),
            _("Launch, measure, iterate"),
        ],
        "use_cases": [
            _("D2C brand launching a new product line"),
            _("B2B SaaS building thought leadership"),
            _("Local business driving footfall"),
        ],
        "case_study": _(
            "Nova Retail grew Instagram engagement by 4.3× and reduced CAC by 38% in 90 days."
        ),
    },
    {
        "slug": "paid-ads",
        "icon": "🎯",
        "title": _("Paid ads strategy"),
        "tagline": _("Scale customer acquisition with measurable paid media."),
        "overview": _(
            "Multi-channel paid media strategy across Meta, Google, TikTok and LinkedIn "
            "built on forecasted unit economics."
        ),
        "benefits": [
            _("Full-funnel campaign architecture"),
            _("Creative testing framework"),
            _("Bid and budget pacing automation"),
            _("Weekly performance reports"),
        ],
        "process": [
            _("Map funnel and KPIs"),
            _("Design campaign architecture"),
            _("Launch creative tests"),
            _("Scale winning cohorts"),
        ],
        "use_cases": [
            _("E-commerce scaling to new geos"),
            _("SaaS driving demo bookings"),
            _("Marketplace boosting liquidity"),
        ],
        "case_study": _(
            "Helix Analytics lowered cost-per-demo by 52% while tripling booked meetings."
        ),
    },
    {
        "slug": "branding",
        "icon": "✨",
        "title": _("Branding strategy"),
        "tagline": _("Define a distinct voice, story and identity."),
        "overview": _(
            "From brand archetype to visual system — everything that makes your brand "
            "unmistakable at every touchpoint."
        ),
        "benefits": [
            _("Brand positioning statement"),
            _("Tone of voice guidelines"),
            _("Visual identity system"),
            _("Rollout playbook"),
        ],
        "process": [
            _("Discovery workshops"),
            _("Positioning & narrative"),
            _("Visual identity design"),
            _("Guidelines & rollout"),
        ],
        "use_cases": [
            _("Rebrand after a funding round"),
            _("New product sub-brand"),
            _("Refreshing legacy brands"),
        ],
        "case_study": _("Atlas Studio's rebrand lifted aided recall by 3.8× in 6 months."),
    },
    {
        "slug": "seo-content",
        "icon": "📝",
        "title": _("SEO & content strategy"),
        "tagline": _("Win compounding organic traffic."),
        "overview": _(
            "Search-first content planning across topical clusters, technical SEO "
            "foundations, and programmatic content opportunities."
        ),
        "benefits": [
            _("Keyword cluster roadmap"),
            _("Editorial calendar"),
            _("Technical SEO audit"),
            _("Link-building playbook"),
        ],
        "process": [
            _("Keyword & competitor research"),
            _("Topical authority map"),
            _("Content production"),
            _("Measure and refresh"),
        ],
        "use_cases": [
            _("New SaaS entering a market"),
            _("Media brand expanding verticals"),
            _("B2B lowering paid dependency"),
        ],
        "case_study": _(
            "Northwind tripled organic signups in 9 months with a topical authority plan."
        ),
    },
    {
        "slug": "email",
        "icon": "📧",
        "title": _("Email marketing strategy"),
        "tagline": _("Convert, retain and reactivate with lifecycle email."),
        "overview": _(
            "Lifecycle email programs across onboarding, promotion, retention and "
            "win-back, with segmentation and deliverability at the core."
        ),
        "benefits": [
            _("Lifecycle program design"),
            _("Segmentation strategy"),
            _("Template system"),
            _("A/B testing roadmap"),
        ],
        "process": [
            _("Audit CRM & list health"),
            _("Map lifecycle stages"),
            _("Design flows and creative"),
            _("Launch and optimize"),
        ],
        "use_cases": [
            _("E-commerce retention"),
            _("SaaS onboarding"),
            _("Event and webinar nurture"),
        ],
        "case_study": _("Lumen Co. recovered 18% of abandoned carts with a 3-step flow."),
    },
    {
        "slug": "analytics",
        "icon": "📊",
        "title": _("Campaign analytics & optimization"),
        "tagline": _("Measure what matters and improve every month."),
        "overview": _(
            "Set up reliable measurement, build an executive dashboard, and run a "
            "disciplined experiment cadence."
        ),
        "benefits": [
            _("Unified KPI dashboard"),
            _("Experiment backlog"),
            _("Attribution framework"),
            _("Monthly growth review"),
        ],
        "process": [
            _("KPI & measurement design"),
            _("Dashboard & data pipelines"),
            _("Experiment planning"),
            _("Iterate and scale wins"),
        ],
        "use_cases": [
            _("Mature brands seeking incremental wins"),
            _("Agencies needing reporting rigor"),
            _("Growth teams scaling cross-channel"),
        ],
        "case_study": _("Orbit Mobility shipped 24 experiments in a quarter; 9 were winners."),
    },
]

SOLUTION_BY_SLUG = {s["slug"]: s for s in MARKETING_SOLUTIONS}
