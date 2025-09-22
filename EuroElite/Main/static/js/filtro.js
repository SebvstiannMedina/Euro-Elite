// 🔍 Buscar productos por texto
function searchProducts() {
  let input = document.getElementById("searchInput").value.toLowerCase();
  let products = document.querySelectorAll(".product-card");

  products.forEach(product => {
    let title = product.querySelector(".product-title").textContent.toLowerCase();
    let description = product.querySelector(".product-description").textContent.toLowerCase();
    if (title.includes(input) || description.includes(input)) {
      product.style.display = "";
    } else {
      product.style.display = "none";
    }
  });
}

// 🎯 Filtrar por categoría (usa slug)
function filterProducts() {
  let category = document.getElementById("categoryFilter").value.toLowerCase();
  let products = document.querySelectorAll(".product-card");

  products.forEach(product => {
    let productCategory = product.getAttribute("data-category")?.toLowerCase();
    if (category === "all" || productCategory === category) {
      product.style.display = "";
    } else {
      product.style.display = "none";
    }
  });
}
