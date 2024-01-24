function updateTransformDataInlines() {
  document.querySelectorAll("div[id$='-group'].js-inline-admin-formset.inline-group").forEach((e) => {e.hidden = true;});  // hide all datasource inlines
  if (document.querySelector("#id_datasource_model") != null) {
    var v = document.querySelector("#id_datasource_model").selectedOptions[0].dataset.inlineDatasourceModelName;  // get the selected datasource model name
    document.querySelectorAll("[id='" + v.toLowerCase() + "-group'].js-inline-admin-formset.inline-group").forEach((e) => {e.hidden = false;});  // show the correct transform data inline

    document.querySelector("#id_datasource_model").onchange = function(e) {
        document.querySelectorAll("div[id$='-group'].js-inline-admin-formset.inline-group").forEach((e) => {e.hidden = true;});  // hide all datasource inlines
        var v = e.target.selectedOptions[0].dataset.inlineDatasourceModelName;  // get the selected transform data name
        document.querySelectorAll("[id='" + v.toLowerCase() + "-group'].js-inline-admin-formset.inline-group").forEach((e) => {e.hidden = false;});  // show the correct transform data inline
    };
  };
};

  document.addEventListener("DOMContentLoaded", function () {updateTransformDataInlines();});