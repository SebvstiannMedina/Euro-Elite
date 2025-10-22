// =============== VARIABLES GLOBALES ===============
let currentSlide = 0;
const totalSlides = 3;
let isUserMenuOpen = false;

// =============== CAROUSEL ===============
function updateCarousel() {
    const track = document.getElementById('carousel-track');
    const dots = document.querySelectorAll('.nav-dot');
    if (!track || !dots || dots.length === 0) return;

    track.style.transform = `translateX(-${currentSlide * 33.3333}%)`;
    dots.forEach((dot, index) => {
        dot.classList.toggle('active', index === currentSlide);
    });
}
function goToSlide(slideIndex) { currentSlide = slideIndex; updateCarousel(); }
function nextSlide() { currentSlide = (currentSlide + 1) % totalSlides; updateCarousel(); }
try { setInterval(nextSlide, 4000); } catch { }

// =============== MOBILE MENU ===============
function toggleMobileMenu() {
    const menu = document.getElementById('navbar-menu');
    const toggle = document.querySelector('.navbar-toggle i');
    menu.classList.toggle('active');
    if (menu.classList.contains('active')) {
        toggle.classList.remove('fa-bars'); toggle.classList.add('fa-times');
    } else {
        toggle.classList.remove('fa-times'); toggle.classList.add('fa-bars');
    }
}

// =============== CARRITO (versión servidor) ===============
let cart = [];

function parsePriceStringGlobal(s) {
  if (s === undefined || s === null) return 0;
  let t = s.toString().trim();
  if (!t) return 0;
  t = t.replace(/[^0-9.,-]/g, '').trim();
  if (t === '') return 0;
  if (t.indexOf('.') !== -1 && t.indexOf(',') !== -1) {
    t = t.replace(/\./g, '');
    t = t.replace(/,/g, '.');
  } else if (t.indexOf(',') !== -1 && t.indexOf('.') === -1) {
    t = t.replace(/,/g, '.');
  } else {
    t = t.replace(/[^0-9.\-]/g, '');
  }
  const n = parseFloat(t);
  return Number.isFinite(n) ? n : 0;
}

function getCSRFToken() {
  const name = 'csrftoken=';
  const cookies = document.cookie ? document.cookie.split(';') : [];
  for (let c of cookies) {
    c = c.trim();
    if (c.startsWith(name)) return c.substring(name.length);
  }
  return '';
}

async function fetchCartJSON() {
  const res = await fetch('/carrito/json', { credentials: 'same-origin' });
  if (!res.ok) throw new Error('No se pudo obtener el carrito');
  return res.json();
}

async function postForm(url, payload) {
  const fd = new FormData();
  Object.entries(payload || {}).forEach(([k, v]) => fd.append(k, v));
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCSRFToken() },
    body: fd,
    credentials: 'same-origin'
  });
  if (!res.ok) throw new Error(`Error en ${url}`);
  return res.json();
}

function goToResumen() {
  window.location.href = '/resumen_compra';
}


// === Acciones de carrito (server) =========================================================================

async function addToCart(productName, price, productId, stock) {
  try {
    const fd = new FormData();
    fd.append('producto_id', productId);
    fd.append('cantidad', 1);
    
    const res = await fetch('/carrito/agregar', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCSRFToken() },
      body: fd,
      credentials: 'same-origin'
    });
    
    const response = await res.json();
    
    if (res.ok && response.ok) {
      showCartNotification(productName);
      await refreshCartBadge();

      try {
        const raw = localStorage.getItem('cart');
        const clientCart = raw ? JSON.parse(raw) : [];
        const priceNum = parsePriceStringGlobal(price);
        const existing = clientCart.find(it => (it.product_id && it.product_id.toString() === productId.toString()));
        if (existing) {
          existing.quantity = Number(existing.quantity || 0) + 1;
          existing.price = priceNum;
        } else {
          clientCart.push({ name: productName, price: priceNum, quantity: 1, sku: null, product_id: productId });
        }
        localStorage.setItem('cart', JSON.stringify(clientCart));
      } catch (e) {
        console.warn('Could not update localStorage cart', e);
      }
    } else {
      // Mostrar mensaje específico del servidor (stock límite, sin stock, etc.)
      showErrorNotification(response.msg || 'No se pudo agregar el producto al carrito.');
    }
  } catch (e) {
    console.warn('No se pudo agregar al carrito', e);
    showErrorNotification('Por favor, inicia sesión para agregar productos al carrito.');
  }
}

