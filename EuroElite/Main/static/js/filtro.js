// 🔍 Buscar productos por texto
function searchProducts() {
  let input = document.getElementById("searchInput").value.toLowerCase();
  let products = document.querySelectorAll(".product-card");

  products.forEach(product => {
    let title = product.querySelector(".product-title").textContent.toLowerCase();
    let description = product.querySelector(".product-description").textContent.toLowerCase();
    if (title.includes(input) || description.includes(input)) {
      product.style.display = "block";
    } else {
      product.style.display = "none";
    }
  });
}

// 🎯 Filtrar por categoría
function filterProducts() {
  let category = document.getElementById("categoryFilter").value;
  let products = document.querySelectorAll(".product-card");

  products.forEach(product => {
    let productCategory = product.getAttribute("data-category");
    if (category === "all" || productCategory === category) {
      product.style.display = "block";
    } else {
      product.style.display = "none";
    }
  });
}
