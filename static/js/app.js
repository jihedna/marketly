// Marketly client-side interactions.
(() => {
  const root = document.documentElement;

  // Theme toggle -----------------------------------------------------------
  const themeToggle = document.querySelector('[data-theme-toggle]');
  const stored = localStorage.getItem('preferred_theme');
  if (stored && (stored === 'light' || stored === 'dark')) {
    root.setAttribute('data-theme', stored);
  }
  function persistTheme(theme) {
    localStorage.setItem('preferred_theme', theme);
    fetch('/set-theme/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: 'theme=' + encodeURIComponent(theme),
    }).catch(() => {});
  }
  themeToggle?.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    persistTheme(next);
  });

  // Language switcher ------------------------------------------------------
  const lang = document.querySelector('[data-lang-switcher]');
  const langBtn = lang?.querySelector('.lang-btn');
  langBtn?.addEventListener('click', (e) => {
    e.stopPropagation();
    const open = lang.getAttribute('data-open') === 'true';
    lang.setAttribute('data-open', open ? 'false' : 'true');
    langBtn.setAttribute('aria-expanded', !open);
  });
  document.addEventListener('click', (e) => {
    if (lang && !lang.contains(e.target)) {
      lang.setAttribute('data-open', 'false');
      langBtn?.setAttribute('aria-expanded', 'false');
    }
  });
  lang?.querySelectorAll('.lang-menu button').forEach((btn) => {
    btn.addEventListener('click', () => {
      const code = btn.getAttribute('data-lang');
      localStorage.setItem('preferred_language', code);
      // Use Django's set_language to redirect properly with the new prefix.
      const form = document.createElement('form');
      form.method = 'post';
      form.action = '/i18n/setlang/';
      const csrf = document.createElement('input');
      csrf.type = 'hidden';
      csrf.name = 'csrfmiddlewaretoken';
      csrf.value = getCookie('csrftoken') || '';
      const langInput = document.createElement('input');
      langInput.type = 'hidden';
      langInput.name = 'language';
      langInput.value = code;
      const next = document.createElement('input');
      next.type = 'hidden';
      next.name = 'next';
      next.value = window.location.pathname + window.location.search;
      form.append(csrf, langInput, next);
      document.body.appendChild(form);
      form.submit();
    });
  });

  // Mobile nav toggle ------------------------------------------------------
  const navToggle = document.querySelector('[data-nav-toggle]');
  const mainNav = document.querySelector('[data-main-nav]');
  navToggle?.addEventListener('click', () => {
    const open = mainNav.getAttribute('data-open') === 'true';
    mainNav.setAttribute('data-open', open ? 'false' : 'true');
    navToggle.setAttribute('aria-expanded', !open);
  });

  // Drawer (solution modal) -----------------------------------------------
  const drawers = document.querySelectorAll('[data-drawer]');
  document.querySelectorAll('[data-open-drawer]').forEach((el) => {
    el.addEventListener('click', () => {
      const id = el.getAttribute('data-open-drawer');
      const d = document.getElementById(id);
      d?.setAttribute('data-open', 'true');
    });
  });
  drawers.forEach((d) => {
    d.querySelector('.backdrop')?.addEventListener('click', () => d.setAttribute('data-open', 'false'));
    d.querySelector('.close')?.addEventListener('click', () => d.setAttribute('data-open', 'false'));
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') drawers.forEach((d) => d.setAttribute('data-open', 'false'));
  });

  // Chatbot ---------------------------------------------------------------
  const chatForm = document.querySelector('[data-chat-form]');
  if (chatForm) {
    const textarea = chatForm.querySelector('textarea');
    const body = document.querySelector('[data-chat-body]');
    const convIdInput = chatForm.querySelector('input[name="conversation_id"]');

    function appendMsg(role, content) {
      const el = document.createElement('div');
      el.className = 'msg ' + role;
      el.textContent = content;
      body.appendChild(el);
      body.scrollTop = body.scrollHeight;
      return el;
    }

    async function sendMessage(text) {
      appendMsg('user', text);
      const typing = appendMsg('assistant', '');
      typing.innerHTML = '<span class="typing"><span></span><span></span><span></span></span>';
      try {
        const resp = await fetch('/chatbot/send/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
          body: JSON.stringify({
            message: text,
            conversation_id: convIdInput?.value || null,
          }),
        });
        const data = await resp.json();
        typing.remove();
        appendMsg('assistant', data.reply);
        if (!convIdInput.value) {
          convIdInput.value = data.conversation_id;
          const title = document.querySelector('[data-conv-title]');
          if (title) title.textContent = data.conversation_title;
          // Add to sidebar
          const sidebar = document.querySelector('[data-chat-sidebar]');
          if (sidebar) {
            const a = document.createElement('a');
            a.href = '/chatbot/c/' + data.conversation_id + '/';
            a.textContent = data.conversation_title;
            a.className = 'active';
            sidebar.prepend(a);
          }
        }
      } catch (err) {
        typing.remove();
        appendMsg('assistant', 'Sorry, something went wrong. Please try again.');
      }
    }

    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = textarea.value.trim();
      if (!text) return;
      textarea.value = '';
      sendMessage(text);
    });
    textarea.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.requestSubmit();
      }
    });
    document.querySelectorAll('[data-suggestion]').forEach((btn) => {
      btn.addEventListener('click', () => {
        textarea.value = btn.textContent.trim();
        textarea.focus();
      });
    });
  }

  // Wizard — client-side step UX (server still validates each step)
  const wizard = document.querySelector('[data-wizard]');
  if (wizard) {
    const steps = wizard.querySelectorAll('[data-wizard-step]');
    const cur = parseInt(wizard.getAttribute('data-step'), 10) || 1;
    steps.forEach((s) => {
      const n = parseInt(s.getAttribute('data-wizard-step'), 10);
      if (n < cur) s.classList.add('done');
      if (n === cur) s.classList.add('current');
    });
  }

  // Utility ---------------------------------------------------------------
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
  }
})();