async function updateCartItem(itemId, cantidad) {
  try {
    const fd = new FormData();
    fd.append('item_id', itemId);
    fd.append('cantidad', cantidad);
    
    const res = await fetch('/carrito/actualizar', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCSRFToken() },
      body: fd,
      credentials: 'same-origin'
    });
    
    const response = await res.json();
    
    if (res.ok && response.ok) {
      await refreshCartBadge();
      const existingModal = document.getElementById('cart-modal');
      if (existingModal) await toggleCart(true);
      showSuccessNotification('Cantidad actualizada correctamente');
    } else {
      showErrorNotification(response.msg || 'No se pudo actualizar la cantidad');
    }
  } catch (e) {
    console.warn('No se pudo actualizar el item', e);
    showErrorNotification('Error al actualizar el producto en el carrito');
  }
}

async function removeCartItem(itemId) {
  try {
    const fd = new FormData();
    fd.append('item_id', itemId);
    
    const res = await fetch('/carrito/eliminar', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCSRFToken() },
      body: fd,
      credentials: 'same-origin'
    });
    
    const response = await res.json();
    
    if (res.ok && response.ok) {
      await refreshCartBadge();
      const existingModal = document.getElementById('cart-modal');
      if (existingModal) await toggleCart(true);
      showSuccessNotification('Producto eliminado del carrito');
    } else {
      showErrorNotification(response.msg || 'No se pudo eliminar el producto');
    }
  } catch (e) {
    console.warn('No se pudo eliminar el item', e);
    showErrorNotification('Error al eliminar el producto del carrito');
  }
}


async function refreshCartBadge() {
  try {
    const data = await fetchCartJSON();
    // totalItems = suma de cantidades
    const totalItems = data.items.reduce((sum, it) => sum + Number(it.cantidad || 0), 0);
    const cartCount = document.getElementById('cart-count');
    if (cartCount) cartCount.textContent = totalItems;

    const cartIcon = document.querySelector('.cart-icon');
    if (cartIcon) {
      cartIcon.style.transform = 'scale(1.2)';
      setTimeout(() => { cartIcon.style.transform = 'scale(1)'; }, 200);
    }
  } catch (e) {
  }
}

function showCartNotification(productName) {
  const notification = document.createElement('div');
  notification.innerHTML = `
    <div style="
      position: fixed; top: 100px; right: 20px;
      background: #28a745; color: white;
      padding: 15px 20px; border-radius: 8px;
      box-shadow: var(--shadow-hover); z-index: 9999;
      animation: slideInRight 0.3s ease;">
      <i class="fas fa-check-circle"></i> ${productName} añadido al carrito
    </div>`;
  document.body.appendChild(notification);
  setTimeout(() => { notification.remove(); }, 3000);
}

function showErrorNotification(message) {
  const notification = document.createElement('div');
  notification.innerHTML = `
    <div style="
      position: fixed; top: 100px; right: 20px;
      background: #dc3545; color: white;
      padding: 15px 20px; border-radius: 8px;
      box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3); z-index: 9999;
      animation: slideInRight 0.3s ease;">
      <i class="fas fa-exclamation-circle"></i> ${message}
    </div>`;
  document.body.appendChild(notification);
  setTimeout(() => { notification.remove(); }, 4000);
}

