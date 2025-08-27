$(document).ready(function () {
  // Inicializar Owl Carousel
  $(".custom-carousel").owlCarousel({
    loop: true,
    margin: 10,
    nav: true,
    dots: true,
    autoplay: true,
    autoplayTimeout: 5000,
    responsive: {
      0: { items: 1 },
      600: { items: 2 },
      1000: { items: 3 }
    }
  });

  // Click en los items del carrusel
  $(".custom-carousel .item").click(function () {
    $(".custom-carousel .item").not($(this)).removeClass("selected");
    $(this).toggleClass("selected");
  });

  // Toggle menú hamburguesa (opcional si tu navbar lo usa)
  $("#navbar-toggle").click(function () {
    $("#navbar-menu").toggleClass("show");
  });
});
