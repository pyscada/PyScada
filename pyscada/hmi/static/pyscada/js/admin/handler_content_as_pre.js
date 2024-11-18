function handlerContentAsPre() {
  document.querySelectorAll(".form-row.field-content .flex-container .readonly").forEach((e) => {e.style.whiteSpace = "pre"; e.style.fontFamily = "monospace";});
};

document.addEventListener("DOMContentLoaded", function () {handlerContentAsPre();});
