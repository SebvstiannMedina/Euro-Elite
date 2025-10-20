const REGION_COMMUNES = [
  {
    name: "Arica y Parinacota",
    comunas: ["Arica", "Camarones", "Putre", "General Lagos"]
  },
  {
    name: "Tarapac\u00e1",
    comunas: ["Iquique", "Alto Hospicio", "Pozo Almonte", "Cami\u00f1a", "Colchane", "Huara", "Pica"]
  },
  {
    name: "Antofagasta",
    comunas: ["Antofagasta", "Mejillones", "Sierra Gorda", "Taltal", "Calama", "Ollag\u00fce", "San Pedro de Atacama", "Tocopilla", "Mar\u00eda Elena"]
  },
  {
    name: "Atacama",
    comunas: ["Copiap\u00f3", "Caldera", "Tierra Amarilla", "Cha\u00f1aral", "Diego de Almagro", "Vallenar", "Freirina", "Huasco", "Alto del Carmen"]
  },
  {
    name: "Coquimbo",
    comunas: ["La Serena", "Coquimbo", "Andacollo", "La Higuera", "Paihuano", "Vicu\u00f1a", "Illapel", "Canela", "Los Vilos", "Salamanca", "Ovalle", "Combarbal\u00e1", "Monte Patria", "Punitaqui", "R\u00edo Hurtado"]
  },
  {
    name: "Valpara\u00edso",
    comunas: ["Valpara\u00edso", "Casablanca", "Conc\u00f3n", "Juan Fern\u00e1ndez", "Puchuncav\u00ed", "Quilpu\u00e9", "Quintero", "Villa Alemana", "Vi\u00f1a del Mar", "Rapa Nui (Isla de Pascua)", "Los Andes", "Calle Larga", "Rinconada", "San Esteban", "La Ligua", "Cabildo", "Papudo", "Petorca", "Zapallar", "Quillota", "La Calera", "Hijuelas", "La Cruz", "Nogales", "Limache", "Olmu\u00e9", "San Antonio", "Algarrobo", "Cartagena", "El Quisco", "El Tabo", "Santo Domingo", "San Felipe", "Catemu", "Llay-Llay", "Panquehue", "Putaendo", "Santa Mar\u00eda"]
  },
  {
    name: "Metropolitana de Santiago",
    comunas: ["Cerrillos", "Cerro Navia", "Conchal\u00ed", "El Bosque", "Estaci\u00f3n Central", "Huechuraba", "Independencia", "La Cisterna", "La Florida", "La Granja", "La Pintana", "La Reina", "Las Condes", "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maip\u00fa", "\u00d1u\u00f1oa", "Pedro Aguirre Cerda", "Pe\u00f1alol\u00e9n", "Providencia", "Pudahuel", "Quilicura", "Quinta Normal", "Recoleta", "Renca", "San Joaqu\u00edn", "San Miguel", "San Ram\u00f3n", "Santiago", "Vitacura", "Colina", "Lampa", "Tiltil", "Puente Alto", "Pirque", "San Jos\u00e9 de Maipo", "San Bernardo", "Buin", "Calera de Tango", "Paine", "Melipilla", "Alhu\u00e9", "Curacav\u00ed", "Mar\u00eda Pinto", "San Pedro", "Talagante", "El Monte", "Isla de Maipo", "Padre Hurtado", "Pe\u00f1aflor"]
  },
  {
    name: "O'Higgins",
    comunas: ["Rancagua", "Codegua", "Coinco", "Coltauco", "Do\u00f1ihue", "Graneros", "Las Cabras", "Machal\u00ed", "Malloa", "Mostazal", "Olivar", "Peumo", "Pichidegua", "Quinta de Tilcoco", "Rengo", "Requ\u00ednoa", "San Vicente", "Pichilemu", "La Estrella", "Litueche", "Marchihue", "Navidad", "Paredones", "San Fernando", "Ch\u00e9pica", "Chimbarongo", "Lolol", "Nancagua", "Palmilla", "Peralillo", "Placilla", "Pumanque", "Santa Cruz"]
  },
  {
    name: "Maule",
    comunas: ["Talca", "Constituci\u00f3n", "Curepto", "Empedrado", "Maule", "Pelarco", "Pencahue", "R\u00edo Claro", "San Clemente", "San Rafael", "Cauquenes", "Chanco", "Pelluhue", "Curic\u00f3", "Huala\u00f1\u00e9", "Licant\u00e9n", "Molina", "Rauco", "Romeral", "Sagrada Familia", "Teno", "Vichuqu\u00e9n", "Linares", "Colb\u00fan", "Longav\u00ed", "Parral", "Retiro", "San Javier", "Villa Alegre", "Yerbas Buenas"]
  },
  {
    name: "\u00d1uble",
    comunas: ["Bulnes", "Chill\u00e1n", "Chill\u00e1n Viejo", "El Carmen", "Pemuco", "Pinto", "Quill\u00f3n", "San Ignacio", "Yungay", "Cobquecura", "Coelemu", "Ninhue", "Portezuelo", "Quirihue", "R\u00e1nquil", "Trehuaco", "Coihueco", "\u00d1iqu\u00e9n", "San Carlos", "San Fabi\u00e1n", "San Nicol\u00e1s"]
  },
  {
    name: "Biob\u00edo",
    comunas: ["Concepci\u00f3n", "Coronel", "Chiguayante", "Florida", "Hualp\u00e9n", "Hualqui", "Lota", "Penco", "San Pedro de la Paz", "Santa Juana", "Talcahuano", "Tom\u00e9", "Arauco", "Ca\u00f1ete", "Contulmo", "Curanilahue", "Lebu", "Los \u00c1lamos", "Tir\u00faa", "Los \u00c1ngeles", "Alto Biob\u00edo", "Antuco", "Cabrero", "Laja", "Mulch\u00e9n", "Nacimiento", "Negrete", "Quilaco", "Quilleco", "San Rosendo", "Santa B\u00e1rbara", "Tucapel", "Yumbel"]
  },
  {
    name: "La Araucan\u00eda",
    comunas: ["Temuco", "Carahue", "Cholchol", "Cunco", "Curarrehue", "Freire", "Galvarino", "Gorbea", "Lautaro", "Loncoche", "Melipeuco", "Nueva Imperial", "Padre Las Casas", "Perquenco", "Pitrufqu\u00e9n", "Puc\u00f3n", "Saavedra", "Teodoro Schmidt", "Tolt\u00e9n", "Vilc\u00fan", "Villarrica", "Angol", "Collipulli", "Curacaut\u00edn", "Ercilla", "Lonquimay", "Los Sauces", "Lumaco", "Pur\u00e9n", "Renaico", "Traigu\u00e9n", "Victoria"]
  },
  {
    name: "Los R\u00edos",
    comunas: ["Valdivia", "Corral", "Lanco", "Los Lagos", "M\u00e1fil", "Mariquina", "Paillaco", "Panguipulli", "La Uni\u00f3n", "Futrono", "Lago Ranco", "R\u00edo Bueno"]
  },
  {
    name: "Los Lagos",
    comunas: ["Ancud", "Castro", "Chonchi", "Curaco de V\u00e9lez", "Dalcahue", "Puqueld\u00f3n", "Queil\u00e9n", "Quemchi", "Quell\u00f3n", "Quinchao", "Calbuco", "Cocham\u00f3", "Fresia", "Frutillar", "Llanquihue", "Los Muermos", "Maull\u00edn", "Puerto Montt", "Puerto Varas", "Osorno", "Puerto Octay", "Purranque", "Puyehue", "R\u00edo Negro", "San Juan de la Costa", "San Pablo", "Chait\u00e9n", "Futaleuf\u00fa", "Hualaihu\u00e9", "Palena"]
  },
  {
    name: "Ays\u00e9n del Gral. Carlos Ib\u00e1\u00f1ez del Campo",
    comunas: ["Coyhaique", "Lago Verde", "Ays\u00e9n", "Cisnes", "Guaitecas", "Cochrane", "O\u2019Higgins", "Tortel", "Chile Chico", "R\u00edo Ib\u00e1\u00f1ez"]
  },
  {
    name: "Magallanes y de la Ant\u00e1rtica Chilena",
    comunas: ["Punta Arenas", "Laguna Blanca", "R\u00edo Verde", "San Gregorio", "Porvenir", "Primavera", "Timaukel", "Cabo de Hornos (Puerto Williams)", "Ant\u00e1rtica", "Natales", "Torres del Paine"]
  },
];

