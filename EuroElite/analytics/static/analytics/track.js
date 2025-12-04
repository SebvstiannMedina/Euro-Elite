/**
 * Analytics tracking mejorado
 * Captura datos de navegador, performance, y eventos
 */

window.analyticsCollector = window.analyticsCollector || {
  sessionStart: Date.now(),
  events: [],
  
  getBrowserContext() {
    return {
      viewport_width: window.innerWidth,
      viewport_height: window.innerHeight,
      screen_width: window.screen.width,
      screen_height: window.screen.height,
      screen_color_depth: window.screen.colorDepth,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      language: navigator.language,
      languages: navigator.languages,
      platform: navigator.platform,
      cookie_enabled: navigator.cookieEnabled,
      do_not_track: navigator.doNotTrack,
      memory: window.deviceMemory || null,
      cores: navigator.hardwareConcurrency || null,
      connection_type: navigator.connection?.effectiveType || null,
      is_online: navigator.onLine,
    };
  },

  getPerformanceData() {
    if (!window.performance || !window.performance.timing) {
      return {};
    }

    const timing = window.performance.timing;
    const navigationStart = timing.navigationStart;

    return {
      dns_lookup_ms: timing.domainLookupEnd - timing.domainLookupStart,
      tcp_connection_ms: timing.connectEnd - timing.connectStart,
      request_time_ms: timing.responseStart - timing.requestStart,
      response_time_ms: timing.responseEnd - timing.responseStart,
      dom_interactive_ms: timing.domInteractive - navigationStart,
      dom_complete_ms: timing.domComplete - navigationStart,
      page_load_ms: timing.loadEventEnd - navigationStart,
      first_paint_ms: timing.responseEnd - navigationStart,
    };
  },

  sendEvent(name, props = {}) {
    try {
      const payload = {
        name: name,
        props: {
          ...props,
          browser_context: this.getBrowserContext(),
          session_start: this.sessionStart,
          timestamp: Date.now(),
        },
      };

      fetch('/analytics/track/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      }).catch((e) => {
        console.warn('[analytics] send failed', e);
      });
    } catch (e) {
      console.warn('[analytics] error', e);
    }
  },

  initClickTracking() {
    document.addEventListener('click', (e) => {
      const el = e.target.closest && e.target.closest('[data-event]');
      if (!el) return;

      const name = el.getAttribute('data-event');
      const propsStr = el.getAttribute('data-props');
      const props = {};

      try {
        if (propsStr) Object.assign(props, JSON.parse(propsStr));
      } catch (err) {
        console.warn('[analytics] failed to parse data-props', err);
      }

      props.element_type = el.tagName;
      props.element_id = el.id || null;
      props.element_class = el.className || null;
      props.element_text = el.textContent?.substring(0, 100) || null;

      this.sendEvent(name, props);
    });
  },

  initChangeTracking() {
    document.addEventListener('change', (e) => {
      const el = e.target.closest && e.target.closest('[data-track-change]');
      if (!el) return;

      const name = el.getAttribute('data-track-change');
      const props = {
        element_type: el.tagName,
        element_id: el.id || null,
        element_name: el.name || null,
        value: el.value || null,
        checked: el.checked || null,
      };

      this.sendEvent(name, props);
    });
  },

  initFormTracking() {
    document.addEventListener('submit', (e) => {
      const form = e.target.closest && e.target.closest('[data-track-form]');
      if (!form) return;

      const name = form.getAttribute('data-track-form');
      const props = {
        form_id: form.id || null,
        form_method: form.method || null,
        form_action: form.action || null,
      };

      this.sendEvent(name, props);
    });
  },

  initErrorTracking() {
    window.addEventListener('error', (e) => {
      this.sendEvent('js_error', {
        message: e.message || null,
        filename: e.filename || null,
        lineno: e.lineno || null,
        colno: e.colno || null,
        error: e.error ? e.error.toString() : null,
      });
    });

    window.addEventListener('unhandledrejection', (e) => {
      this.sendEvent('unhandled_promise_rejection', {
        reason: e.reason ? e.reason.toString() : null,
      });
    });
  },

  initVisibilityTracking() {
    document.addEventListener('visibilitychange', () => {
      this.sendEvent('visibility_change', {
        is_visible: !document.hidden,
      });
    });
  },

  init() {
    this.initClickTracking();
    this.initChangeTracking();
    this.initFormTracking();
    this.initErrorTracking();
    this.initVisibilityTracking();

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
          this.sendEvent('page_performance', this.getPerformanceData());
        }, 100);
      });
    } else {
      setTimeout(() => {
        this.sendEvent('page_performance', this.getPerformanceData());
      }, 100);
    }

    console.log('[analytics] initialized');
  },
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.analyticsCollector.init();
  });
} else {
  window.analyticsCollector.init();
}
