document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('perfilForm');
  if (!form) {
    return;
  }

  const showInlineError = (field, message) => {
    const { input, feedback } = field;
    if (!feedback) {
      return !message;
    }
    if (message) {
      feedback.textContent = message;
      feedback.classList.remove('d-none');
      input.classList.add('is-invalid');
      input.setAttribute('aria-invalid', 'true');
      return false;
    }
    feedback.textContent = '';
    feedback.classList.add('d-none');
    input.classList.remove('is-invalid');
    input.removeAttribute('aria-invalid');
    return true;
  };

  const getField = (name) => {
    const input = form.querySelector(`[name="${name}"]`);
    const feedback = form.querySelector(`[data-feedback="${name}"]`);
    if (!input) {
      return null;
    }
    return { name, input, feedback };
  };

  const applyPlaceholders = () => {
    const placeholders = [
      { name: 'first_name', value: 'Ingresa tu nombre' },
      { name: 'last_name', value: 'Ingresa tu apellido' },
      { name: 'email', value: 'ejemplo@dominio.com' },
    ];
    placeholders.forEach(({ name, value }) => {
      const field = getField(name);
      if (field?.input) {
        field.input.setAttribute('placeholder', value);
      }
    });
  };

  applyPlaceholders();

  const sanitizeRutValue = (value) => {
    if (!value) {
      return '';
    }
    const normalized = value.normalize('NFC').replace(/\s+/g, '');
    let result = '';
    for (const char of normalized) {
      if (result.length >= 9) {
        break;
      }
      if (/[0-9]/.test(char)) {
        result += char;
        continue;
      }
      if ((char === 'k' || char === 'K') && result.length === 8) {
        result += 'K';
      }
    }
    return result;
  };

  const cleanRut = (value) => sanitizeRutValue(value);

  const formatRut = (value) => {
    const cleaned = cleanRut(value);
    if (cleaned.length <= 1) {
      return cleaned;
    }
    const body = cleaned.slice(0, -1);
    const dv = cleaned.slice(-1);
    const reversed = body.split('').reverse();
    const chunks = [];
    for (let index = 0; index < reversed.length; index += 3) {
      chunks.push(reversed.slice(index, index + 3).reverse().join(''));
    }
    return chunks.reverse().join('.') + '-' + dv;
  };

  const computeDV = (body) => {
    let sum = 0;
    let multiplier = 2;
    for (let index = body.length - 1; index >= 0; index -= 1) {
      sum += parseInt(body[index], 10) * multiplier;
      multiplier = multiplier === 7 ? 2 : multiplier + 1;
    }
    const remainder = 11 - (sum % 11);
    if (remainder === 11) {
      return '0';
    }
    if (remainder === 10) {
      return 'K';
    }
    return String(remainder);
  };

  const isValidRut = (value) => {
    const cleaned = cleanRut(value);
    if (cleaned.length < 2) {
      return false;
    }
    const body = cleaned.slice(0, -1);
    const dv = cleaned.slice(-1);
    if (!/^[0-9]+$/.test(body)) {
      return false;
    }
    return computeDV(body) === dv;
  };

  const sanitizeNameValue = (value) => {
    if (!value) {
      return '';
    }
    const normalized = value.normalize('NFC');
    const allowedOnly = normalized.replace(/[^A-Za-z\u00C1\u00C9\u00CD\u00D3\u00DA\u00DC\u00E1\u00E9\u00ED\u00F3\u00FA\u00FC\u00D1\u00F1\s]/g, '');
    const singleSpaced = allowedOnly.replace(/\s{2,}/g, ' ');
    return singleSpaced.replace(/^\s+/, '');
  };

  const sanitizeNameInput = (field) => {
    const { input } = field;
    const sanitized = sanitizeNameValue(input.value);
    if (input.value !== sanitized) {
      input.value = sanitized;
      input.setSelectionRange(sanitized.length, sanitized.length);
    }
  };

  const handleNamePaste = (field, event) => {
    applyPasteSanitation(field, event, sanitizeNameValue, sanitizeNameInput);
  };

  const validateNameField = (field, emptyMessage, shortMessage) => {
    const sanitized = sanitizeNameValue(field.input.value).trim();
    field.input.value = sanitized;
    if (!sanitized) {
      return emptyMessage;
    }
    if (sanitized.length > 0 && sanitized.length < 4) {
      return shortMessage;
    }
    return '';
  };

  const sanitizeEmailValue = (value) => {
    if (!value) {
      return '';
    }
    let result = '';
    let hasAt = false;
    const normalized = value.normalize('NFC');
    const allowedChars = 'abcdefghijklmnopqrstuvwxyz0123456789._%+-';
    for (const char of normalized) {
      const lower = char.toLowerCase();
      if (allowedChars.includes(lower)) {
        result += lower;
        continue;
      }
      if ((char === '@' || lower === '@') && !hasAt) {
        result += '@';
        hasAt = true;
      }
    }
    return result;
  };

  const sanitizeEmailInput = (field) => {
    const { input } = field;
    const sanitized = sanitizeEmailValue(input.value);
    if (input.value !== sanitized) {
      input.value = sanitized;
      input.setSelectionRange(sanitized.length, sanitized.length);
    }
  };

  const sanitizeRutInput = (field) => {
    const { input } = field;
    const sanitized = sanitizeRutValue(input.value);
    if (input.value !== sanitized) {
      input.value = sanitized;
      if (typeof input.setSelectionRange === 'function') {
        const caret = sanitized.length;
        input.setSelectionRange(caret, caret);
      }
    }
  };

  const applyPasteSanitation = (field, event, sanitizeValue, sanitizeInput) => {
    const clipboard = event.clipboardData || window.clipboardData;
    const runSanitizer = () => {
      sanitizeInput(field);
      showInlineError(field, '');
    };
    if (!clipboard || typeof clipboard.getData !== 'function') {
      setTimeout(runSanitizer, 0);
      return;
    }
    const pasted = clipboard.getData('text') || '';
    const sanitized = sanitizeValue(pasted);
    event.preventDefault();
    const input = field.input;
    const start = input.selectionStart ?? input.value.length;
    const end = input.selectionEnd ?? input.value.length;
    const before = input.value.slice(0, start);
    const after = input.value.slice(end);
    input.value = `${before}${sanitized}${after}`;
    if (typeof input.setSelectionRange === 'function') {
      const caret = start + sanitized.length;
      input.setSelectionRange(caret, caret);
    }
    runSanitizer();
    input.dispatchEvent(new Event('input', { bubbles: true }));
  };

  const handleEmailPaste = (field, event) => {
    applyPasteSanitation(field, event, sanitizeEmailValue, sanitizeEmailInput);
  };

  const normalizeEmail = (value) => sanitizeEmailValue((value || '').trim());

  const sanitizePhoneValue = (value) => {
    const digits = (value || '').replace(/\D/g, '');
    return digits.slice(0, 8);
  };

  const sanitizePhoneInput = (field) => {
    const { input } = field;
    const sanitized = sanitizePhoneValue(input.value);
    if (input.value !== sanitized) {
      input.value = sanitized;
      if (typeof input.setSelectionRange === 'function') {
        const caret = sanitized.length;
        input.setSelectionRange(caret, caret);
      }
    }
  };

  const sanitizePostalValue = (value) => (value || '').replace(/\D/g, '').slice(0, 7);

  const sanitizePostalInput = (field) => {
    const { input } = field;
    const sanitized = sanitizePostalValue(input.value);
    if (input.value !== sanitized) {
      input.value = sanitized;
      if (typeof input.setSelectionRange === 'function') {
        const caret = sanitized.length;
        input.setSelectionRange(caret, caret);
      }
    }
  };

  const fields = [
    {
      ...getField('first_name'),
      prepare(field) {
        field.input.setAttribute('autocomplete', 'given-name');
        field.input.setAttribute('autocapitalize', 'words');
        field.input.setAttribute('spellcheck', 'false');
      },
      onFocus(field) {
        showInlineError(field, '');
      },
      onInput(field) {
        sanitizeNameInput(field);
        showInlineError(field, '');
      },
      onBlur(field) {
        field.input.value = sanitizeNameValue(field.input.value).trim();
      },
      onPaste(field, event) {
        handleNamePaste(field, event);
      },
      validate(field) {
        return validateNameField(field, 'Debes rellenar este campo', 'Ingresa un nombre v\u00E1lido');
      }
    },
    {
      ...getField('last_name'),
      prepare(field) {
        field.input.setAttribute('autocomplete', 'family-name');
        field.input.setAttribute('autocapitalize', 'words');
        field.input.setAttribute('spellcheck', 'false');
      },
      onFocus(field) {
        showInlineError(field, '');
      },
      onInput(field) {
        sanitizeNameInput(field);
        showInlineError(field, '');
      },
      onBlur(field) {
        field.input.value = sanitizeNameValue(field.input.value).trim();
      },
      onPaste(field, event) {
        handleNamePaste(field, event);
      },
      validate(field) {
        return validateNameField(field, 'Debes rellenar este campo', 'Ingresa un apellido v\u00E1lido');
      }
    },
    {
      ...getField('email'),
      prepare(field) {
        field.input.setAttribute('inputmode', 'email');
        field.input.setAttribute('spellcheck', 'false');
        field.input.setAttribute('autocorrect', 'off');
        field.input.setAttribute('autocapitalize', 'none');
        if (!field.input.getAttribute('autocomplete')) {
          field.input.setAttribute('autocomplete', 'email');
        }
      },
      onFocus(field) {
        showInlineError(field, '');
      },
      onInput(field) {
        sanitizeEmailInput(field);
        showInlineError(field, '');
      },
      onBlur(field) {
        field.input.value = normalizeEmail(field.input.value);
      },
      onPaste(field, event) {
        handleEmailPaste(field, event);
      },
      validate(field) {
        const value = normalizeEmail(field.input.value);
        field.input.value = value;
        if (!value) {
          return 'Debes rellenar este campo';
        }
        if (!/^[^@\s]+@[^@\s]+\.[^@\s]{3,}$/.test(value)) {
          return 'Inv\u00E1lido, estructura correcta; nombre@correo.***';
        }
        return '';
      }
    },
    {
      ...getField('telefono'),
      prepare(field) {
        field.input.setAttribute('inputmode', 'numeric');
        field.input.setAttribute('maxlength', '8');
        field.input.setAttribute('pattern', '[0-9]{8}');
        field.input.setAttribute('placeholder', '12345678');
        if (!field.input.getAttribute('autocomplete')) {
          field.input.setAttribute('autocomplete', 'tel');
        }
      },
      onFocus(field) {
        showInlineError(field, '');
      },
      onInput(field) {
        sanitizePhoneInput(field);
        showInlineError(field, '');
      },
      onPaste(field, event) {
        applyPasteSanitation(field, event, sanitizePhoneValue, sanitizePhoneInput);
      },
      onBlur(field) {
        field.input.value = sanitizePhoneValue(field.input.value);
      },
      validate(field) {
        const digits = sanitizePhoneValue(field.input.value);
        field.input.value = digits;
        if (!digits) {
          return 'Debes rellenar este campo';
        }
        if (digits.length < 8) {
          return 'Tel\u00e9fono debe contener 8 caracteres';
        }
        return '';
      }
    },
    {
      ...getField('codigo_postal'),
      prepare(field) {
        field.input.setAttribute('inputmode', 'numeric');
        field.input.setAttribute('maxlength', '7');
        field.input.setAttribute('pattern', '[0-9]{7}');
        field.input.setAttribute('placeholder', '1234567');
      },
      onFocus(field) {
        showInlineError(field, '');
      },
      onInput(field) {
        sanitizePostalInput(field);
        showInlineError(field, '');
      },
      onPaste(field, event) {
        applyPasteSanitation(field, event, sanitizePostalValue, sanitizePostalInput);
      },
      onBlur(field) {
        field.input.value = sanitizePostalValue(field.input.value);
      },
      validate(field) {
        const digits = sanitizePostalValue(field.input.value);
        field.input.value = digits;
        if (!digits) {
          return 'Debes rellenar este campo';
        }
        if (digits.length < 7) {
          return 'C\u00f3digo postal debe tener 7 d\u00edgitos';
        }
        return '';
      }
    },
    {
      ...getField('rut'),
      prepare(field) {
        field.input.setAttribute('inputmode', 'text');
        field.input.setAttribute('maxlength', '12');
        field.input.setAttribute('pattern', '\d{1,2}\.\d{3}\.\d{3}-[\dkK]');
        field.input.setAttribute('placeholder', '12.345.678-5');
        field.input.setAttribute('autocomplete', 'off');
      },
      onFocus(field) {
        sanitizeRutInput(field);
        showInlineError(field, '');
      },
      onInput(field) {
        sanitizeRutInput(field);
        showInlineError(field, '');
      },
      onPaste(field, event) {
        applyPasteSanitation(field, event, sanitizeRutValue, sanitizeRutInput);
      },
      onBlur(field) {
        const sanitized = sanitizeRutValue(field.input.value);
        if (sanitized.length === 8 || sanitized.length === 9) {
          field.input.value = formatRut(sanitized);
        } else {
          field.input.value = sanitized;
        }
      },
      validate(field) {
        const sanitized = sanitizeRutValue(field.input.value);
        field.input.value = sanitized;
        if (!sanitized) {
          return 'Debes rellenar este campo';
        }
        if (sanitized.length < 8) {
          return 'Rut debe contener entre 8 y 9 caracteres';
        }
        const formatted = formatRut(sanitized);
        field.input.value = formatted;
        if (!/^[0-9]{1,2}\.[0-9]{3}\.[0-9]{3}-[0-9K]$/i.test(formatted)) {
          return 'Formato inv\u00E1lido. Usa 12.345.678-5';
        }
        if (!isValidRut(formatted)) {
          return 'El d\u00EDgito verificador no coincide.';
        }
        return '';
      }
    }
  ].filter(Boolean);

  const validateField = (field) => {
    if (!field || !field.input || field.input.disabled) {
      return true;
    }
    const message = field.validate ? field.validate(field) : '';
    return showInlineError(field, message);
  };

  fields.forEach((field) => {
    if (!field?.input) {
      return;
    }
    field.prepare?.(field);
    field.input.addEventListener('focus', () => field.onFocus?.(field));
    field.input.addEventListener('input', () => field.onInput?.(field));
    field.input.addEventListener('paste', (event) => field.onPaste?.(field, event));
    field.input.addEventListener('blur', () => {
      field.onBlur?.(field);
      validateField(field);
    });
  });

  const runInitialValidation = () => {
    fields.forEach((field) => {
      if (!field?.input) {
        return;
      }
      field.onBlur?.(field);
      validateField(field);
    });
  };

  runInitialValidation();

  form.addEventListener('submit', (event) => {
    let isValid = true;
    fields.forEach((field) => {
      const ok = validateField(field);
      if (!ok) {
        isValid = false;
      }
    });
    if (!isValid) {
      event.preventDefault();
      event.stopPropagation();
      const firstInvalid = fields.find((field) => field.input && field.input.classList.contains('is-invalid'));
      if (firstInvalid?.input) {
        firstInvalid.input.focus({ preventScroll: true });
      }
    }
  });
});