document.addEventListener('DOMContentLoaded', () => {
  const ensureLocationStyles = () => {
    if (document.getElementById('perfil-location-style')) {
      return;
    }
    const style = document.createElement('style');
    style.id = 'perfil-location-style';
    style.textContent = `
      .form-select.location-disabled {
        background-color: #f8f9fa;
        color: #6c757d;
        cursor: not-allowed;
        border-color: #dee2e6;
      }
      .location-guard {
        position: absolute;
        inset: 0;
        z-index: 2;
        border-radius: inherit;
        background: transparent;
        pointer-events: none;
      }
      .location-guard.active {
        pointer-events: auto;
        cursor: not-allowed;
      }
    `;
    document.head.appendChild(style);
  };

  ensureLocationStyles();

  const form = document.getElementById('perfilForm');
  if (!form) {
    return;
  }

  const submitButtons = Array.from(
    form.querySelectorAll('button[type="submit"], input[type="submit"]')
  );

  const setSubmitDisabled = (disabled) => {
    submitButtons.forEach((button) => {
      if (!button) {
        return;
      }
      if (disabled) {
        button.setAttribute('disabled', 'disabled');
        button.setAttribute('aria-disabled', 'true');
        button.classList.add('disabled');
      } else {
        button.removeAttribute('disabled');
        button.removeAttribute('aria-disabled');
        button.classList.remove('disabled');
      }
 
 
      const updateSubmitState = () => {
    setSubmitDisabled(hasVisibleErrors());
  };

  updateSubmitState();

  const showInlineError = (field, message) => {
    const { input, feedback } = field;
    const hasMessage = Boolean(message);
    if (!feedback) {
      if (input) {
        if (hasMessage) {
          input.classList.add('is-invalid');
          input.setAttribute('aria-invalid', 'true');
        } else {
          input.classList.remove('is-invalid');
          input.removeAttribute('aria-invalid');
        }
      }
      updateSubmitState();
      return !hasMessage;
    }
    if (hasMessage) {
      feedback.textContent = message;
      feedback.classList.remove('d-none');
      if (input) {
        input.classList.add('is-invalid');
        input.setAttribute('aria-invalid', 'true');
      }
      updateSubmitState();
      return false;
    }
    feedback.textContent = '';
    feedback.classList.add('d-none');
    if (input) {
      input.classList.remove('is-invalid');
      input.removeAttribute('aria-invalid');
    }
    updateSubmitState();
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

  const normalizeText = (value) => {
    if (!value) {
      return '';
    }
    const trimmed = value.trim();
    if (!trimmed) {
      return '';
    }
    return trimmed
      .normalize('NFD')
      .replace(/[\u0300-\u036f\u00ad]/g, '')
      .replace(/[^a-zA-Z0-9]/g, '')
      .toLowerCase();
  };

  const regionLookup = new Map(
    REGION_COMMUNES.map((region) => [normalizeText(region.name), region])
  );

  const allComunas = Array.from(
    new Set(REGION_COMMUNES.flatMap((region) => region.comunas))
  ).sort((a, b) => a.localeCompare(b, 'es', { sensitivity: 'base' }));

  let comunaRequiresRegionAttempted = false;

  const setupLocationFields = () => {
    const regionField = form.querySelector('select[name="region"]');
    const comunaField = form.querySelector('[name="comuna"]');
    if (!regionField || !comunaField) {
      return;
    }

    const ensureFeedback = (input, name) => {
      if (!input) {
        return null;
      }
      const selector = `[data-feedback="${name}"]`;
      let feedback = form.querySelector(selector);
      if (feedback) {
        return feedback;
      }
      feedback = document.createElement('div');
      feedback.className = 'text-danger small d-none';
      feedback.dataset.feedback = name;
      input.insertAdjacentElement('afterend', feedback);
      return feedback;
    };

    ensureFeedback(regionField, 'region');
    ensureFeedback(comunaField, 'comuna');

    if (regionField.classList.contains('form-control')) {
      regionField.classList.remove('form-control');
      regionField.classList.add('form-select');
    } else if (!regionField.classList.contains('form-select')) {
      regionField.classList.add('form-select');
    }

    const initialComunaValue = (comunaField.value || '').trim();
    const comunaSelect = document.createElement('select');
    comunaSelect.name = comunaField.name || 'comuna';
    comunaSelect.id = comunaField.id || 'id_comuna';

    const originalClasses = (comunaField.getAttribute('class') || '')
      .split(/\s+/)
      .filter(Boolean);
    const updatedClasses = originalClasses.filter((cls) => cls !== 'form-control');
    if (!updatedClasses.includes('form-select')) {
      updatedClasses.push('form-select');
    }
    if (updatedClasses.length > 0) {
      comunaSelect.className = updatedClasses.join(' ');
    }
    if (comunaField.hasAttribute('required')) {
      comunaSelect.setAttribute('required', 'required');
    }
    if (comunaField.hasAttribute('aria-describedby')) {
      comunaSelect.setAttribute(
        'aria-describedby',
        comunaField.getAttribute('aria-describedby')
      );
    }
    Array.from(comunaField.attributes).forEach((attr) => {
      const name = attr.name;
      if (
        name === 'class' ||
        name === 'name' ||
        name === 'id' ||
        name === 'type' ||
        name === 'value' ||
        name === 'required' ||
        name === 'aria-describedby'
      ) {
        return;
      }
      if (name.startsWith('data-') || name.startsWith('aria-')) {
        comunaSelect.setAttribute(name, attr.value);
      }
    });

    comunaField.replaceWith(comunaSelect);
    ensureFeedback(comunaSelect, 'comuna');

    const wrapper = comunaSelect.parentElement;
    let comunaGuard = null;
    if (wrapper) {
      const computed = window.getComputedStyle(wrapper);
      if (!computed || computed.position === 'static') {
        wrapper.style.position = 'relative';
      }
      comunaGuard = wrapper.querySelector('[data-location-guard="comuna"]');
      if (!comunaGuard) {
        comunaGuard = document.createElement('div');
        comunaGuard.dataset.locationGuard = 'comuna';
        comunaGuard.className = 'location-guard';
        wrapper.appendChild(comunaGuard);
      }
    }

    const setComunaGuardState = (isDisabled) => {
      if (!comunaGuard) {
        return;
      }
      comunaGuard.classList.toggle('active', Boolean(isDisabled));
      if (isDisabled) {
        comunaGuard.setAttribute('aria-hidden', 'false');
      } else {
        comunaGuard.removeAttribute('aria-hidden');
      }
    };

    const refreshComunas = (regionValue, comunaValue) => {
      const normalizedRegion = normalizeText(regionValue);
      const regionData = regionLookup.get(normalizedRegion);
      const requiresRegion = !regionData && !normalizedRegion;
      const source = requiresRegion
        ? []
        : regionData
          ? [...regionData.comunas].sort((a, b) => a.localeCompare(b, 'es', { sensitivity: 'base' }))
          : allComunas;

      comunaSelect.innerHTML = '';
      const placeholder = document.createElement('option');
      placeholder.value = '';
      placeholder.textContent = requiresRegion
        ? 'Selecciona una regi\u00f3n primero'
        : 'Selecciona una comuna';
      placeholder.disabled = true;
      placeholder.hidden = true;
      comunaSelect.appendChild(placeholder);

      const normalizedComuna = normalizeText(comunaValue);
      let matched = false;
      source.forEach((name) => {
        const option = new Option(name, name);
        if (normalizedComuna && normalizeText(name) === normalizedComuna) {
          option.selected = true;
          matched = true;
        }
        comunaSelect.appendChild(option);
      });

      if (!matched) {
        placeholder.selected = true;
      }

      if (requiresRegion) {
        comunaSelect.value = '';
      }
      comunaSelect.dataset.requiresRegion = requiresRegion ? 'true' : 'false';
      comunaSelect.disabled = requiresRegion;
      comunaSelect.setAttribute('aria-disabled', requiresRegion ? 'true' : 'false');
      comunaSelect.classList.toggle('location-disabled', requiresRegion);
      if (!requiresRegion) {
        comunaRequiresRegionAttempted = false;
      }
      setComunaGuardState(requiresRegion);
    };

    const focusRegionSoon = () => {
      setTimeout(() => {
        regionField.focus({ preventScroll: true });
      }, 0);
    };

    const enforceRegionFirst = () => {
      if (normalizeText(regionField.value)) {
        return false;
      }
      comunaRequiresRegionAttempted = true;
      const comunaFieldState = getField('comuna');
      if (comunaFieldState) {
        showInlineError(comunaFieldState, 'Primero debes seleccionar regi\u00f3n');
      }
      focusRegionSoon();
      return true;
    };

    if (comunaGuard && !comunaGuard.dataset.guardReady) {
      const handleGuardInteraction = (event) => {
        if (enforceRegionFirst()) {
          event.preventDefault();
        }
      };
      comunaGuard.addEventListener('mousedown', handleGuardInteraction);
      comunaGuard.addEventListener('click', handleGuardInteraction);
      comunaGuard.addEventListener(
        'touchstart',
        (event) => {
          handleGuardInteraction(event);
        },
        { passive: false }
      );
      comunaGuard.dataset.guardReady = 'true';
    }

    refreshComunas(regionField.value, initialComunaValue);

    regionField.addEventListener('change', () => {
      refreshComunas(regionField.value, '');
      comunaRequiresRegionAttempted = false;
      const comunaFieldState = getField('comuna');
      if (comunaFieldState) {
        showInlineError(comunaFieldState, '');
      }
    });

    const guardComunaSelection = (event) => {
      if (enforceRegionFirst()) {
        event.preventDefault();
      }
    };

    comunaSelect.addEventListener('mousedown', (event) => {
      guardComunaSelection(event);
    });

    comunaSelect.addEventListener('keydown', (event) => {
      guardComunaSelection(event);
    });

    comunaSelect.addEventListener('touchstart', (event) => {
      guardComunaSelection(event);
    });

    comunaSelect.addEventListener('focus', () => {
      if (enforceRegionFirst()) {
        setTimeout(() => comunaSelect.blur(), 0);
        return;
      }
      const comunaFieldState = getField('comuna');
      if (comunaFieldState) {
        showInlineError(comunaFieldState, '');
      }
    });

    comunaSelect.addEventListener('change', () => {
      comunaRequiresRegionAttempted = false;
      const comunaFieldState = getField('comuna');
      if (comunaFieldState) {
        showInlineError(comunaFieldState, '');
      }
    });
  };

  setupLocationFields();

  const sanitizeRutValue = (value) => {
    if (!value) {
      return '';
    }
@@ -484,416 +473,384 @@
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

  const sanitizeAddressValue = (value) => {
    if (!value) {
      return '';
    }
    const normalized = value.normalize('NFC');
    const filtered = normalized.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9º°ª#.,'\/\-\s]/g, '');
    const singleSpaced = filtered.replace(/\s{2,}/g, ' ');
    const withoutLeading = singleSpaced.replace(/^\s+/, '');
    return withoutLeading.slice(0, 120);
  };

  const sanitizeAddressInput = (field) => {
    const { input } = field;
    const sanitized = sanitizeAddressValue(input.value);
    if (input.value !== sanitized) {
      input.value = sanitized;
      if (typeof input.setSelectionRange === 'function') {
        const caret = sanitized.length;
        input.setSelectionRange(caret, caret);
      }
    }
  };

  const validateAddressField = (field) => {
    const sanitized = sanitizeAddressValue(field.input.value).trim();
    field.input.value = sanitized;
    if (!sanitized) {
      return 'Debes rellenar este campo';
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
      ...getField('linea1'),
      prepare(field) {
        if (!field?.input) {
          return;
        }
        field.input.setAttribute('autocomplete', 'address-line1');
        field.input.setAttribute('inputmode', 'text');
        field.input.setAttribute('maxlength', '120');
        field.input.setAttribute('aria-required', 'true');
        field.input.setAttribute('required', 'required');
        if (!field.input.getAttribute('placeholder')) {
          field.input.setAttribute('placeholder', 'Av. Siempre Viva 742');
        }
      },
      onFocus(field) {
        showInlineError(field, '');
      },
      onInput(field) {
        sanitizeAddressInput(field);
        showInlineError(field, '');
      },
      onPaste(field, event) {
        applyPasteSanitation(field, event, sanitizeAddressValue, sanitizeAddressInput);
      },
      onBlur(field) {
        field.input.value = sanitizeAddressValue(field.input.value).trim();
      },
      validate(field) {
        return validateAddressField(field);
      }
    },
     {
      ...getField('region'),
      prepare(field) {
        if (!field?.input) {
          return;
        }
        field.input.classList.remove('form-control');
        if (!field.input.classList.contains('form-select')) {
          field.input.classList.add('form-select');
        }
        field.input.setAttribute('aria-required', 'true');
      },
      onFocus(field) {
        showInlineError(field, '');
      },
      onInput(field) {
        showInlineError(field, '');
      },
      onBlur(field) {
        if (!normalizeText(field.input.value)) {
          field.input.value = '';
        }
      },
      validate(field) {
        if (!normalizeText(field.input.value)) {
          return 'Debes seleccionar una regi\u00f3n';
        }
        return '';
      }
    },
    {
      ...getField('comuna'),
      prepare(field) {
        if (!field?.input) {
          return;
        }
        field.input.classList.remove('form-control');
        if (!field.input.classList.contains('form-select')) {
          field.input.classList.add('form-select');
        }
        field.input.setAttribute('aria-required', 'true');
      },
      onFocus(field) {
        if (!normalizeText(field.input.value)) {
          const regionInput = form.querySelector('[name="region"]');
          const regionSelected = normalizeText(regionInput?.value || '');
          if (!regionSelected && comunaRequiresRegionAttempted) {
            showInlineError(field, 'Primero debes seleccionar regi\u00f3n');
            return;
          }
        }
        showInlineError(field, '');
      },
      onInput(field) {
        comunaRequiresRegionAttempted = false;
        showInlineError(field, '');
      },
      onBlur(field) {
        if (!normalizeText(field.input.value)) {
          field.input.value = '';
        }
      },
      validate(field) {
        const regionInput = form.querySelector('[name="region"]');
        const regionSelected = normalizeText(regionInput?.value || '');
        if (!regionSelected) {
          return comunaRequiresRegionAttempted ? 'Primero debes seleccionar regi\u00f3n' : '';
        }
        if (!normalizeText(field.input.value)) {
          return 'Debes seleccionar una comuna';
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
  updateSubmitState();

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