function showSuccessNotification(message) {
  const notification = document.createElement('div');
  notification.innerHTML = `
    <div style="
      position: fixed; top: 100px; right: 20px;
      background: #28a745; color: white;
      padding: 15px 20px; border-radius: 8px;
      box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3); z-index: 9999;
      animation: slideInRight 0.3s ease;">
      <i class="fas fa-check-circle"></i> ${message}
    </div>`;
  document.body.appendChild(notification);
  setTimeout(() => { notification.remove(); }, 3000);
}

function showWarningNotification(message) {
  const notification = document.createElement('div');
  notification.innerHTML = `
    <div style="
      position: fixed; top: 100px; right: 20px;
      background: #ffc107; color: #000;
      padding: 15px 20px; border-radius: 8px;
      box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3); z-index: 9999;
      animation: slideInRight 0.3s ease;">
      <i class="fas fa-exclamation-triangle"></i> ${message}
    </div>`;
  document.body.appendChild(notification);
  setTimeout(() => { notification.remove(); }, 3500);
}

async function toggleCart(forceOpen = false) {
  const existingModal = document.getElementById('cart-modal');
  if (existingModal && !forceOpen) {
    existingModal.remove();
    return;
  }

  // Trae el carrito del servidor
  let data;
  try {
    data = await fetchCartJSON();
  } catch (e) {
    showErrorNotification('No se pudo cargar el carrito. Por favor, inicia sesión.');
    return;
  }

  const items = data.items || [];
  if (items.length === 0) {
    showWarningNotification('Tu carrito está vacío 🛒');
    if (existingModal) existingModal.remove();
    return;
  }

  // cache local solo para optimizar render
  cart = items.map(it => ({
    item_id: it.item_id,
    name: it.nombre,
    price: Number(it.precio),
    quantity: Number(it.cantidad),
    producto_id: it.producto_id
  }));

  let total = 0;
  let cartHTML = `
    <h3 style="font-size:1.4rem; font-weight:700; margin-bottom:1rem;">🛒 Carrito de Compras</h3>
    <div style="max-height: 360px; overflow-y: auto; border-bottom: 1px solid #ddd; padding-bottom: 1rem;">`;

  cart.forEach((item) => {
    const itemTotal = item.price * item.quantity;
    total += itemTotal;
    cartHTML += `
      <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px dashed #e0e0e0;">
        <div style="flex:1;">
          <div style="font-weight:600;">${item.name}</div>
          <div style="font-size:0.9rem; color:#666;">$${item.price.toLocaleString()} × ${item.quantity}</div>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <button onclick="updateCartItem(${item.item_id}, ${Math.max(1, item.quantity - 1)})"
            style="padding:4px 8px; border:1px solid #ccc; background:#f8f8f8; border-radius:4px; cursor:pointer;">−</button>
          <span>${item.quantity}</span>
          <button onclick="updateCartItem(${item.item_id}, ${item.quantity + 1})"
            style="padding:4px 8px; border:1px solid #ccc; background:#f8f8f8; border-radius:4px; cursor:pointer;">+</button>
          <strong style="width:80px; text-align:right;">$${itemTotal.toLocaleString()}</strong>
          <button onclick="removeCartItem(${item.item_id})"
            style="background:#dc3545; color:white; border:none; border-radius:6px; padding:6px 8px; cursor:pointer;">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>`;
  });

  cartHTML += `
    </div>
    <div style="margin-top:1.2rem; text-align:right; font-size:1.2rem; font-weight:600;">
      Total: <span style="color:#0d6efd;">$${(data.total || total).toLocaleString()}</span>
    </div>

    <div style="display:flex; justify-content:center; gap:12px; margin-top:1.5rem; flex-wrap:wrap;">
      <button onclick="window.location.href='${carritoURL}'"
        style="background:#6c757d; color:white; border:none; border-radius:8px; padding:10px 22px; font-weight:600; cursor:pointer;">
        Ver Carrito Completo
      </button>

      <button onclick="goToResumen()"
        style="background:#0d6efd; color:white; border:none; border-radius:8px; padding:10px 22px; font-weight:600; cursor:pointer;">
        Proceder al Pago
      </button>
    </div>
  `;

  const modal = document.createElement('div');
  modal.id = "cart-modal";
  modal.innerHTML = `
    <div style="
      position: fixed; top:0; left:0; right:0; bottom:0;
      background: rgba(0,0,0,0.45);
      display:flex; align-items:center; justify-content:center;
      z-index:10000;
      animation: fadeInCart 0.25s ease;
    " onclick="this.remove()">
      <div style="
        background:white;
        padding:30px 25px;
        border-radius:16px;
        max-width:520px;
        width:90%;
        position:relative;
        box-shadow:0 10px 25px rgba(0,0,0,0.2);
        animation: slideUpCart 0.3s ease;
      " onclick="event.stopPropagation()">
        <button onclick="this.closest('#cart-modal').remove()" style="
          position:absolute; top:12px; right:15px;
          background:none; border:none; font-size:1.6rem; color:#333; cursor:pointer;">×</button>
        ${cartHTML}
      </div>
    </div>`;

  if (existingModal) existingModal.replaceWith(modal);
  else document.body.appendChild(modal);
}


