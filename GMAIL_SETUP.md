# Sending real emails from Marketly via Gmail

By default Marketly uses Django's **console** email backend: verification codes and
password-reset codes are printed to the terminal running `python manage.py runserver`
instead of being actually delivered. This is fine for quick local exploration, but if
you want real emails (verification code in the user's inbox, password-reset link that
really arrives, etc.), you need to point Django at a real SMTP server.

This guide walks you through using your personal Gmail account as the sender.

> **Why can't I configure Gmail from the hosted Devin VM?**
> The Devin VM blocks outbound SMTP ports (25/465/587). Gmail SMTP will therefore time
> out from that environment. Run the project **on your own computer** and Gmail will
> work fine. If you need real email while running on the Devin VM, use a provider with
> an HTTPS API or an alt-port SMTP endpoint (SendGrid, Brevo, Mailjet, MailerSend
> all work on port 2525 from there).

---

## Step 1 — Enable 2-Step Verification on your Google account

App Passwords are only available on accounts with 2SV turned on.

1. Go to https://myaccount.google.com/security
2. Under **How you sign in to Google**, click **2-Step Verification** and follow the
   prompts to enable it (needs a phone number).

## Step 2 — Create a Google App Password

1. Go to https://myaccount.google.com/apppasswords
2. **App name**: type something like `Marketly dev`
3. Click **Create**. Google shows a 16-character password like
   `abcd efgh ijkl mnop`.
4. Copy it. You won't be able to see it again.

> The App Password is tied to your Google account but only valid for app-level
> authentication. You can revoke it at any time from the same page.

## Step 3 — Put the credentials into `.env`

In your local checkout of Marketly, copy the example file if you haven't already:

```bash
cp .env.example .env
```

Then open `.env` and fill in the email section like this:

```dotenv
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your.address@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop               # 16-char App Password, no spaces
DEFAULT_FROM_EMAIL=Marketly <your.address@gmail.com>
```

Notes:
- `EMAIL_HOST_PASSWORD` is the App Password, **not** your regular Gmail password.
- You can paste the App Password with or without the spaces Google displays — both
  work. The example above has the spaces stripped for clarity.
- `DEFAULT_FROM_EMAIL` should match the Gmail address in `EMAIL_HOST_USER`. Gmail
  rewrites the `From:` header otherwise.

## Step 4 — Restart the server and test

```bash
python manage.py runserver
```

Then in another terminal (or a Django shell), send a test message to yourself:

```bash
python manage.py shell -c "from django.core.mail import send_mail; \
  send_mail('Marketly test', 'If you see this, SMTP works.', \
  None, ['your.address@gmail.com'], fail_silently=False)"
```

Check your Gmail inbox — if the message arrives, the full verification-code and
password-reset flows will now deliver for real.

## Troubleshooting

- **`SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')`**
  Double-check that 2-Step Verification is actually enabled, and that the value of
  `EMAIL_HOST_PASSWORD` is the 16-character App Password (no quotes, no spaces).
- **`SMTPServerDisconnected` or `Connection timed out`**
  Your network is blocking outbound 587. Try port 465 with `EMAIL_USE_SSL=True` and
  `EMAIL_USE_TLS=False` — or use one of the alt-port providers listed at the top.
- **Email lands in spam on the recipient side**
  Expected for a dev-only setup. Gmail's spam filter distrusts mail from addresses
  that don't control a domain. For production, buy a domain and use a real
  transactional-email provider (SendGrid, Postmark, Resend, etc.) with SPF/DKIM
  configured.
