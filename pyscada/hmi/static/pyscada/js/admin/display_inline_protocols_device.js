django.jQuery(
 function($) {
    $(".js-inline-admin-formset.inline-group").hide();
    v = $(".form-row.field-protocol .readonly").text();
    $("[id^='" + v + "'].js-inline-admin-formset.inline-group").show();
    $("#id_protocol").on('change', function() {
      value = $("#id_protocol :selected").text()
      $("[id^='" + value + "'].js-inline-admin-formset.inline-group").show();
      $(".js-inline-admin-formset.inline-group").not("[id^='" + value + "']").hide();
    })
  }
);