function removeFromCart(indexOrItemId) {
  const itemId = (cart[indexOrItemId] && cart[indexOrItemId].item_id) || indexOrItemId;
  return removeCartItem(itemId);
}

function saveCart() {}

async function updateCartCount() { await refreshCartBadge(); }

// =============== USUARIO MENU ===============
function toggleUserMenu() {
    const dropdown = document.getElementById('user-dropdown');
    dropdown.classList.toggle('show');
    isUserMenuOpen = !isUserMenuOpen;
}
document.addEventListener('click', function (event) {
    const userIcon = document.querySelector('.user-icon');
    const dropdown = document.getElementById('user-dropdown');
    if (userIcon && !userIcon.contains(event.target) && isUserMenuOpen) {
        dropdown.classList.remove('show'); isUserMenuOpen = false;
    }
});

// =============== SCROLL SUAVE ===============
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});


// =============== OBSERVER ANIMACIONES ===============
const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -100px 0px' };
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);
document.querySelectorAll('.offer-card, .product-card').forEach(card => {
    card.style.opacity = '0'; card.style.transform = 'translateY(30px)';
    card.style.transition = 'all 0.6s ease'; observer.observe(card);
});

// =============== LOADING ===============
document.addEventListener("DOMContentLoaded", () => {
    updateCartCount();
    if (document.getElementById("cart-page")) renderCartPage();
    const products = JSON.parse(localStorage.getItem("products")) || [];
    const container = document.getElementById("products");
    if (container) {
        container.innerHTML = "";
        products.forEach(p => {
            container.innerHTML += `
              <div class="col-sm-6 col-md-4 col-lg-3">
                <div class="card h-100 shadow-sm border-0">
                  <img src="${p.image}" class="card-img-top" alt="${p.name}" style="height:200px; object-fit:cover;">
                  <div class="card-body text-center">
                    <h5 class="card-title">${p.name}</h5>
                    <p class="card-text small">${p.description}</p>
                    <div class="fw-bold mb-3">$${p.price.toLocaleString()}</div>
                    <div class="mb-2">Stock disponible: ${p.stock}</div>
                    <button class="btn btn-primary mb-2"
                        onclick="showProductDetail('${p.name}', '${p.description}', ${p.price}, '${p.image}')">
                        Ver Detalle
                    </button>
                    <button class="btn btn-danger w-100"
                        onclick="addToCart('${p.name}', ${p.price})">
                        <i class="fas fa-shopping-cart me-2"></i>Añadir al Carrito
                    </button>
                  </div>
                </div>
              </div>`;
        });
    }
});
window.addEventListener('load', function () { document.body.style.animation = 'fadeIn 0.5s ease forwards'; });

