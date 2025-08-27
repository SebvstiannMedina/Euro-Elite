document.addEventListener("DOMContentLoaded", () => {
  const boton = document.getElementById("boton");
  const titulo = document.getElementById("titulo");

  boton.addEventListener("click", () => {
    titulo.innerText = "¡Seba pagame! 🎉";
    titulo.style.color = "green";
  });
});
