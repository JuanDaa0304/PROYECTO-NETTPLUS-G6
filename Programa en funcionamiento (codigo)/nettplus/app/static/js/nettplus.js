// Comportamiento de la carga de archivo: muestra el nombre elegido y permite arrastrar y soltar.
(function () {
    var zona = document.getElementById("zona-carga");
    var input = document.getElementById("archivo");
    var etiqueta = document.getElementById("archivo-elegido");
    if (!zona || !input) return;

    function mostrar() {
        etiqueta.textContent = input.files.length ? "Archivo listo: " + input.files[0].name : "";
    }
    input.addEventListener("change", mostrar);

    ["dragenter", "dragover"].forEach(function (ev) {
        zona.addEventListener(ev, function (e) { e.preventDefault(); zona.classList.add("arrastrando"); });
    });
    ["dragleave", "drop"].forEach(function (ev) {
        zona.addEventListener(ev, function (e) { e.preventDefault(); zona.classList.remove("arrastrando"); });
    });
    zona.addEventListener("drop", function (e) {
        if (e.dataTransfer.files.length) { input.files = e.dataTransfer.files; mostrar(); }
    });
})();
