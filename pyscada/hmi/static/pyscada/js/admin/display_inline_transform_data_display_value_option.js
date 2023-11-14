function updateTransformDataInlines() {
  document.querySelectorAll("div[id^='transformdata'].js-inline-admin-formset.inline-group").forEach((e) => {e.hidden = true;});  // hide all transform data inlines
  var v = document.querySelector("#id_transform_data").selectedOptions[0].innerHTML;  // get the selected transform data name
  document.querySelectorAll("[id='transformdata" + v.toLowerCase() + "-group'].js-inline-admin-formset.inline-group").forEach((e) => {e.hidden = false;});  // show the correct transform data inline
    document.querySelector("#id_transform_data").onchange = function(e) {
      document.querySelectorAll("div[id^='transformdata'].js-inline-admin-formset.inline-group").forEach((e) => {e.hidden = true;});  // hide all transform data inlines
      var v = e.target.selectedOptions[0].innerHTML;  // get the selected transform data name
      document.querySelectorAll("[id='transformdata" + v.toLowerCase() + "-group'].js-inline-admin-formset.inline-group").forEach((e) => {e.hidden = false;});  // show the correct transform data inline
    };
  };
  document.addEventListener("DOMContentLoaded", function () {updateTransformDataInlines();});
