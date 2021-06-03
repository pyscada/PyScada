django.jQuery(
 function($) {
    $(".js-inline-admin-formset.inline-group").hide();
    v = $(".form-row.field-device .readonly").text();
    $("[id^='" + v + "'].js-inline-admin-formset.inline-group").show();
    $("#id_device").on('change', function() {
      value = $("#id_device :selected").text().split("-")[0]
      $("[id^='" + value + "variable'].js-inline-admin-formset.inline-group").show();
      $(".js-inline-admin-formset.inline-group").not("[id^='" + value + "']").hide();
    })
  }
);
