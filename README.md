# Marketly — Marketing Strategy Planning Platform

A modern, premium SaaS for planning and managing marketing strategies. Built with
Django 5, HTML/CSS/JS, PostgreSQL (SQLite fallback), Stripe, and allauth for social
login. Multilingual (EN / FR / AR with RTL) and full light/dark theme support.

## Highlights

- Custom email-first user, code-based email verification + password reset
- Social login (Google, Facebook, GitHub) via django-allauth
- 6 marketing solutions with detailed drawers and a stateful 3-step
  configuration wizard
- Rule-based marketing plan generator (executive summary, business analysis,
  objectives, target audience, value prop, channels, timeline, budget, KPIs,
  optimization, next steps)
- Personalized recommendation engine with filters
- AI chatbot page (mock provider, pluggable)
- Pricing page + Stripe Checkout + webhook handler
- Responsive premium UI — orange → pink → violet gradients, teal/green success
- Full Django admin for all models
- Seed demo data command

## Quickstart (local)

```bash
git clone https://github.com/jihedna/marketly.git
cd marketly

python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # then edit values as needed

python manage.py migrate
python manage.py seed_demo  # seeds solutions + pricing plans
python manage.py createsuperuser

python manage.py runserver
```

Open http://localhost:8000.

### Email (dev)

The default `EMAIL_BACKEND` is `django.core.mail.backends.console.EmailBackend`,
so verification and reset codes are **printed to the terminal** where runserver
is running. Switch to SMTP by setting `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
and filling in `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, etc.

To send **real** email via your personal Gmail account, follow the step-by-step
instructions in [GMAIL_SETUP.md](GMAIL_SETUP.md). The short version: enable
2-Step Verification, generate an App Password at
https://myaccount.google.com/apppasswords, and paste it into `.env` as
`EMAIL_HOST_PASSWORD`.

### Stripe

Set `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, and (optionally) `STRIPE_WEBHOOK_SECRET`
in your `.env`. Without them, pricing pages still render and the flow degrades
gracefully (the checkout button redirects to a friendly setup notice). With
keys set, the pricing page creates Stripe Checkout sessions and the webhook at
`/billing/webhook/stripe/` marks transactions as succeeded.

Local webhook testing:

```bash
stripe listen --forward-to localhost:8000/billing/webhook/stripe/
```

### Social login

After running migrations, go to `/admin/` → Social applications and create a
`SocialApplication` per provider (Google, Facebook, GitHub) with the client id /
secret issued by the provider. Associate it with Site `localhost:8000`.
Environment variables are also read if you prefer configuring via `.env`.

### Database

- Default: SQLite (`db.sqlite3`) for zero-config dev.
- Production: set `DATABASE_URL` (e.g., `postgres://user:pass@host:5432/db`) or
  individual `POSTGRES_*` variables.

## Project structure

```
marketly/
├── config/                 # Django project (settings, urls, wsgi/asgi)
├── apps/
│   ├── accounts/           # Custom user, profiles, auth, dashboard
│   ├── core/               # Home, contact, 404, site middleware
│   ├── solutions/          # Solutions, 3-step wizard, plan generator
│   ├── chatbot/            # Chatbot UI + mock provider
│   ├── recommendations/    # Recommendation engine
│   └── billing/            # Pricing, Stripe checkout, webhooks
├── templates/              # Global HTML templates
├── static/
│   ├── css/styles.css
│   └── js/app.js
├── locale/                 # i18n (en/fr/ar)
├── requirements.txt
└── manage.py
```

## Main user journey

1. Lands on `/` (home) → explores solutions.
2. Clicks a solution → opens detailed drawer/modal.
3. Clicks **Start with this solution** → if logged out, redirected to
   `/accounts/login/` (or signup).
4. Signs up → receives a 6-digit code (console backend prints it) → verifies email.
5. Completes 3-step wizard (Company, Campaign, Plan).
6. Gets a full marketing plan generated from the inputs.
7. Saves strategy → reviewed on `/dashboard/`.
8. Views personalized recommendations.
9. Upgrades on `/billing/pricing/` via Stripe Checkout.
10. After successful payment, premium features unlock.

## Admin

Everything is registered: users, profiles, companies, solutions, projects,
plans, conversations, messages, recommendations, pricing plans, subscriptions,
transactions, verification codes.

## Commands

```bash
python manage.py check          # system checks
python manage.py migrate        # apply migrations
python manage.py seed_demo      # seed solutions + plans
python manage.py collectstatic  # for production
python manage.py makemessages -l fr -l ar  # extract translation strings
python manage.py compilemessages            # compile .mo files
```

## Environment variables

See [`.env.example`](./.env.example) for the full list. Key ones:

| Variable | Purpose |
| -------- | ------- |
| `DJANGO_SECRET_KEY` | Django secret key (required in production) |
| `DJANGO_DEBUG` | `True` for dev |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts |
| `DATABASE_URL` | Postgres connection string (optional; SQLite fallback) |
| `EMAIL_BACKEND` | Defaults to console backend |
| `STRIPE_PUBLIC_KEY` / `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` | Stripe |
| `GOOGLE_OAUTH_CLIENT_ID` / `_SECRET` | Google login |
| `FACEBOOK_APP_ID` / `_SECRET` | Facebook login |
| `GITHUB_CLIENT_ID` / `_SECRET` | GitHub login |
| `SITE_URL` | Public base URL (used in emails + Stripe redirects) |

## License

MIT.
