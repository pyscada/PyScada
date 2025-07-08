document.addEventListener("DOMContentLoaded", function () {
    display_inline_protocols_device();
    document.querySelector("#id_protocol").onchange = function() {
      display_inline_protocols_device();
    };
});

function display_inline_protocols_device() {
    document.querySelectorAll(".js-inline-admin-formset.inline-group").forEach((e) => {
        if (!e.id.includes("devicehandlerparameter_set")) {
            e.style.display = "none";
        }
    });
    v = document.querySelector("#id_protocol").options[document.querySelector("#id_protocol").selectedIndex].text;
    document.querySelectorAll("[id^='" + v + "'].js-inline-admin-formset.inline-group").forEach((e) => {
        e.style.display = "";
    });
};