// =============== VARIABLES GLOBALES ===============
let currentSlide = 0;
const totalSlides = 3;
let cart = JSON.parse(localStorage.getItem("cart")) || [];
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

// =============== CARRITO ===============
function addToCart(productName, price) {
    let products = JSON.parse(localStorage.getItem("products")) || [];
    const product = products.find(p => p.name === productName);
    if (!product) { alert("Producto no encontrado"); return; }

    const existingItem = cart.find(item => item.name === productName);

    if (existingItem) {
        if (existingItem.quantity < product.stock) {
            existingItem.quantity += 1;
        } else {
            alert(`Solo hay ${product.stock} unidades disponibles de ${productName}`);
            return;
        }
    } else {
        if (product.stock > 0) {
            cart.push({
                name: productName,
                price: price,
                quantity: 1,
                stock: product.stock
            });
        } else {
            alert(`No hay stock disponible para ${productName}`);
            return;
        }
    }

    updateCartCount();
    saveCart();
    showCartNotification(productName);
}

function updateCartCount() {
    const cartCount = document.getElementById('cart-count');
    if (!cartCount) return;
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCount.textContent = totalItems;
    const cartIcon = document.querySelector('.cart-icon');
    if (cartIcon) {
        cartIcon.style.transform = 'scale(1.2)';
        setTimeout(() => { cartIcon.style.transform = 'scale(1)'; }, 200);
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

function toggleCart() {
    if (cart.length === 0) { alert('Tu carrito está vacío'); return; }
    let cartHTML = '<h3>Carrito de Compras</h3><div style="max-height: 400px; overflow-y: auto;">';
    let total = 0;
    cart.forEach((item, index) => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        cartHTML += `
            <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid #eee;">
                <div>
                    <strong>${item.name}</strong><br>
                    <small>${item.price.toLocaleString()} x ${item.quantity} (Stock: ${item.stock})</small>
                </div>
                <div>
                    <strong>${itemTotal.toLocaleString()}</strong>
                    <button class="remove-btn" data-index="${index}" style="
                        margin-left: 10px; background: var(--accent-red); color: white;
                        border: none; border-radius: 4px; padding: 4px 8px; cursor: pointer;">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>`;
    });
    cartHTML += `
    </div>
    <div style="margin-top:20px; padding-top:20px; border-top:2px solid var(--primary-dark); text-align:center;">
        <h4>Total: ${total.toLocaleString()}</h4>
        <div style="display:flex; justify-content:center; gap:10px; flex-wrap:wrap;">
            <button onclick="goToResumen()" style="
                background: var(--primary-dark); color: white; border: none;
                padding: 12px 30px; border-radius: 8px; font-weight: bold; cursor: pointer;">
                Proceder al Pago
            </button>
            <button onclick="window.location.href=carritoURL" style="
                background: var(--primary-dark); color: white; border: none;
                padding: 12px 30px; border-radius: 8px; font-weight: bold; cursor: pointer;">
                <i class="fas fa-shopping-cart"></i> Ver Carrito
            </button>
        </div>
    </div>`;
    const modal = document.createElement('div');
    modal.innerHTML = `
        <div style="position: fixed; top:0; left:0; right:0; bottom:0; background: rgba(0,0,0,0.5);
            display:flex; align-items:center; justify-content:center; z-index:10000;" onclick="this.remove()">
            <div style="background:white; padding:30px; border-radius:12px; max-width:500px; width:90%;
                max-height:80vh; overflow-y:auto; position:relative;" onclick="event.stopPropagation()">
                <button onclick="this.closest('div').parentElement.remove()" style="
                    position:absolute; top:15px; right:15px; background:none; border:none; font-size:1.5rem; cursor:pointer;">×</button>
                ${cartHTML}
            </div>
        </div>`;
    document.body.appendChild(modal);
}

function removeFromCart(index) {
    cart.splice(index, 1);
    saveCart(); updateCartCount();
    const backdrop = document.querySelector('[style*="position: fixed"][style*="background: rgba(0,0,0,0.5)"]');
    if (backdrop) backdrop.remove();
    if (cart.length > 0) toggleCart();
}

function checkout() {
    let products = JSON.parse(localStorage.getItem("products")) || [];
    cart.forEach(item => {
        const prod = products.find(p => p.name === item.name);
        if (prod) { prod.stock -= item.quantity; if (prod.stock < 0) prod.stock = 0; }
    });
    localStorage.setItem("products", JSON.stringify(products));
    alert('Compra realizada con éxito 🎉');
    cart = []; saveCart(); updateCartCount();
    const backdrop = document.querySelector('[style*="position: fixed"][style*="background: rgba(0,0,0,0.5)"]');
    if (backdrop) backdrop.remove();
}

function saveCart() { localStorage.setItem("cart", JSON.stringify(cart)); }

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

// =============== EFFECTO SCROLL NAVBAR ===============
window.addEventListener('scroll', function () {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;
    if (window.scrollY > 100) {
        navbar.style.background = 'linear-gradient(135deg, rgba(6, 43, 97, 0.95), rgba(0, 51, 153, 0.95))';
        navbar.style.backdropFilter = 'blur(10px)';
    } else {
        navbar.style.background = 'linear-gradient(135deg, var(--primary-dark), var(--primary-medium))';
        navbar.style.backdropFilter = 'none';
    }
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
            <button onclick="window.location.href='{% url 'productos' %}'">Seguir Comprando</button>
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

// ✅ Delegación de eventos para los botones ❌
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
