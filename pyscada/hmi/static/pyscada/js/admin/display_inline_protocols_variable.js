document.addEventListener("DOMContentLoaded", function () {
    display_inline_protocols_variable();
    document.querySelector("#id_device").onchange = function() {
      display_inline_protocols_variable();
    };
});

function display_inline_protocols_variable() {
    document.querySelectorAll(".js-inline-admin-formset.inline-group").forEach((e) => {
        if (!e.id.includes("variablehandlerparameter_set")) {
            e.style.display = "none";
        }
    });
    v = document.querySelector("#id_device").options[document.querySelector("#id_device").selectedIndex].text.split("-")[0];
    document.querySelectorAll("[id^='" + v + "'].js-inline-admin-formset.inline-group").forEach((e) => {
        e.style.display = "";
    });
};