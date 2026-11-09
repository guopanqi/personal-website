// ==UserScript==
// @name         X Clean - Reading Mode
// @namespace    https://github.com/guopanqi
// @version      2.1.0
// @description  Following first, hide distractions, and toggle filters in a menu.
// @match        https://x.com/*
// @match        https://twitter.com/*
// @grant        none
// @inject-into  content
// @run-at       document-idle
// ==/UserScript==

(function () {
  'use strict';
  if (document.getElementById('xclean-root')) return;

  const KEY = 'xclean-v2-settings';
  const defaults = {
    following: true, forYou: true, suggestions: true,
    trends: true, grok: true, premium: true,
    explore: false, metrics: false, paused: false
  };
  const labels = {
    following: '优先 Following', forYou: '隐藏 For You',
    suggestions: '隐藏推荐关注', trends: '隐藏热门趋势',
    grok: '隐藏 Grok', premium: '隐藏 Premium 推广',
    explore: '隐藏 Explore', metrics: '隐藏互动按钮'
  };
  let prefs = { ...defaults };
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) || '{}');
    if (saved && typeof saved === 'object') prefs = { ...prefs, ...saved };
  } catch (_) {}
  const save = () => {
    try { localStorage.setItem(KEY, JSON.stringify(prefs)); } catch (_) {}
  };
  const normalize = s => (s || '').toLowerCase().replace(/\s+/g, ' ').trim();
  const onHome = () => location.pathname === '/home' || location.pathname === '/';
  const words = {
    forYou: ['for you', '为你推荐', '為你推薦', 'おすすめ'],
    following: ['following', '正在关注', '正在關注', 'フォロー中'],
    suggestions: ['who to follow', '推荐关注', '推薦關注', '推薦追蹤'],
    trends: ["what's happening", 'what’s happening', 'trends for you',
      '有什么新鲜事', '正在发生', '热门趋势', '熱門趨勢'],
    premium: ['subscribe to premium', '订阅 premium', '訂閱 premium']
  };
  const exact = (s, list) => list.includes(normalize(s));
  const has = (s, list) => list.some(v => normalize(s).includes(v));

  const css = document.createElement('style');
  css.textContent = '[data-xclean-hidden="true"]{display:none!important}';
  (document.head || document.documentElement).append(css);
  function toggle(el, hidden) {
    if (!el) return;
    if (hidden && el.getAttribute('data-xclean-hidden') !== 'true')
      el.setAttribute('data-xclean-hidden', 'true');
    if (!hidden && el.hasAttribute('data-xclean-hidden'))
      el.removeAttribute('data-xclean-hidden');
  }
  let lastSwitch = 0;
  function apply() {
    if (prefs.paused) {
      document.querySelectorAll('[data-xclean-hidden]').forEach(el => toggle(el, false));
      return;
    }
    document.querySelectorAll('main [role="tablist"]').forEach(list => {
      const tabs = [...list.querySelectorAll('[role="tab"]')];
      const f = tabs.find(x => exact(x.textContent, words.following));
      const y = tabs.find(x => exact(x.textContent, words.forYou));
      if (!f || !y) return;
      if (onHome() && prefs.following &&
          y.getAttribute('aria-selected') === 'true' &&
          Date.now() - lastSwitch > 2000) {
        lastSwitch = Date.now();
        f.click();
      }
      toggle(y, onHome() && prefs.forYou);
    });
    document.querySelectorAll('nav a[href],header a[href]').forEach(a => {
      let path = '';
      try { path = new URL(a.href).pathname; } catch (_) {}
      const hide = (prefs.grok && (/^\/i\/grok/.test(path) || path === '/grok')) ||
        (prefs.premium && (path === '/premium' || /^\/i\/premium/.test(path))) ||
        (prefs.explore && path === '/explore');
      toggle(a, hide);
    });
    document.querySelectorAll('aside h2,[data-testid="sidebarColumn"] h2,[data-testid="cellInnerDiv"] h2')
      .forEach(h => {
        const s = normalize(h.textContent);
        const category = has(s, words.suggestions) ? 'suggestions'
          : has(s, words.trends) ? 'trends'
          : has(s, words.premium) ? 'premium' : null;
        if (!category) return;
        const box = h.closest('section,[data-testid="cellInnerDiv"]');
        if (box && !box.querySelector('[data-testid="tweet"]'))
          toggle(box, prefs[category]);
      });
    document.querySelectorAll('[data-testid="like"],[data-testid="unlike"],[data-testid="retweet"],[data-testid="unretweet"]')
      .forEach(el => toggle(el, prefs.metrics));
  }

  const root = document.createElement('div');
  root.id = 'xclean-root';
  root.style.cssText = 'position:fixed;right:14px;bottom:22px;z-index:2147483647';
  const shadow = root.attachShadow({ mode:'open' });
  shadow.innerHTML = `
    <style>
      *{box-sizing:border-box}
      button{cursor:pointer;font:inherit}
      #bubble{height:43px;width:43px;border:1px solid #567086;border-radius:50%;
        background:#17212e;color:white;font-weight:700;box-shadow:0 3px 15px #0005}
      #panel{display:none;position:absolute;bottom:53px;right:0;width:min(315px,calc(100vw - 28px));
        max-height:72vh;overflow:auto;background:#17212e;color:#fff;
        border:1px solid #485a6e;border-radius:14px;padding:16px;
        font:14px -apple-system,BlinkMacSystemFont,sans-serif;box-shadow:0 8px 30px #0008}
      #panel.open{display:block}
      h3{margin:0 0 4px;font-size:17px}
      p{margin:0 0 12px;color:#b3c2cd;font-size:12px}
      label{display:flex;align-items:center;justify-content:space-between;
        border-bottom:1px solid #ffffff18;padding:9px 0;gap:10px}
      input{width:19px;height:19px;accent-color:#82b7e7}
      .actions{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:14px}
      .actions button{background:#283b4e;border:1px solid #5c7286;color:white;
        border-radius:8px;padding:10px 4px;font-size:12px}
      #pause{grid-column:span 2}
    </style>
    <button id="bubble" aria-label="X Clean 菜单">XC</button>
    <div id="panel"><h3>X Clean · 阅读模式</h3>
      <p>设置仅保存在本机 Safari</p>
      <div id="options"></div>
      <div class="actions">
        <button id="focus">专注模式</button>
        <button id="light">轻度清理</button>
        <button id="pause">暂停清理</button>
      </div>
    </div>`;

  const panel = shadow.getElementById('panel');
  shadow.getElementById('bubble').addEventListener('click', () =>
    panel.classList.toggle('open'));
  function render() {
    const container = shadow.getElementById('options');
    container.replaceChildren();
    Object.entries(labels).forEach(([key,label]) => {
      const row = document.createElement('label');
      const name = document.createElement('span');
      name.textContent = label;
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.checked = !!prefs[key];
      checkbox.disabled = prefs.paused;
      checkbox.addEventListener('change', () => {
        prefs[key] = checkbox.checked;
        save(); render(); apply();
      });
      row.append(name, checkbox);
      container.append(row);
    });
    shadow.getElementById('pause').textContent = prefs.paused ? '恢复清理' : '暂停清理';
  }
  shadow.getElementById('focus').addEventListener('click', () => {
    prefs = {...defaults, explore:true, metrics:false};
    save(); render(); apply();
  });
  shadow.getElementById('light').addEventListener('click', () => {
    prefs = {...defaults, suggestions:false, trends:false, grok:false, premium:false};
    save(); render(); apply();
  });
  shadow.getElementById('pause').addEventListener('click', () => {
    prefs.paused = !prefs.paused;
    save(); render(); apply();
  });
  function mount() {
    if (document.body && !root.isConnected) document.body.append(root);
  }
  render();
  mount();
  let queued = false;
  const observer = new MutationObserver(() => {
    mount();
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => {queued = false; apply();});
  });
  observer.observe(document.documentElement, {childList:true,subtree:true});
  window.addEventListener('popstate', apply);
  window.addEventListener('pageshow', apply);
  apply();
})();