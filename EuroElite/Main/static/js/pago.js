// jQuery time
var current_fs, next_fs, previous_fs; // fieldsets
var left, opacity, scale; // fieldset properties
var animating; // flag to prevent quick multi-click glitches

$(".next").click(function(){
	if(animating) return false;
	animating = true;
	
	current_fs = $(this).parent();
	next_fs = $(this).parent().next();
	
	// activar siguiente paso en progressbar
	$("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");
	
	// mostrar el siguiente fieldset
	next_fs.show(); 
	// ocultar el actual con animación
	current_fs.animate({opacity: 0}, {
		step: function(now, mx) {
			scale = 1 - (1 - now) * 0.2; // escala
			left = (now * 50)+"%";       // desplazamiento
			opacity = 1 - now;           // opacidad

			current_fs.css({
				'transform': 'scale('+scale+')',
				'position': 'absolute'
			});
			next_fs.css({'left': left, 'opacity': opacity});
		}, 
		duration: 800, 
		complete: function(){
			current_fs.hide();
			next_fs.css({"position":"relative"}); // ✅ fix para footer
			animating = false;
		}, 
		easing: 'easeInOutBack'
	});
});

$(".previous").click(function(){
	if(animating) return false;
	animating = true;
	
	current_fs = $(this).parent();
	previous_fs = $(this).parent().prev();
	
	// desactivar paso actual en progressbar
	$("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");
	
	// mostrar fieldset anterior
	previous_fs.show(); 
	// ocultar el actual con animación
	current_fs.animate({opacity: 0}, {
		step: function(now, mx) {
			scale = 0.8 + (1 - now) * 0.2;
			left = ((1-now) * 50)+"%";
			opacity = 1 - now;

			current_fs.css({'left': left});
			previous_fs.css({'transform': 'scale('+scale+')', 'opacity': opacity});
		}, 
		duration: 800, 
		complete: function(){
			current_fs.hide();
			previous_fs.css({"position":"relative"}); // ✅ fix para footer
			animating = false;
		}, 
		easing: 'easeInOutBack'
	});
});

$(".submit").click(function(e){
	e.preventDefault();

	// Validación simple de tarjeta
	let nroTarjeta = $("input[name='nrotarjeta']").val();

	if(nroTarjeta.trim() === ""){
		alert("⚠️ Ingresa un número de tarjeta válido");
		return;
	}

	// Simulación de pago exitoso
	alert("✅ Pago realizado con éxito (simulación).");

	// Ocultar formulario y mostrar mensaje final
	$("#msform").fadeOut(500, function(){
		$("body").append(`
			<div class="text-center mt-5">
				<h2>¡Gracias por tu compra!</h2>
				<p>Tu pago fue procesado correctamente.</p>
			</div>
		`);
	});
});