// =============== RENDER CARRITO EN PÁGINA ===============
function renderCartPage() {
    const container = document.getElementById("cart-page");
    if (!container) return;

    container.innerHTML = "";
    if (cart.length === 0) {
        container.innerHTML = "<p style='text-align:center; font-size:1.1rem;'>Tu carrito está vacío 🛒</p>";
        return;
    }

    let total = 0;
    cart.forEach((item, index) => {
        const subtotal = item.price * item.quantity;
        total += subtotal;
        container.innerHTML += `
            <div class="cart-item">
                <div>
                    <strong>${item.name}</strong><br>
                    <small>${item.quantity} × $${item.price.toLocaleString()}</small>
                </div>
                <div>
                    <b>$${subtotal.toLocaleString()}</b>
                    <button class="remove-btn" data-index="${index}">❌</button>
                </div>
            </div>
        `;
    });

    container.innerHTML += `
        <h3>Total: $${total.toLocaleString()}</h3>
        <div class="cart-actions">
            <button onclick="goToResumen();">Proceder al Pago</button>
            <button onclick="goToProductos();">Seguir Comprando</button>
        </div>
    `;
}

function goToResumen() {
    try {
        const url = window.resumenURL || '/resumen_compra';
        window.location.href = url;
    } catch (e) {
        window.location.href = '/resumen_compra';
    }
}

function goToProductos() {
    try {
        const url = window.productosURL || '/productos';
        window.location.href = url;
    } catch (e) {
        window.location.href = '/productos';
    }
}

document.addEventListener("click", function (e) {
    if (e.target.classList.contains("remove-btn")) {
        const index = e.target.getAttribute("data-index");
        removeFromCart(index);
        renderCartPage();
    }
});

// =============== PRODUCTO DETALLE ===============
function showProductDetail(name, description, price, image) {
    const modal = document.createElement('div');
    modal.innerHTML = `
    <div style="position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.6);
        display:flex; align-items:center; justify-content:center; z-index:10000;" onclick="this.remove()">
        <div style="background:white; padding:30px; border-radius:12px; max-width:500px; width:90%; position:relative;"
             onclick="event.stopPropagation()">
            <button onclick="this.closest('div').parentElement.remove()" style="
                position:absolute; top:10px; right:10px; font-size:1.5rem; border:none; background:none; cursor:pointer;">×</button>
            <img src="${image}" alt="${name}" style="width:100%; border-radius:8px; margin-bottom:15px;">
            <h3>${name}</h3>
            <p>${description}</p>
            <h4>$${price.toLocaleString()}</h4>
            <button class="btn btn-danger w-100"
                onclick="addToCart('${name}', ${price}); this.closest('div').parentElement.remove()">
                <i class="fas fa-shopping-cart me-2"></i>Añadir al Carrito
            </button>
        </div>
    </div>`;
    document.body.appendChild(modal);
}

function showProductDetailFromButton(btn) {
  if (!btn) return;
  const name = btn.getAttribute('data-name') || '';
  const description = btn.getAttribute('data-description') || '';
  const rawPrice = (btn.getAttribute('data-price') || '').toString().trim();
  const image = btn.getAttribute('data-image') || '';

  function parsePriceString(s) {
    if (!s) return 0;
    let t = s.replace(/[^0-9.,-]/g, '').trim();
    if (t === '') return 0;

    if (t.indexOf('.') !== -1 && t.indexOf(',') !== -1) {
      t = t.replace(/\./g, '');
      t = t.replace(/,/g, '.');
    } else if (t.indexOf(',') !== -1 && t.indexOf('.') === -1) {
      t = t.replace(/,/g, '.');
    } else {
      t = t.replace(/[^0-9.\-]/g, '');
    }

    const n = parseFloat(t);
    return Number.isFinite(n) ? n : 0;
  }

  const price = parsePriceString(rawPrice);

  try {
    showProductDetail(name, description, price, image);
  } catch (e) {
    console.warn('Error showing product detail', e);
  }
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
  @keyframes slideInRight {
    from {
      transform: translateX(400px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  @keyframes fadeInCart {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  @keyframes slideUpCart {
    from {
      transform: translateY(50px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }
`;
document.head.appendChild(style);