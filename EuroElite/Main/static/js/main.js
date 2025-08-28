$(document).ready(function () {
  // --- Slick (protegido) ---
  if ($.fn.slick && $('.carousel').length) {
    $('.carousel').slick({
      dots: true,
      infinite: true,
      speed: 500,
      slidesToShow: 1,
      adaptiveHeight: true,
      autoplay: true,
      autoplaySpeed: 3000
    });
  } else {
    console.warn('Slick no encontrado o .carousel no existe; se omite la inicialización.');
  }

  // --- Navbar ---
  $('#navbar-toggle').on('click', function (e) {
    e.preventDefault();
    e.stopPropagation();

    const $menu = $('#navbar-menu');
    const $icon = $(this).find('i');

    $menu.toggleClass('active');
    $(this).toggleClass('active');

    if ($menu.hasClass('active')) {
      $icon.removeClass('fa-bars').addClass('fa-xmark'); // FA6
    } else {
      $icon.removeClass('fa-xmark').addClass('fa-bars');
    }
  });

  $('.navbar-menu a').on('click', function () {
    if ($(window).width() <= 768) closeMenu();
  });

  $(document).on('click', function (e) {
    if (!$(e.target).closest('.navbar').length && $(window).width() <= 768) {
      if ($('#navbar-menu').hasClass('active')) closeMenu();
    }
  });

  $('.navbar').on('click', function (e) { e.stopPropagation(); });

  $(window).on('resize', function () {
    if ($(window).width() > 768) closeMenu();
  });

  $(document).on('keydown', function (e) {
    if (e.key === 'Escape' && $('#navbar-menu').hasClass('active')) closeMenu();
  });

  $(window).on('scroll', function () {
    $('.navbar').toggleClass('scrolled', $(this).scrollTop() > 100);
  });

  function closeMenu() {
    $('#navbar-menu').removeClass('active');
    $('#navbar-toggle').removeClass('active')
      .find('i').removeClass('fa-xmark').addClass('fa-bars');
  }

  // Debug útil
  if (!window.jQuery) console.error('jQuery NO cargó');
  if (!$('#navbar-toggle').length) console.error('#navbar-toggle no encontrado');
  if (!$('#navbar-menu').length) console.error('#navbar-menu no encontrado');
});

// Variables del carousel moderno
    let modernCurrentSlide = 0;
    const modernTotalSlides = 5;
    const modernTrack = document.getElementById('modernCarouselTrack');
    const modernSlides = document.querySelectorAll('.modern-carousel-slide');
    const modernDots = document.querySelectorAll('.modern-nav-dot');
    let modernAutoSlideInterval;

    function modernUpdateCarousel() {
      // Mover el track
      modernTrack.style.transform = `translateX(-${modernCurrentSlide * 20}%)`;
      
      // Actualizar clases activas
      modernSlides.forEach((slide, index) => {
        slide.classList.toggle('active', index === modernCurrentSlide);
      });
      
      modernDots.forEach((dot, index) => {
        dot.classList.toggle('active', index === modernCurrentSlide);
      });
    }

    function modernChangeSlide(direction) {
      modernCurrentSlide += direction;
      
      if (modernCurrentSlide >= modernTotalSlides) {
        modernCurrentSlide = 0;
      } else if (modernCurrentSlide < 0) {
        modernCurrentSlide = modernTotalSlides - 1;
      }
      
      modernUpdateCarousel();
      modernResetAutoSlide();
    }

    function modernGoToSlide(slideIndex) {
      modernCurrentSlide = slideIndex;
      modernUpdateCarousel();
      modernResetAutoSlide();
    }

    function modernStartAutoSlide() {
      modernAutoSlideInterval = setInterval(() => {
        modernChangeSlide(1);
      }, 6000);
    }

    function modernResetAutoSlide() {
      clearInterval(modernAutoSlideInterval);
      modernStartAutoSlide();
    }

    // Eventos de teclado para el carousel moderno
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') {
        modernChangeSlide(-1);
      } else if (e.key === 'ArrowRight') {
        modernChangeSlide(1);
      }
    });

    // Eventos táctiles para móvil
    let modernStartX = 0;
    let modernEndX = 0;

    modernTrack.addEventListener('touchstart', (e) => {
      modernStartX = e.touches[0].clientX;
    });

    modernTrack.addEventListener('touchend', (e) => {
      modernEndX = e.changedTouches[0].clientX;
      modernHandleSwipe();
    });

    function modernHandleSwipe() {
      const threshold = 50;
      const diff = modernStartX - modernEndX;
      
      if (Math.abs(diff) > threshold) {
        if (diff > 0) {
          modernChangeSlide(1); // Swipe izquierda
        } else {
          modernChangeSlide(-1); // Swipe derecha
        }
      }
    }

    // Pausar auto-slide al hacer hover
    const modernContainer = document.querySelector('.modern-carousel-container');
    modernContainer.addEventListener('mouseenter', () => {
      clearInterval(modernAutoSlideInterval);
    });

    modernContainer.addEventListener('mouseleave', () => {
      modernStartAutoSlide();
    });

    // Iniciar el carousel moderno
    modernStartAutoSlide();