/* Javascript library for the PyScada web client based on jquery and flot,

version 0.7.1rc5

Copyright (c) 2013-2019 Martin Schröder, Camille Lavayssière
Licensed under the GPL.

*/



//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

//                                                      VARIABLES

//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

/**
 * Script's version
 * @type {string}
 */
 var version = "0.7.1rc5";

 /**
  * Date format : day/month/year hours:minutes:seconds
  * @type {string}
  */
 var daterange_format = "DD/MM/YYYY HH:mm:ss";

 //                             -----------------------------------------------------------
 //                                             Client-Server's Variables
 //                             -----------------------------------------------------------
 /**
  * Loading page state - 0 = not loaded / 1 = loaded
  * @type {boolean}
  */
 var LOADING_PAGE_DONE = 0;
 /**
  * ???
  */
 var debug = 0;


 // Loadings :
 /**
  * Loading percentage
  * @type {number}
  */
 var loading_percent = 0;

 /**
  * All recorded loading states
  * @type {number}
  */
 var loading_states = {};

 /**
  * Current loading state
  * @type {string}
  */
 var loading_labels = {0:'CSS: ', 1:'Loading javascript: ', 4:'Loading static variables: ', 5:'Loading chart variables: ',};

 // Ajax :
 /**
  * Count of all the JSON errors - used for errors notification.
  * @type {number}
  */
 var JSON_ERROR_COUNT = 0;

 /**
  * Current server time
  * @type {number}
  */
 var SERVER_TIME = 0;

 /**
  * Last recorded query time
  * @type {number}
  */
 var LAST_QUERY_TIME = 0;

 /**
  * Token used for the ajax setup
  * @type {string}
  */
 var CSRFTOKEN = $.cookie('csrftoken');

 /**
  * Refresh rate in milliseconds - used to update data
  * @type {number}
  */
 var REFRESH_RATE = 2500;

 /**
  * Cache timeout in milliseconds
  * @type {number}
  */
 var CACHE_TIMEOUT = 15000;

 /**
  * Root's url - used to locate pyscada elements
  * @type {string}
  */
 var ROOT_URL = window.location.protocol+"//"+window.location.host + "/";

 // Log :
 /**
  * Log's last timestamp - Collect the data last timestamp
  * @type {number}
  */
 var LOG_LAST_TIMESTAMP = 0;

 /**
  * Count of fetching data pending
  * @type {boolean}
  */
 var LOG_FETCH_PENDING_COUNT = false;

 // Status :
 /**
  * Chart initialization status count -
  * @type {number}
  */
 var INIT_STATUS_COUNT = 0;

 /**
  * Chart update status count
  * @type {number}
  */
 var UPDATE_STATUS_COUNT = 0;

 /**
  * Auto chart's data update button status
  * @type {boolean}
  */
 var AUTO_UPDATE_ACTIVE = true;

 /**
  * Previous auto chart's data update button active
  * @type {boolean}
  */
 var PREVIOUS_AUTO_UPDATE_ACTIVE_STATE = false;

 /**
  * Last end date
  * @type {number}
  */
 var PREVIOUS_END_DATE = 0;

 // Notifications :
 /**
  * Count of all displayed notification
  * @type {number}
  */
 var NOTIFICATION_COUNT = 0;

 /**
  * Id of the 'data out of date' error notification to display
  * @type {number}
  */
 var DATA_OUT_OF_DATE_ALERT_ID = '';


  /**
  * State of the daterangepicker
  * @type {boolean}
  */
 var DATERANGEPICKER_SET = false;


 //                             -----------------------------------------------------------
 //                                                      Objects
 //                             -----------------------------------------------------------
 /**
  * Chart's variables initialization count
  * @type {number}
  */
 var INIT_CHART_VARIABLES_COUNT = 0;

 /**
  * Chart's variables initialization state
  * @type {boolean}
  */
 var INIT_CHART_VARIABLES_DONE = false;


 // List of Charts
 /**
  * List of chart's variables keys
  * @type {Array<number>}
  */
 var CHART_VARIABLE_KEYS = {count:function(){var c = 0;for (var key in this){c++;} return c-2;},keys:function(){var k = [];for (var key in this){if (key !=="keys" && key !=="count"){k.push(key);}} return k;}};

 // Plot :

 /**
  * List of all the chart to display
  * @type {Array<object>}
  */
 var PyScadaPlots = [];

 /**
  * X axe's progress bar resize function state
  * @type {boolean}
  */
 var progressbar_resize_active = false;

 /**
  * Update chart's x axes time line status
  * @type {boolean}
  */
 var UPDATE_X_AXES_TIME_LINE_STATUS = true;


 //                             -----------------------------------------------------------
 //                                                  Data's Variables
 //                             -----------------------------------------------------------

 /**
  * Holds the fetched data from the server
  * @type {Array<object>}
  */
 var DATA = {};
 /**
  * Data initialization status
  * @type {number}
  */
 var DATA_INIT_STATUS = 0;

 /**
  * Count of fetch data pending
  * @type {number}
  */
 var FETCH_DATA_PENDING = 0;

 /**
  * Variables initialization done status
  * @type {boolean}
  */
 var INIT_STATUS_VARIABLES_DONE = false;

 /**
  * Count of data fetching process
  * @type {number}
  */
 var DataFetchingProcessCount = 0;


 // Data's dates :
 /**
  * Data out of date - would be used to display an error notification
  * @type {boolean}
  */
 var DATA_OUT_OF_DATE = false;

 /**
  * Last data timestamp
  * @type {number}
  */
 var DATA_TO_TIMESTAMP = 0;

 /**
  * First data timestamp
  * @type {number}
  */
 var DATA_FROM_TIMESTAMP = 0;

 /**
  * First data timestamp to display
  * @type {number}
  */
 var DATA_DISPLAY_FROM_TIMESTAMP = -1;

 /**
  * Last data timestamp to display
  * @type {number}
  */
 var DATA_DISPLAY_TO_TIMESTAMP = -1;

 /**
  * Interval of time between the first data timestamp and the last one in milliseconds
  * @type {number}
  */
 var DATA_DISPLAY_WINDOW = 20*60*1000;

 // Data Time
 /**
  * Size of the data buffer in milliseconds
  * @type {number}
  */
 var DATA_BUFFER_SIZE = 300*60*1000;

 /**
  * Response timeout while retrieving data
  * @type {number}
  */
 var FETCH_DATA_TIMEOUT = 5000;

 // List of Datas
 /**
  * List of all the variables keys
  * @type {Array<number>}
  */
 var VARIABLE_KEYS = [];

 /**
  * List of variables property keys
  * @type {Array<number>}
  */
 var VARIABLE_PROPERTY_KEYS = [];

 /**
  * List of variable status from keys
  * @type {Array<string>}
  */
 var STATUS_VARIABLE_KEYS = {count:function(){var c = 0;for (var key in this){c++;} return c-2;},keys:function(){var k = [];for (var key in this){if (key !=="keys" && key !=="count"){k.push(key);}} return k;}};

 /**
  * List of variables properties
  * @type {Array<object>}
  */
 var VARIABLE_PROPERTIES = {};

 /**
  * List of variable data
  * @type {Array<object>}
  */
 var VARIABLE_PROPERTIES_DATA = {};

 /**
  * Historic of last modified variable properties
  * @type {Array<object>}
  */
 var VARIABLE_PROPERTIES_LAST_MODIFIED = {};

var store_temp_ajax_data = null;

 //---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 //---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

 //                                                      DATA

 //---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 //---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


 /**
  * Adding fetched data
  * @param {number} key Index used to fetch the data in 'DATA[]'
  * @param {*} value The data
  * @returns void
  */
 function add_fetched_data(key,value){

     // CHECK THE INPUT 'value' :

     if (typeof(value)==="object"){
         // check if there is values
         if (value.length >0){
             if (typeof(CHART_VARIABLE_KEYS[key]) === 'undefined'){
                 // no history needed
                 DATA[key] = [value.pop()];
                 if (DATA[key][0] < DATA_FROM_TIMESTAMP){
                     //DATA_FROM_TIMESTAMP = value[0][0];
                     UPDATE_X_AXES_TIME_LINE_STATUS = true;
                 }
             }else {
                 // if the input data is not stored, we save it
                 if (typeof(DATA[key]) == "undefined"){
                     DATA[key] = value;
                 } else {
                     // Min and Max of 'value' and DATA
                     var v_t_min = value[0][0];
                     var v_t_max = value[value.length-1][0];
                     var d_t_min = DATA[key][0][0];
                     var d_t_max = DATA[key][DATA[key].length-1][0];


                     // CHECKING 'value' and 'DATA' :

                     if (v_t_min > d_t_max){
                         // append, most likely
                         DATA[key] = DATA[key].concat(value);
                     } else if (v_t_min == d_t_max && value.length > 1){
                         // append, drop first element of value
                         DATA[key] = DATA[key].concat(value.slice(1));
                     } else if (v_t_max < d_t_min){
                         // prepend,
                         DATA[key] = value.concat(DATA[key]);
                     } else if (v_t_max == d_t_min){
                         // prepend, drop last element of value
                         DATA[key] = value.slice(0,value.length-1).concat(DATA[key]);


                     // data and value overlapping, value has older and newer elements than data, prepend and append
                     } else if (v_t_max > d_t_max && v_t_min < d_t_min){
                         // data and value overlapping, value has older and newer elements than data, prepend and append
                         start_id = find_index_sub_lte(value,DATA[key][0][0],0);
                         stop_id = find_index_sub_gte(value,DATA[key][DATA[key].length-1][0],0);
                         if (typeof(stop_id) === "number" ){
                             DATA[key] = DATA[key].concat(value.slice(stop_id));
                             if (typeof(start_id) === "number" ){
                                 DATA[key] = value.slice(0,start_id).concat(DATA[key]);
                             }else{
                                 console.log(key + ' : dropped data');
                             }
                         }else{
                             console.log(key + ' : dropped data');
                         }
                     }

                     // data and value overlapping, data has older elements than value, append
                     else if (v_t_max > d_t_min && v_t_min < d_t_min){
                         // data and value overlapping, value has older elements than data, prepend
                         stop_id = find_index_sub_lte(value,DATA[key][0][0],0);
                         if (typeof(stop_id) === "number" ){
                             DATA[key] = value.slice(0,stop_id).concat(DATA[key]);
                         }else{
                             console.log(key + ' : dropped data');
                         }
                     } else if (v_t_max > d_t_max && d_t_min < v_t_min){
                         // data and value overlapping, data has older elements than value, append
                         stop_id = find_index_sub_gte(value,DATA[key][DATA[key].length-1][0],0);
                         if (typeof(stop_id) === "number" ){
                             DATA[key] = DATA[key].concat(value.slice(stop_id));
                         }else{
                             console.log(key + ' : dropped data');
                         }
                     } else{
                         //console.log(key + ' : no new data');
                     }
                 }

                 // update x axes
                 if (value[0][0] < DATA_FROM_TIMESTAMP){
                     //DATA_FROM_TIMESTAMP = value[0][0];
                     UPDATE_X_AXES_TIME_LINE_STATUS = true;
                 }
             }
         }else{
             //console.log(key + ' : value.length==0')
         }
     }
 }



 //                             -----------------------------------------------------------
 //                                                  Data's Settings
 //                             -----------------------------------------------------------

 // TIME :

 /**
  * Timestamp Conversion from data
  * @param {number} id Data id
  * @param {*} val
  * @returns {string} Return a date
  */
 function timestamp_conversion(id,val){
     if ($(".variable-config[data-timestamp-conversion][data-id=" + id + "]").attr('data-timestamp-conversion') == 1){
         // convert millisecond timestamp to local date
         val = new Date(val).toDateString();
     }else if ($(".variable-config[data-timestamp-conversion][data-id=" + id + "]").attr('data-timestamp-conversion') == 2){
         // convert millisecond timestamp to local time
         val = new Date(val).toTimeString();
     }else if ($(".variable-config[data-timestamp-conversion][data-id=" + id + "]").attr('data-timestamp-conversion') == 3){
         // convert millisecond timestamp to local date and time
         val = new Date(val).toUTCString();
     }else if ($(".variable-config[data-timestamp-conversion][data-id=" + id + "]").attr('data-timestamp-conversion') == 4){
         // convert second timestamp to local date
         val = new Date(val * 1000).toDateString();
     }else if ($(".variable-config[data-timestamp-conversion][data-id=" + id + "]").attr('data-timestamp-conversion') == 5){
         // convert second timestamp to local time
         val = new Date(val * 1000).toTimeString();
     }else if ($(".variable-config[data-timestamp-conversion][data-id=" + id + "]").attr('data-timestamp-conversion') == 6){
         // convert second timestamp to local date and time
         val = new Date(val * 1000).toUTCString();
     }
     return val;
 }
 /**
  * Convert milliseconds into time format
  * @param {*} duration Time to convert
  * @returns {string} Return a time string like
  */
 function msToTime(duration) {
     var milliseconds = parseInt(duration % 1000),
       seconds = Math.floor((duration / 1000) % 60),
       minutes = Math.floor((duration / (1000 * 60)) % 60),
       hours = Math.floor((duration / (1000 * 60 * 60)) % 24);
       days = Math.floor(duration / (1000 * 60 * 60 * 24));

     //hours = (hours < 10) ? "0" + hours : hours;
     //minutes = (minutes < 10) ? "0" + minutes : minutes;
     //seconds = (seconds < 10) ? "0" + seconds : seconds;
     if (days != 0) {
       return days + "d " + hours + "h " + minutes + "m " + seconds + "s";
     }else if (hours != 0) {
       return hours + "h " + minutes + "m " + seconds + "s";
     }else if (minutes != 0) {
       return minutes + "m " + seconds + "s";
     }else {
       return seconds + "." + milliseconds + "s";
     }
 }


 /**
  * As data can take multiple format, we have to use a data dictionnary
  * @param {number} id Data id
  * @param {number|boolean} val Data format
  * @returns {*} Returns data type of 'val' in the data dictionnary
  */
 function dictionary(id,val){
     if ($(".variable-config[data-dictionary][data-id=" + id + "]").attr('data-dictionary')){
         // apply dictionary
         t = JSON.parse($(".variable-config[data-dictionary][data-id=" + id + "]").attr('data-dictionary'));
         if (val in t) {
             val = t[val];
         }else if (parseFloat(val).toFixed(1) in t) {
             //int stored as a float
             val = t[parseFloat(val).toFixed(1)];
         }
     }
     return val;
 }


 /**
  * Return id's variable's color
  * @param {number} id Control item id
  * @param {boolean} val
  * @returns {string} Return the hex color
  */
 function update_data_colors(id,val){
     if (typeof id == 'undefined' || id.split("-").length < 2) {return;}
     id = id.split("-")[1]

     function componentToHex(c) {
         var hex = c.toString(16);
         return hex.length == 1 ? "0" + hex : hex;
     }

     function rgbToHex(rgb) {
         if (typeof rgb != "object" || rgb.constructor != Array || rgb.length != 3) {console.log(typeof rgb, rgb.constructor, rgb.length, rgb);return;}
         r = rgb[0]
         g = rgb[1]
         b = rgb[2]
         return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
     }

     function colorToRgb(color_id) {
        if (color_id == -1) {return [92, 200, 92];}
        else if (color_id == 0) {return [250, 250, 250];}
        var r = get_config_from_hidden_config("color", 'id', color_id, 'r');
        var g = get_config_from_hidden_config("color", 'id', color_id, 'g');
        var b = get_config_from_hidden_config("color", 'id', color_id, 'b');
        return [parseInt(r), parseInt(g), parseInt(b)]
     }

     var display_value_option_id = get_config_from_hidden_config("controlitem", 'id', id, 'display-value-options');
     // variable colors
     var color_type = get_config_from_hidden_config("displayvalueoption", 'id', display_value_option_id, 'color_type');
     var color_mode = get_config_from_hidden_config("displayvalueoption", 'id', id, 'mode');
     var color_level_1_type = get_config_from_hidden_config("displayvalueoption", 'id', display_value_option_id, 'color-level-1-type');
     var color_level_2_type = get_config_from_hidden_config("displayvalueoption", 'id', display_value_option_id, 'color-level-2-type');
     var color_level_1 = get_config_from_hidden_config("displayvalueoption", 'id', display_value_option_id, 'color-level-1');
     var color_level_2 = get_config_from_hidden_config("displayvalueoption", 'id', display_value_option_id, 'color-level-2');
     var color_1 = get_config_from_hidden_config("displayvalueoption", 'id', display_value_option_id, 'color-1');
     var color_2 = get_config_from_hidden_config("displayvalueoption", 'id', display_value_option_id, 'color-2');
     var color_3 = get_config_from_hidden_config("displayvalueoption", 'id', display_value_option_id, 'color-3');

     var type = null;
     var v_id = null;
     if (get_config_from_hidden_config("controlitem", 'id', id, 'variable') != null) {
        type = "variable";
        v_id = get_config_from_hidden_config("controlitem", 'id', id, 'variable');
     }else if (get_config_from_hidden_config("controlitem", 'id', id, 'variable-property') != null) {
        type = "variableproperty";
        v_id = get_config_from_hidden_config("controlitem", 'id', id, 'variable-property');
     }

     if (get_config_from_hidden_config(type, 'id', v_id, 'value-class') == 'BOOLEAN') {
         color_type = 1;
         color_level_1 = 1;
         color_level_1_type = 1;
         if (val == false) { val = 0 ;} else if ( val == true ) { val = 1 ;}
         if (color_1 == null) {color_1 = 0};
         if (color_2 == null) {color_2 = -1};
     }


     if (typeof color_1 == 'undefined') {return;}

     var color = null;

     // COLOR TYPE :
     switch(color_type){
         case 1 :
         if (color_level_1_type == 0) {
             if (val <= color_level_1) {
                 color = color_1;
             }else {
                 color = color_2;
             }
         }else if (color_level_1_type == 1) {
             if (val < color_level_1) {
                 color = color_1;
             }else {
                 color = color_2;
             }
         }
         break;

         case 2:
             if (color_level_1_type == 0) {
                 if (val <= color_level_1) {
                     color = color_1;
                 }else {
                     color = color_2;
                 }
             }else if (color_level_1_type == 1) {
                 if (val < color_level_1) {
                     color = color_1;
                 }else {
                     color = color_2;
                 }
             }
             break;

         case 3:
             if (val <= color_level_1) {
                 color = color_1;
             }else if (val >= color_level_2) {
                 color = color_2;
             }else {
                 fade = (val-color_level_1)/(color_level_2-color_level_1);
                 color_1_new = new Color(color_1.match(/\d+/g)[0],color_1.match(/\d+/g)[1],color_1.match(/\d+/g)[2]);
                 color_2_new = new Color(color_2.match(/\d+/g)[0],color_2.match(/\d+/g)[1],color_2.match(/\d+/g)[2]);
                 color = colorGradient(fade, color_1_new, color_2_new);
             }
             break;

         default:
             if (val < color_level_1) {
                 color = color_1;
             }else if (color_level_2_type == 0) {
                 if (val <= color_level_2) {
                     color = color_2;
                 }else {
                     color = color_3;
                 }
             }else {
                 if (val < color_level_2) {
                     color = color_2;
                 }else {
                     color = color_3;
                 }
             }
             break;
     }

     return rgbToHex(colorToRgb(color));
 }


 //                             -----------------------------------------------------------
 //                                                  Data's Functions
 //                             -----------------------------------------------------------

 /**
  * Update variable data values and refresh logo
  * @param {number} key Data id to update
  * @param {*} val The new data
  * @param {number} time The timestamp
  */
 function update_data_values(key,val,time){

     // CHECKING 'key' TYPE :
     if (key.split("-")[0] == "var") {var type="variable";} else {var type="variableproperty";}

     // get the unit
     var unit_id = get_config_from_hidden_config(type,'id',key.split("-")[1],'unit')
     var unit = get_config_from_hidden_config('unit','id',unit_id,'unit')
     if (typeof unit == 'undefined') { unit = '' };

     // get the device polling interval
     if (type == "variable") {
        var var_id = key.split("-")[1];
     }else {
        var var_id = get_config_from_hidden_config(type, 'id', key.split("-")[1], 'variable')
     }
     var device_id = get_config_from_hidden_config("variable", 'id', var_id, 'device')
     var device_polling_interval = get_config_from_hidden_config("device", 'id', device_id, 'polling-interval')

     // TIME UPDATE :
     if (time != null) {
         var t_last_update = SERVER_TIME - time;
         //t_next_update = 1000 * $(".variable-config[data-value-timestamp][data-key=" + key.split("-")[1] + "][data-type=" + type + "]").attr('data-device-polling_interval') - t_last_update;
         var t_next_update = 1000 * device_polling_interval - t_last_update;
         var t_next_update_string = ((t_next_update < 1000) ? '< 1 sec' : msToTime(t_next_update));

         //$(".type-numeric." + key).attr('data-original-title','Current value: ' + val + ' ' + unit + '<br>Last update: ' + msToTime(t_last_update) + ' ago<br>Next update: ' + t_next_update_string);
         document.querySelectorAll(".type-numeric." + key).forEach(function(e) {
            e.setAttribute('data-original-title','Current value: ' + val + ' ' + unit + '<br>Last update: ' + msToTime(t_last_update) + ' ago<br>Next update: ' + t_next_update_string);
         });
         //$(".variable-config[data-value-timestamp][data-key=" + key.split("-")[1] + "][data-type=" + type + "]").attr('data-value-timestamp',time);
         set_config_from_hidden_config(type, 'id', key.split("-")[1], 'value-timestamp', time)
         //$(".variable-config2[data-value-timestamp][data-id=" + key.split("-")[1] + "]").attr('data-value-timestamp',time);

         // Show and hide warning or alert icons left the the variable name when data is old in comparison of the device polling interval
         //polling_interval = $(".variable-config[data-device-polling_interval][data-key=" + key.split("-")[1] + "]").attr('data-device-polling_interval');
         if (time < SERVER_TIME - 10 * Math.max(1000 * device_polling_interval, REFRESH_RATE)) {
             $(".type-numeric." + key).parent().find('.glyphicon-alert').removeClass("hidden");
             $(".type-numeric." + key).parent().find('.glyphicon-exclamation-sign').addClass("hidden");
         }else if (time < SERVER_TIME - 3 * Math.max(1000 * device_polling_interval, REFRESH_RATE)) {
             $(".type-numeric." + key).parent().find('.glyphicon-alert').addClass("hidden");
             $(".type-numeric." + key).parent().find('.glyphicon-exclamation-sign').removeClass("hidden");
         }else {
             $(".type-numeric." + key).parent().find('.glyphicon-alert').addClass("hidden");
             $(".type-numeric." + key).parent().find('.glyphicon-exclamation-sign').addClass("hidden");
         }
     }

     //if ($(".variable-config[data-refresh-requested-timestamp][data-key=" + key.split("-")[1] + "][data-type=" + type + "]").attr('data-refresh-requested-timestamp') != "" && time != null && time <= $(".variable-config[data-refresh-requested-timestamp][data-key=" + key.split("-")[1] + "][data-type=" + type + "]").attr('data-refresh-requested-timestamp')) {
     // Quit if the value is not newer than the last read request
     var refresh_requested_timestamp = get_config_from_hidden_config(type, 'id', key.split("-")[1], 'refresh-requested-timestamp');
     if (refresh_requested_timestamp != null && time != null && time <= refresh_requested_timestamp) {
         return;
     }


     // TYPE OF 'val' :
     // NUMBER :
     if (typeof(val)==="number"){

         var r_val = Number(val);

         // adjusting r_val
         if(Math.abs(r_val) == 0 ){
             r_val = 0;
         }else if(Math.abs(r_val) < 0.001) {
             r_val = r_val.toExponential(2);
         }else if (Math.abs(r_val) < 0.01) {
             r_val = r_val.toPrecision(1);
         }else if(Math.abs(r_val) < 0.1) {
             r_val = r_val.toPrecision(2);
         }else if(Math.abs(r_val) < 1) {
             r_val = r_val.toPrecision(3);
         }else if(r_val > 100) {
             r_val = r_val.toPrecision(4);
         }else{
             r_val = r_val.toPrecision(4);
         }

         // colors
         document.querySelectorAll(".control-item.type-numeric." + key).forEach(function(e) {
             var control_item_id = e.id;
             var display_value_option_id = get_config_from_hidden_config("controlitem", 'id', control_item_id, 'display-value-options');
             //var color_mode = $(".variable-config[data-color-mode][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-color-mode');
             var color_mode = get_config_from_hidden_config("displayvalueoption", 'id', display_value_option_id, 'mode');
             var color_type = get_config_from_hidden_config("displayvalueoption", 'id', display_value_option_id, 'color_type');
             var timestamp_conversion_value = get_config_from_hidden_config("displayvalueoption", 'id', display_value_option_id, 'timestamp-conversion');
             var dictionary_value = get_config_from_hidden_config("displayvalueoption", 'id', display_value_option_id, 'data-dictionary');
             if (color_mode != 1 ) {
                 var r_val_temp = r_val;
                 if (timestamp_conversion_value != null && timestamp_conversion_value != 0){
                     // Transform timestamps
                     r_val_temp=timestamp_conversion(control_item_id,val);
                 }else if (dictionary_value != null && dictionary_value != 0){
                     // Transform value in dictionaries
                     r_val_temp=dictionary(control_item_id,val);
                 }
                 // Set the text value
                 document.querySelector("#" + control_item_id).innerHTML = r_val_temp + " " + unit;
             }
             if (color_type != 0 && color_mode != 0){
                 // Change background color
                 e.style.backgroundColor = update_data_colors(control_item_id,val);
             }
         })

         // timestamps
         if (DATA_DISPLAY_FROM_TIMESTAMP > 0 && time < DATA_DISPLAY_FROM_TIMESTAMP) {
         }else if (DATA_DISPLAY_TO_TIMESTAMP > 0 && time > DATA_DISPLAY_TO_TIMESTAMP) {
         }else if (DATA_FROM_TIMESTAMP > 0 && time < DATA_FROM_TIMESTAMP) {
         }else if (DATA_TO_TIMESTAMP > 0 && time > DATA_TO_TIMESTAMP) {
         }else {
             $(".legendValue.type-numeric." + key).html(r_val);
         }

         $(".label .type-numeric." + key).html(r_val);

         if ($('input.'+ key).attr("placeholder") == "") {
             $('input.'+ key).attr("placeholder",r_val);
         }

         // unixtime
         var date = new Date(val*1000);
         $(".type-numeric.unixtime_local_date_time." + key).html(date.toLocaleString());
         $(".type-numeric.unixtime_utc_date_time." + key).html(date.toUTCString());
         $(".type-numeric.hex_str_full." + key).html(val.toString(16).toUpperCase());
     }

     // BOOLEAN :
     // set value fields
     if (typeof(val)==="boolean"){
         // set button colors
         if (val === 0 | val == false) {
             $(".label.type-bool." + key).addClass("label-default");
             $(".label.type-bool." + key).removeClass("label-primary");
             $(".label.type-bool." + key).removeClass("label-info");
             $(".label.type-bool." + key).removeClass("label-success");
             $(".label.type-bool." + key).removeClass("label-warning");
             $(".label.type-bool." + key).removeClass("label-danger");

             // inverted
             $(".label.type-bool.status-red-inv." + key).addClass("label-danger");
             $(".label.type-bool.status-red-inv." + key).removeClass("label-default");

             $('button.btn-success.write-task-btn.' + key).addClass("update-able");
             $('button.update-able.write-task-btn.' + key).addClass("btn-default");
             $('button.update-able.write-task-btn.' + key).removeClass("btn-success");

             val = 0;

             //$(".type-numeric." + key).html(0);
             if ($('input.'+ key).attr("placeholder") == "") {
                 $('input.'+ key).attr("placeholder",0);
             }
         } else {
             $(".label.type-bool." + key).removeClass("label-default");
             $(".label.type-bool.status-blue." + key).addClass("label-primary");
             $(".label.type-bool.status-info." + key).addClass("label-info");
             $(".label.type-bool.status-green." + key).addClass("label-success");
             $(".label.type-bool.status-yellow." + key).addClass("label-warning");
             $(".label.type-bool.status-red." + key).addClass("label-danger");

             // inverted
             $(".label.type-bool.status-red-inv." + key).removeClass("label-danger");
             $(".label.type-bool.status-red-inv." + key).addClass("label-default");

             val = 1;

             $('button.btn-default.write-task-btn.' + key).addClass("update-able");
             $('button.update-able.write-task-btn.' + key).removeClass("btn-default");
             $('button.update-able.write-task-btn.' + key).addClass("btn-success");

             //$(".type-numeric." + key).html(1);
             if ($('input.'+ key).attr("placeholder") == "") {
                 $('input.'+ key).attr("placeholder",1);
             }
         }

         $(".label .type-numeric." + key).html(val);

         // timestamps
         if (DATA_DISPLAY_FROM_TIMESTAMP > 0 && time < DATA_DISPLAY_FROM_TIMESTAMP) {
         }else if (DATA_DISPLAY_TO_TIMESTAMP > 0 && time > DATA_DISPLAY_TO_TIMESTAMP) {
         }else if (DATA_FROM_TIMESTAMP > 0 && time < DATA_FROM_TIMESTAMP) {
         }else if (DATA_TO_TIMESTAMP > 0 && time > DATA_TO_TIMESTAMP) {
         }else { $(".legendValue.type-numeric." + key).html(val); }

         // colors
         for (i = 0; i < $(".control-item.type-numeric." + key).length; ++i) {
             var display_value_option_id = get_config_from_hidden_config("controlitem", 'id', i, 'display-value-options');
             //var color_mode = $(".variable-config[data-color-mode][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-color-mode');
             var color_mode = get_config_from_hidden_config("displayvalueoption", 'id', display_value_option_id, 'mode');
             var color_type = get_config_from_hidden_config("displayvalueoption", 'id', display_value_option_id, 'color_type');
             var dictionary_value = get_config_from_hidden_config("displayvalueoption", 'id', display_value_option_id, 'data-dictionary');

             if (color_mode != 1 ) {
                 var r_val_temp = r_val;
                 if (dictionary_value != null && dictionary_value != 0){
                     // Transform value in dictionaries
                     r_val_temp=dictionary($(".control-item.type-numeric." + key)[i].id,val);
                 }
                 // Set the text value
                 $("#" + $(".control-item.type-numeric." + key)[i].id).html(r_val_temp);
             }
             if (color_type != 0 && color_mode != 0){
                 // Change background color
                 $($(".control-item.type-numeric." + key)[i]).css("background-color", update_data_colors($(".control-item.type-numeric." + key)[i].id,val));
             }
         }
     }

     // OBJECT :
     if (typeof(val)==="object" && val === null){
         $(".type-numeric." + key).html(val);
         if ($('input.'+ key).attr("placeholder") == "") {
             $('input.'+ key).attr("placeholder",val);
         }
     }

     // STRING :
     if (typeof(val)==="string"){
         $(".type-numeric." + key).html(val);
         // indicative text
         if ($('input.'+ key).attr("placeholder") == "") {
             $('input.'+ key).attr("placeholder",val);
         }
     }

     refresh_logo(key.split("-")[1], type);
 }


/**
- Get a config from ALL hidden config div
- @param {string} type Name of the model
- @param {string} filter_data name of the data config to filter by
- @param {string} get_data name of the data config wanted
- @returns {Array<object>} dict of (id: value) of found values
*/
function get_config_from_hidden_configs(type,filter_data='id',get_data='id'){
    var result = {};
    if (typeof(type)!== 'string' || typeof(filter_data) !== 'string' || typeof(get_data) !== 'string' || filter_data === '' || get_data === '' || type === '') {
      return result;
    };
    var query = document.querySelectorAll("." + type + "-config2");
    query.forEach(item => {
        //var id = item.dataset.id;
        var id = item.getAttribute("data-" + filter_data);
        var r = item.getAttribute("data-" + get_data);
        if (id in result === false && typeof(r) !== "undefined") {
            result[id] = r;
        };
    });
    return result;
}


/**
- Get a config from ONE hidden config div
- @param {string} type Name of the model
- @param {string} filter_data name of the data config to filter by
- @param {string} val value of the data config to filter by
- @param {string} get_data name of the data config wanted
- @returns {Array<object>} value found
*/
function get_config_from_hidden_config(type,filter_data,val,get_data){
    var r = get_config_from_hidden_configs(type,filter_data,get_data);
    if (val in r) {return r[val];}
}

/**
- Set a config from ONE hidden config div
- @param {string} type Name of the model
- @param {string} filter_data name of the data config to filter by
- @param {string} val value of the data config to filter by
- @param {string} get_data name of the data config wanted
- @param {string} value set get_data filed to this
*/
function set_config_from_hidden_config(type,filter_data,val,get_data,value){
    document.querySelectorAll("." + type + "-config2[data-" + filter_data + "='" + val + "']").forEach(function(e) {
    e.setAttribute("data-" + get_data, value);
    })
}


 /**
  * Update 'DATA', by erasing datas which are out of date
  * @param {number} key Data id to update
  */
 function check_buffer(key){
     if ((DATA[key][0][0] < DATA_FROM_TIMESTAMP)){
         stop_id = find_index_sub_lte(DATA[key],DATA_FROM_TIMESTAMP,0);
         DATA[key] = DATA[key].splice(stop_id);
     }
 }

 function add_key_to_chart_vars(key, var_count, vars, device_pulling_interval_sum, timestamp, var_count_poll) {
    if(key in CHART_VARIABLE_KEYS && CHART_VARIABLE_KEYS[key]<=DATA_INIT_STATUS){
         CHART_VARIABLE_KEYS[key]++;
         var_count++;
         INIT_CHART_VARIABLES_COUNT++;
         vars.push(key);
         dpi = get_config_from_hidden_config('device','id',get_config_from_hidden_config('variable','id',key,'device') ,'polling-interval');
         if (! isNaN(dpi)) {device_pulling_interval_sum += parseFloat(dpi);var_count_poll++;}else {console.log("ConfigV2 not found for var " + key);};
         if (typeof(DATA[key]) == 'object'){
             timestamp = Math.max(timestamp,DATA[key][0][0]);
         }else{
            // if a key doesn't exist in DATA timestamp to is set to now
            timestamp = SERVER_TIME;
         }
    }
    return [key, var_count, vars, device_pulling_interval_sum, timestamp, var_count_poll];
 }

 /**
  * Update periodically the DATA, by requesting the server
  */
 function data_handler(){
     if(AUTO_UPDATE_ACTIVE || !INIT_STATUS_VARIABLES_DONE || !INIT_CHART_VARIABLES_DONE){
         if(DATA_TO_TIMESTAMP==0 && FETCH_DATA_PENDING<=0){
         // fetch the SERVER_TIME
             data_handler_ajax(0,[],[],Date.now());
         }else{
             if(FETCH_DATA_PENDING<=0 && INIT_STATUS_VARIABLES_DONE && INIT_CHART_VARIABLES_DONE){
             // fetch new data
                 data_handler_ajax(0, VARIABLE_KEYS, VARIABLE_PROPERTY_KEYS, LAST_QUERY_TIME);
             }
             // fetch historic data
             else if(FETCH_DATA_PENDING<=0){
                 if(!INIT_STATUS_VARIABLES_DONE){
                 loading_states[4] || set_loading_state(4, 0);
                 // first load STATUS_VARIABLES
                     var var_count = 0;
                     var vars = [];
                     var props = [];
                     var timestamp = DATA_TO_TIMESTAMP;
                     for (var key in STATUS_VARIABLE_KEYS){
                         if (typeof(CHART_VARIABLE_KEYS[key]) === 'undefined'){
                             if(STATUS_VARIABLE_KEYS[key]<1){
                                 STATUS_VARIABLE_KEYS[key]++;
                                 var_count++;
                                 vars.push(key);
                             }
                         }
                         if(var_count >= 5){break;}
                     }
                     if(var_count>0){
                         data_handler_ajax(1,vars,props,timestamp);
                         set_loading_state(4, (loading_states[4] || 0) + 100*var_count/STATUS_VARIABLE_KEYS.count());
                     }else{
                         INIT_STATUS_VARIABLES_DONE = true;
                         set_loading_state(4, 100);
                     }
                 }else if (!INIT_CHART_VARIABLES_DONE){
                     loading_states[5] || set_loading_state(5, 0);
                     var var_count = 0;
                     var var_count_poll = 0;
                     var vars = [];
                     var props = [];
                     var device_pulling_interval_sum = 0.0
                     if (DATA_FROM_TIMESTAMP == -1){
                         var timestamp = SERVER_TIME;
                     }else{
                         var timestamp = DATA_FROM_TIMESTAMP;
                     }

                     var page = document.querySelector('#content .sub-page:not([style*="display:none"]):not([style*="display: none"])');
                     var visible_hidden_config = page != null ? page.querySelectorAll('.hidden.variable-config') : [];
                     var visible_vars = [];
                     for (let vhc of visible_hidden_config.keys()) {
                         visible_vars.push(visible_hidden_config[vhc].dataset['key']);
                     }

                     // First iterate on visible variables
                     for (var key in visible_vars){
                        key = visible_vars[key];
                        if(var_count >= 10){break;}
                        [key, var_count, vars, device_pulling_interval_sum, timestamp, var_count_poll] = add_key_to_chart_vars(key, var_count, vars, device_pulling_interval_sum, timestamp, var_count_poll);
                     }
                     if (var_count == 0) {
                         for (var key in CHART_VARIABLE_KEYS){
                            if(var_count >= 10){break;}
                            [key, var_count, vars, device_pulling_interval_sum, timestamp, var_count_poll] = add_key_to_chart_vars(key, var_count, vars, device_pulling_interval_sum, timestamp, var_count_poll);
                         }
                     }
                     if(var_count>0){
                         //set_loading_state(5, (loading_states[5] || 0) + 100*var_count/CHART_VARIABLE_KEYS.count());
                         if (timestamp === DATA_FROM_TIMESTAMP){
                             timestamp = DATA_DISPLAY_TO_TIMESTAMP;
                         }
                         if (timestamp == -1){
                             //var timestamp = SERVER_TIME;
                             timestamp = DATA_TO_TIMESTAMP;
                         }
                         request_duration = timestamp - DATA_FROM_TIMESTAMP
                         // Fetch 1 000 points by var
                         point_quantity_to_fetch_by_var = 1000;
                         t_start = DATA_FROM_TIMESTAMP;
                         if (var_count_poll > 0) {
                           duration_for_quantity = point_quantity_to_fetch_by_var * device_pulling_interval_sum / var_count_poll;
                           duration_for_quantity = duration_for_quantity * 10 / var_count  //adjust for less than 10 vars
                           duration_for_quantity = parseInt(duration_for_quantity);
                           t = Math.max(timestamp - duration_for_quantity * 1000, t_start);
                         }else {
                           t = t_start;
                           duration_for_quantity = 1;
                         }
                         FETCH_DATA_PENDING++;
                         store_temp_ajax_data = [1,vars,props,t_start,t,timestamp,duration_for_quantity,timestamp]
                         //data_handler_ajax(1,vars,props,DATA_FROM_TIMESTAMP,timestamp);
                     }else{
                         INIT_CHART_VARIABLES_DONE = true;
                         set_loading_state(5, 100);
                         $('.loadingAnimation').hide();
                     }
                 }
             }else if (FETCH_DATA_PENDING<=1 && store_temp_ajax_data !== null) {
               /*
               */
               vars = store_temp_ajax_data[1]
               props = store_temp_ajax_data[2]
               t_start = store_temp_ajax_data[3]
               t = store_temp_ajax_data[4]
               timestamp = store_temp_ajax_data[5]
               duration_for_quantity = store_temp_ajax_data[6]
               tmax = store_temp_ajax_data[7]
               set_loading_state(5, (loading_states[5] || 0) + 100*(vars.length/CHART_VARIABLE_KEYS.count())*((timestamp-t)/(tmax-t_start)));
               //data_handler_ajax(1,vars,props,t_start,t);
               data_handler_ajax(1,vars,props,t,timestamp);
               if (t_start < t) {
                 timestamp = t;
                 t = Math.max(t - duration_for_quantity * 1000, t_start);
                 store_temp_ajax_data = [1,vars,props,t_start,t,timestamp,duration_for_quantity,tmax];
               }else {
                 FETCH_DATA_PENDING--;
                 store_temp_ajax_data = null;
               }
             }
         }
     }

     // call the data handler periodically
     if(!INIT_STATUS_VARIABLES_DONE || !INIT_CHART_VARIABLES_DONE){
         // initialisation is active
         //setTimeout(function() {data_handler();}, REFRESH_RATE/2.0);
         if (STATUS_VARIABLE_KEYS.count() + CHART_VARIABLE_KEYS.count() == 0 && LOADING_PAGE_DONE == 0) {LOADING_PAGE_DONE = 1;show_page();hide_loading_state();}
         setTimeout(function() {data_handler();}, 100);
     }else{
         if (LOADING_PAGE_DONE == 0) {LOADING_PAGE_DONE = 1;show_page();hide_loading_state();loading_states={};}
         setTimeout(function() {data_handler();}, REFRESH_RATE);
     }
 }


 /**
  * Send data to the Data handler
  * @param {boolean} init Show update status or not
  * @param {Array<number>} variable_keys List of variables to update
  * @param {Array<*>} variable_property_keys List of variable properties to update
  * @param {number} timestamp_from Update data from this timestamp
  * @param {number} timestamp_to Update data to this timestamp
  */
 function data_handler_ajax(init,variable_keys,variable_property_keys,timestamp_from,timestamp_to){
     show_update_status();
     FETCH_DATA_PENDING++;
     if(init){show_init_status();}
     request_data = {timestamp_from:timestamp_from, variables: variable_keys, init: init, variable_properties:variable_property_keys};
     if (typeof(timestamp_to !== 'undefined')){request_data['timestamp_to']=timestamp_to};
     //if (!init){request_data['timestamp_from'] = request_data['timestamp_from'] - REFRESH_RATE;};
     $.ajax({
         url: ROOT_URL+'json/cache_data/',
         dataType: "json",
         timeout: ((init == 1) ? FETCH_DATA_TIMEOUT*5: FETCH_DATA_TIMEOUT),
         type: "POST",
         data:request_data,
         dataType:"json"
         }).done(data_handler_done).fail(data_handler_fail);
 }


 /**
  * Update DATA and Charts when initialization is done
  * @param {Array<*>} fetched_data
  */
 function data_handler_done(fetched_data){

     update_charts = true;

     // checking 'fectched_data' type
     if (typeof(fetched_data['timestamp'])==="number"){
         timestamp = fetched_data['timestamp'];
         delete fetched_data['timestamp'];
     }else{
         timestamp = 0;
     }

     if (typeof(fetched_data['server_time'])==="number"){
         SERVER_TIME = fetched_data['server_time'];
         delete fetched_data['server_time'];
         var date = new Date(SERVER_TIME);
         $(".server_time").html(date.toLocaleString());
     }else{
         SERVER_TIME = 0;
     }

     if (typeof(fetched_data['date_saved_max'])==="number"){
         LAST_QUERY_TIME = fetched_data['date_saved_max'];
         delete fetched_data['date_saved_max'];
     }else{
         //LAST_QUERY_TIME = 0;
     }

     if (typeof(fetched_data['variable_properties'])==="object"){
         VARIABLE_PROPERTIES_DATA = fetched_data['variable_properties'];
         delete fetched_data['variable_properties'];
         VARIABLE_PROPERTIES_LAST_MODIFIED = fetched_data['variable_properties_last_modified'];
         delete fetched_data['variable_properties_last_modified'];
     }else{
         VARIABLE_PROPERTIES_DATA = {};
         VARIABLE_PROPERTIES_LAST_MODIFIED = {};
     }

     // update data timestamp
     if(DATA_TO_TIMESTAMP==0){
         //DATA_TO_TIMESTAMP = DATA_FROM_TIMESTAMP = SERVER_TIME;
         DATA_TO_TIMESTAMP = SERVER_TIME;
         DATA_FROM_TIMESTAMP = SERVER_TIME - 120 * 60 * 1000;
     }else{
         $.each(fetched_data, function(key, val) {
             add_fetched_data(parseInt(key),val);
         });
         if (DATA_TO_TIMESTAMP < timestamp){
             DATA_TO_TIMESTAMP = timestamp;
             if ((DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP)> DATA_BUFFER_SIZE){
                 DATA_BUFFER_SIZE = DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP
                 //DATA_FROM_TIMESTAMP = DATA_TO_TIMESTAMP - DATA_BUFFER_SIZE;
             }
             if (DATA_DISPLAY_TO_TIMESTAMP < 0 && DATA_DISPLAY_FROM_TIMESTAMP < 0){
                 // both fixed
                 DATA_DISPLAY_WINDOW = DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP;
             }else if (DATA_DISPLAY_FROM_TIMESTAMP > 0 && DATA_DISPLAY_TO_TIMESTAMP < 0){
                 // to time is fixed
                 DATA_DISPLAY_FROM_TIMESTAMP = DATA_TO_TIMESTAMP - DATA_DISPLAY_WINDOW;
             }else if (DATA_DISPLAY_FROM_TIMESTAMP < 0 && DATA_DISPLAY_TO_TIMESTAMP > 0 ){
                 // from time fixed
                 DATA_DISPLAY_TO_TIMESTAMP = DATA_FROM_TIMESTAMP + DATA_DISPLAY_WINDOW;
             }
             UPDATE_X_AXES_TIME_LINE_STATUS = true;
         }
         $.each(PyScadaPlots,function(plot_id){
             var self = this, doBind = function() {
                 PyScadaPlots[plot_id].update(false);
             };
             $.browserQueue.add(doBind, this);
         });
         for (var key in VARIABLE_KEYS) {
             key = VARIABLE_KEYS[key];
             if (typeof(DATA[key]) == 'object'){
                 update_data_values('var-' + key,DATA[key][DATA[key].length-1][1],DATA[key][DATA[key].length-1][0]);
             }
         }
         for (var key in VARIABLE_PROPERTIES_DATA) {
             value = VARIABLE_PROPERTIES_DATA[key];
             if (key in VARIABLE_PROPERTIES_LAST_MODIFIED) {
                 time = VARIABLE_PROPERTIES_LAST_MODIFIED[key];
             }else {time = null};
             update_data_values('prop-' + key,value,time);
         }
         /*
         DATA_OUT_OF_DATE = (SERVER_TIME - timestamp  > CACHE_TIMEOUT);
         if (DATA_OUT_OF_DATE){
             raise_data_out_of_date_error();
         }else{
             clear_data_out_of_date_error();
          }
          */
         // todo
     }

     // update time line
     if (UPDATE_X_AXES_TIME_LINE_STATUS){
         update_timeline();
     }
     // update all legend tables
     $('.legend table').trigger("update");
     if (JSON_ERROR_COUNT > 0) {
         JSON_ERROR_COUNT = JSON_ERROR_COUNT - 1;
     }
     UPDATE_STATUS_COUNT = 0;
     hide_update_status();
     if(request_data.init===1){
         hide_init_status();
     }
     FETCH_DATA_PENDING--;
 }


 /**
  * Will display an Ajax error notification
  * @param {*} x
  * @param {*} t
  * @param {*} m
  */
 function data_handler_fail(x, t, m) {
     //check if we are unauthenticated
     if (x.status !== 0 && x.getResponseHeader("content-type") !== null && x.getResponseHeader("content-type").indexOf("text/html") !== -1) {
         add_notification("Authentication failed, please reload the page", 2, 0);
         //location.reload();
     }

     // error notifications
     if(JSON_ERROR_COUNT % 5 == 0)
         add_notification("Fetching data failed", 3);

     JSON_ERROR_COUNT = JSON_ERROR_COUNT + 1;
     if (JSON_ERROR_COUNT > 15) {
         $(".AutoUpdateStatus").css("color", "red");
         auto_update_click();
         add_notification("Fetching data failed limit reached, auto update deactivated.<br>Check your connectivity and active auto update in the top right corner.", 2, 0);
     } else if(JSON_ERROR_COUNT > 3){
         $(".AutoUpdateStatus").css("color", "orange");
         for (var key in VARIABLE_KEYS) {
             key = VARIABLE_KEYS[key];
             //add_fetched_data(key, [[DATA_TO_TIMESTAMP,Number.NaN]]);
         }
     }
     //hide_update_status();
     if(request_data.init===1){
         for (key in request_data.variables){
             key = request_data.variables[key];
             if (typeof(CHART_VARIABLE_KEYS[key]) === 'number'){
                 CHART_VARIABLE_KEYS[key]--;
             }else if (typeof(STATUS_VARIABLE_KEYS[key]) == 'number'){
                 STATUS_VARIABLE_KEYS[key]--;
             }
         }
         hide_init_status();
     }
     FETCH_DATA_PENDING--;
 }


 // FIND INDEX :

 /**
  * Return index 'i' where a value in 'a' is lower or equal to value 't'
  * @param {Array} a The array
  * @param {number} t The value
  * @returns {number} The index where a value lower than 't' where found
  */
 function find_index(a,t){
     var i = a.length; //or 10
     while(i--){
         if (a[i]<=t){
             return i;
         }
     }
 }
 /**
  * Return index 'i' where a value in 'd' is lower or equal to value 't'
  * @param {Array} a The array
  * @param {number} t The value
  * @param {number} d Sub index
  * @returns {number} The index where a value lower than 't' where found
  */
 function find_index_sub_lte(a,t,d){
     var i = a.length; //or 10
     while(i--){
         if (a[i][d]<=t){
             return i;
         }
     }
 }
 /**
  * Return index 'i' where a value in 'd' is superior or equal to value 't'
  * @param {Array} a The array
  * @param {number} t The value
  * @param {number} d Sub index
  * @returns {number} The index where a value superior than 't' where found
  */
 function find_index_sub_gte(a,t,d){
     var i = 0; //or 10
     while(i < a.length){
         if (a[i][d]>=t){
             return i;
         }
         i++;
     }
 }



 //---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 //---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

 //                                                   CHARTS & COLOR

 //---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 //---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

 function get_period_fields(key) {
    calculatedvariableselectorID = Number(get_config_from_hidden_config('calculatedvariableselector','main-variable',key,'id'));
    if (typeof(calculatedvariableselectorID) == 'undefined' || isNaN(calculatedvariableselectorID)) {return key;};
    periodFields = get_config_from_hidden_config('calculatedvariableselector','id',calculatedvariableselectorID,'period-fields').split(',');
    if (periodFields.length > 1) {periodFields.pop();};  // remove last empty item
    return periodFields;
 }

 function filter_period_fields_by_type(perdioFields, type) {
    validPeriodFields = [];
    for (field in periodFields) {
        if (get_config_from_hidden_config('periodicfield','id',periodFields[field],'type') == type) {
            validPeriodFields.push(periodFields[field])
        }
    }
    return validPeriodFields;
 }

 aggregation_types = [(0, 'min'),
                    (1, 'max'),
                    (2, 'total'),
                    (3, 'difference'),
                    (4, 'difference percent'),
                    (5, 'delta'),
                    (6, 'mean'),
                    (7, 'first'),
                    (8, 'last'),
                    (9, 'count'),
                    (10, 'count value'),
                    (11, 'range'),
                    (12, 'step'),
                    (13, 'change count'),
                    (14, 'distinct count'),]

 function filter_aggregation_type_for_period_list(period_list) {
    result = []
    for (p in period_list) {
         i = get_config_from_hidden_config('periodicfield','id',period_list[p],'type')
         if (typeof(i) !== 'undefined') {
             result[i] = aggregation_types[i]
         }
    }
    return result
 }

 function get_one_field_by_period_field(validPeriodFields) {
    /*
    period_choices = ((0, 'second'),
                      (1, 'minute'),
                      (2, 'hour'),
                      (3, 'day'),
                      (4, 'week'),
                      (5, 'month'),
                      (6, 'year'),
                      )
    */
    // Store a field by period choice. Prefer the lowest period factor and if equals, the the lowest starting point.
    periodCalcVar = {0:null,1:null,2:null,3:null,4:null,5:null,6:null,}
    for (validPeriodField in validPeriodFields) {
        period = get_config_from_hidden_config('periodicfield','id',validPeriodFields[validPeriodField],'period');
        if (periodCalcVar[period] == null) {
            periodCalcVar[period] = validPeriodFields[validPeriodField];
        }else {
            newPeriodFactor = get_config_from_hidden_config('periodicfield','id',validPeriodFields[validPeriodField],'period-factor');
            newStartFrom = get_config_from_hidden_config('periodicfield','id',validPeriodFields[validPeriodField],'period-factor');
            currentPeriodFactor = get_config_from_hidden_config('periodicfield','id',periodCalcVar[period],'period-factor');
            currentStartFrom = get_config_from_hidden_config('periodicfield','id',periodCalcVar[period],'period-factor');
            if (currentPeriodFactor > newPeriodFactor) {
                periodCalcVar[period] = validPeriodFields[validPeriodField];
            }else if (currentPeriodFactor = newPeriodFactor && currentStartFrom > newStartFrom) {
                periodCalcVar[period] = validPeriodFields[validPeriodField];
            }
        }
    }
    return periodCalcVar;
 }

 function get_variable_keys_for_period_calculated_variables(periodCalcVar) {
    keyCalcVar = {0:null,1:null,2:null,3:null,4:null,5:null,6:null,}
    for (p in periodCalcVar) {
        if (periodCalcVar[p] !== null) {
            periods = get_config_from_hidden_configs('calculatedvariable','id','period');
            for (idP in periods) {
                if (periodCalcVar[p] == periods[idP] && get_config_from_hidden_config('calculatedvariable','id',idP,'variable-calculated-fields') == calculatedvariableselectorID) {
                    keyCalcVar[p] = get_config_from_hidden_config('calculatedvariable','id',idP,'store-variable');
                }
            }
        }
    }
    return keyCalcVar;
 }

 function get_one_variable_key_of_calculated_variable_for_duration(start, stop, min_aggregate, keyCalcVar) {
    if (keyCalcVar[6] !== null && (stop - start) > (60 * 60 * 24 * 365 * min_aggregate)) {return keyCalcVar[6]}
    else if (keyCalcVar[5] !== null && (stop - start) > (60 * 60 * 24 * 31 * min_aggregate)) {return keyCalcVar[5]}
    else if (keyCalcVar[4] !== null && (stop - start) > (60 * 60 * 24 * 7 * min_aggregate)) {return keyCalcVar[4]}
    else if (keyCalcVar[3] !== null && (stop - start) > (60 * 60 * 24 * min_aggregate)) {return keyCalcVar[3]}
    else if (keyCalcVar[2] !== null && (stop - start) > (60 * 60 * min_aggregate)) {return keyCalcVar[2]}
    else if (keyCalcVar[1] !== null && (stop - start) > (60 * min_aggregate)) {return keyCalcVar[1]}
    else if (keyCalcVar[0] !== null && (stop - start) > min_aggregate) {return keyCalcVar[0]}
    return null;
 }

 /*
  * Get data from an agragated variable if it exist
  * If stop - start > 1 year, get value by month if exist, or by week or by day ...
  * @param {number} key key of the initial variable
  * @param {number} start start timestamp in ms
  * @param {number} stop stop timestamp in ms
  * @param {number} type type could be (0, 'min'),
                    (1, 'max'),
                    (2, 'total'),
                    (3, 'difference'),
                    (4, 'difference percent'),
                    (5, 'delta'),
                    (6, 'mean'),
                    (7, 'first'),
                    (8, 'last'),
                    (9, 'count'),
                    (10, 'count value'),
                    (11, 'range'),
                    (12, 'step'),
                    (13, 'change count'),
                    (14, 'distinct count'),
 */
 function get_aggregated_data(key, start, stop, type=6, min_aggregate=3) {
    if (!Number.isInteger(key) || Number.isNaN(start) || Number.isNaN(stop) || !Number.isInteger(type) || !Number.isInteger(min_aggregate)) {console.log("get_aggregated_data : a param is not a int, number, number, int : ", key, start, stop, type);return key;};
    key = Number(key);
    start = Number(start);
    stop = Number(stop);
    type = Number(type);
    min_aggregate = parseInt(min_aggregate);
    if (min_aggregate <= 0) {console.log("min_aggregate should be > 0, it is ", min_aggregate);return key;};
    if (!key in DATA) {console.log(key, "not in DATA");return key;};
    //if (start < 0 || stop < 0) {console.log("start or stop < 0 :", start, stop);};
    if (start < 0) {start = DATA_FROM_TIMESTAMP;};
    if (stop < 0) {stop = DATA_TO_TIMESTAMP;};
    start = start / 1000;
    stop = stop / 1000;
    if (start >= stop) {console.log("start is not < stop :", start, stop);return key;};
    if (type < 0 || type > 14) {console.log("type is not 0 between and 14 included :", type)};

    periodFields = get_period_fields(key);
    validPeriodFields = filter_period_fields_by_type(periodFields, type);
    periodCalcVar = get_one_field_by_period_field(validPeriodFields);
    keyCalcVar = get_variable_keys_for_period_calculated_variables(periodCalcVar);
    new_key = get_one_variable_key_of_calculated_variable_for_duration(start, stop, min_aggregate, keyCalcVar);
    if (new_key !== null) {return new_key;}
    return key;
 }

 // COLOR OBJECT :
 /**
  * Color class
  * @param {number} red red color between 0 and 255
  * @param {number} green green color between 0 and 255
  * @param {number} blue blue color between 0 and 255
  */
 function Color(red,green,blue) {
     this.red = red;
     this.green = green;
     this.blue = blue;
 }

 // CHARTS OBJETCS :

 /**
  * A chart with x and y axes, with logarithmic mode
  * @param {number} id The container id where to display the chart
  * @param {boolean} xaxisVarId
  * @param {boolean} xaxisLinLog Logarithmic mode
  */
 function PyScadaPlot(id, xaxisVarId, xaxisLinLog){
     var options = {
         legend: {
             show: false,
         },
         series: {
             shadowSize: 0,
             lines: {
                show: true,
                lineWidth: 3,
             },
             points: {
                show: true,
                radius: 4,
                symbol: "cross",
             },
             bars: {
                 show: false,
                 barWidth: [0.5, false],
                 align: "center",
             },
         },
         xaxis: {
             mode: (xaxisVarId == null ? "time" : (xaxisLinLog == true ? "log" : null)), // logarithmic mode
             ticks: (xaxisVarId == null ? $('#chart-container-'+id).data('xaxisTicks') : null),
             timeformat: "%d/%m/%Y<br>%H:%M:%S",
             timezone: "browser",
             timeBase: "milliseconds", // x axis is milliseconds
             autoScale: (xaxisVarId == null ? "none" : "exact"),
             showTickLabels: (xaxisVarId == null ? "major" : "all")
         },
         yaxis: {
             position: "left",
             autoScale: "loose",
             autoScaleMargin: 0.1,
             min: null,
             max: null,
         },
         yaxes: [],
         selection: {
             mode: "y"
         },
         grid: {
             labelMargin: 10,
             margin: {
                 top: 20,
                 bottom: 8,
                 left: 20
             },
             borderWidth: 0,
             hoverable: true,
             clickable: true
         },
         zoom: {
             active: true,
         },
         pan: {
             interactive: true,
         },
         axisvalues: {
             mode: "xy",
         },
         crosshair: {
             mode: "xy"
         },
     },
     series = [],		// just the active data series
     keys   = [],		// list of variable keys (ids)
     variable_names = [], // list of all variable names
     variables = {},     // list of all variables
     flotPlot,			// handle to plot
     prepared = false,	// is the chart prepared

     // areas in the container
     legend_id = '#chart-legend-' + id,
     legend_table_id = '#chart-legend-table-' + id,
     chart_container_id = '#chart-container-'+id,
     legend_checkbox_id = '#chart-legend-checkbox-' + id + '-',
     legend_checkbox_status_id = '#chart-legend-checkbox-status-' + id + '-',
     legend_value_id = '#chart-legend-value-' + id + '-',

     axes = {},
     raxes = {},

     // the object
     plot = this;


     // public functions
     plot.update 			= update;
     plot.prepare 			= prepare;
     plot.resize 			= resize;
     plot.updateLegend 		= updateLegend;

     //getter
     plot.getSeries 			= function () { return series };
     plot.getFlotObject		= function () { return flotPlot};
     plot.getKeys			= function (){ return keys};
     plot.getVariableNames	= function (){ return variable_names};

     plot.getInitStatus		= function () { if(InitDone){return InitRetry}else{return false}};
     plot.getId				= function () {return id};
     plot.getChartContainerId= function () {return chart_container_id};

     // init data
     tf = function (value, axis) {
         return value.toFixed(axis.tickDecimals) + (((typeof options.yaxes[axis.n-1].unit != "undefined") && options.yaxes[axis.n-1].unit != null) ? options.yaxes[axis.n-1].unit : '');
     };
     options.yaxis.tickFormatter = tf;

     k=0
     $.each($(legend_id + ' .axis-config'),function(key,val){
         axis_inst = $(val);
         axis_id = axis_inst.data('key');

         axis_label = axis_inst.data('label');
         axis_position = axis_inst.data('position') == 0 ? "left" : "right";
         axis_min = axis_inst.data('min') == "None" ? null : axis_inst.data('min');
         axis_max = axis_inst.data('max') == "None" ? null : axis_inst.data('max');
         axis_points = axis_inst.data('show-plot-points') == "True";
         axis_bars = axis_inst.data('show-plot-bars') == "True";
         axis_lines = axis_inst.data('show-plot-lines') >= 1;
         axis_steps = axis_inst.data('show-plot-lines') >= 2;
         axis_stack = axis_inst.data('stack') == "True";
         axis_fill = axis_inst.data('fill') == "True";
         raxes[axis_id] = {'list_id':k,}
         axes[k] = {'list_id':axis_id, 'label':axis_label, 'position': axis_position, 'min': axis_min, 'max': axis_max, 'points': axis_points, 'lines': axis_lines, 'bars': axis_bars, 'steps': axis_steps, 'stack': axis_stack, 'fill': axis_fill, 'unit': null};
         options.yaxes[k] = {};
         options.yaxes[k].list_id = axis_id;
         options.yaxes[k].label = axis_label;
         options.yaxes[k].position = axis_position;
         //options.yaxes[k].labelWidth = null;
         //options.yaxes[k].reserveSpace = false;
         options.yaxes[k].min = axis_min;
         options.yaxes[k].max = axis_max;
         k++;
     });

     $.each($(legend_table_id + ' .variable-config'),function(key,val){
         val_inst = $(val);
         axis_id = val_inst.data('axis-id')
         raxis_id = raxes[axis_id].list_id
         variable_name = val_inst.data('name');
         variable_key = val_inst.data('key');
         variables[variable_key] = {'color':val_inst.data('color'),'yaxis': raxis_id, 'axis_id': axis_id}
         keys.push(variable_key);
         variable_names.push(variable_name);
         variables[variable_key].label = $(".legendLabel[data-key=" + variable_key + "] .legendLabel-text")[0].textContent.replace(/\s/g, '');
         variables[variable_key].unit = $(".legendUnit[data-key=" + variable_key + "]")[0].textContent.replace(/\s/g, '');
         if (axes[raxis_id].unit == null) {
             axes[raxis_id].unit = variables[variable_key].unit;
         }else if (axes[raxis_id].unit !== variables[variable_key].unit) {
             axes[raxis_id].unit = "";
         }
         options.yaxes[raxis_id].unit = axes[raxes[axis_id].list_id].unit
         options.yaxes[raxis_id].axisLabel = options.yaxes[raxis_id].label.replace(/\s/g, '') + (((typeof options.yaxes[raxis_id].unit != "undefined") && options.yaxes[raxis_id].unit != "" && options.yaxes[raxis_id].unit !=  null) ? " (" + options.yaxes[raxis_id].unit + ")" : '');
     });


     function linearInterpolation (x, x0, y0, x1, y1) {
       var a = (y1 - y0) / (x1 - x0)
       var b = -a * x0 + y0
       return a * x + b
     }

     //Show interpolated value in legend
     function updateLegend() {
         var pos = flotPlot.c2p({left:flotPlot.getOptions().crosshair.lastPosition.x, top:flotPlot.getOptions().crosshair.lastPosition.y});
         var axes = flotPlot.getAxes();

         if (pos.x < axes.xaxis.min || pos.x > axes.xaxis.max ||
             pos.y < axes.yaxis.min || pos.y > axes.yaxis.max) {
             return;
         }

         var i, j, dataset = flotPlot.getData();

         for (i = 0; i < dataset.length; ++i) {
             var series = dataset[i];
             var key = series.key
             // Find the nearest points, x-wise
             for (j = 0; j < series.data.length; ++j) {
                 if (series.data[j][0] > pos.x) {
                     break;
                 }
             }
             // Now Interpolate
             var y,
                 p1 = series.data[j - 1],
                 p2 = series.data[j];
             if (p1 == null && typeof(p2) != "undefined") {
                 y = p2[1];
             } else if (p2 == null && typeof(p1) != "undefined") {
                 y = p1[1];
             } else if (typeof(12) != "undefined" && typeof(p2) != "undefined") {
                 y = p1[1] + (p2[1] - p1[1]) * (pos.x - p1[0]) / (p2[0] - p1[0]);
             }
             if (typeof(y) === "number") {
                 $(legend_value_id+key).text(y.toFixed(2));
             }
         }
     }

     // prepare the chart and display it even without data
     function prepare(){
         // prepare legend table sorter
         if (keys.length > 0) {
             $(legend_table_id).tablesorter({sortList: [[2,0]]});
         };

         // CHECKBOX EVENTS :

         // add onchange function to every checkbox in legend / shows or hides the variable linked to the checked/unchecked checkbox
         $.each(variables,function(key,val){
             $(legend_checkbox_id+key).change(function() {
                 plot.update(true);
                 if ($(legend_checkbox_id+key).is(':checked')){
                     $(legend_checkbox_status_id+key).html(1);
                 }else{
                     $(legend_checkbox_status_id+key).html(0);
                 }
             });
         });
         // add onchange function to 'make_all_none' checkbox in legend / shows or hides all the variable in the chart
         $(legend_checkbox_id+'make_all_none').change(function() {
             if ($(legend_checkbox_id+'make_all_none').is(':checked')){
                 $.each(variables,function(key,val){
                     $(legend_checkbox_status_id+key).html(1);
                     if ($(legend_checkbox_id+key).length > 0) {
                         $(legend_checkbox_id+key)[0].checked = true;
                     }
                 });
             }else{
                 $.each(variables,function(key,val){
                     $(legend_checkbox_status_id+key).html(0);
                     if ($(legend_checkbox_id+key).length > 0) {
                         $(legend_checkbox_id+key)[0].checked = false;
                     }
                  });
             }
             plot.update(true);
          });


         // CORRECTING THE CHART SIZE AND IT'S CONTENTS :

         // expand the chart to the maximum width
         main_chart_area  = $(chart_container_id).closest('.main-chart-area');


         contentAreaHeight = main_chart_area.parent().height();
         mainChartAreaHeight = main_chart_area.height();
         // resize the main chart area if the content height exceed the main chart's
         if (contentAreaHeight>mainChartAreaHeight){
             main_chart_area.height(contentAreaHeight);
         }

         flotPlot = $.plot($(chart_container_id + ' .chart-placeholder'), series, options);
         set_chart_selection_mode();
         // update the plot
         update(true);

         //add info on mouse over a point and position of the mouse
         $(chart_container_id + ' .chart-placeholder').bind("plothover", function (event, pos, item) {
             if(!pos) {
                 //$(".axes-tooltips").hide();
             }
             for (axis in pos) {
                 if (!$("#" + axis + "-tooltip").length) {
                     $("<div id='" + axis + "-tooltip' class='axes-tooltips'></div>").css({
                         position: "absolute",
                         display: "none",
                         border: "1px solid #fdd",
                         padding: "2px",
                         "background-color": "#fee",
                         opacity: 0.90,
                         "z-index": 90,
                         "font-size": "14px"
                     }).appendTo("body");
                 }
             }
             if (item && typeof item.datapoint != 'undefined' && item.datapoint.length > 1) {
                 opts = item.series.xaxis.options;
                 if (opts.mode == "time") {
                     dG = $.plot.dateGenerator(Number(item.datapoint[0].toFixed(0)), opts);
                     dF = $.plot.formatDate(dG, opts.timeformat, opts.monthNames, opts.dayNames);
                     var x = dF,
                         y = item.datapoint[1].toFixed(2);
                 }else {
                     var x = item.datapoint[0].toFixed(2),
                         y = item.datapoint[1].toFixed(2);
                 }
                 y_label = (typeof item.series.label !== 'undefined') ? item.series.label : "T";
                 y_unit = (typeof item.series.unit !== 'undefined') ? item.series.unit : "";
                 $("#tooltip").html(y_label + " (" + x + ") = " + y + " " + y_unit)
                     .css({top: item.pageY+5, left: item.pageX+5, "z-index": 91})
                     .show();
                     //.fadeIn(200);
             } else {
                 $("#tooltip").hide();
             }
             // set Crosshairs
             setCrosshairs(flotPlot, id);

         // mouse leave
         }).bind("mouseleave", function (event, pos, item) {
             if(! flotPlot.getOptions().crosshair.locked) {
                 delCrosshairs(flotPlot);
             }
         // mouse down
         }).bind("mousedown", function (e) {
             var offset = flotPlot.getPlaceholder().offset();
             var plotOffset = flotPlot.getPlotOffset();
             pos={};
             pos.x = Math.max(0, e.pageX - offset.left - plotOffset.left, flotPlot.width());
             pos.y = Math.max(0, e.pageY - offset.top - plotOffset.top, flotPlot.height());
             //pos.x = clamp(0, e.pageX - offset.left - plotOffset.left, flotPlot.width());
             //pos.y = clamp(0, e.pageY - offset.top - plotOffset.top, flotPlot.height());
             flotPlot.getOptions().crosshair.lastPositionMouseDown = pos;
         // mouse up
         }).bind("mouseup", function (e) {
             var offset = flotPlot.getPlaceholder().offset();
             var plotOffset = flotPlot.getPlotOffset();
             pos={};
             pos.x = Math.max(0, e.pageX - offset.left - plotOffset.left, flotPlot.width());
             pos.y = Math.max(0, e.pageY - offset.top - plotOffset.top, flotPlot.height());
             //pos.x = clamp(0, e.pageX - offset.left - plotOffset.left, flotPlot.width());
             //pos.y = clamp(0, e.pageY - offset.top - plotOffset.top, flotPlot.height());
             old_pos = flotPlot.getOptions().crosshair.lastPositionMouseDown;
             if (flotPlot.getOptions().crosshair.locked) {
                 flotPlot.getOptions().crosshair.lastPosition.x = pos.x;
                 flotPlot.getOptions().crosshair.lastPosition.y = pos.y;
                 unlockCrosshairs(flotPlot);
                 setCrosshairs(flotPlot, id);
             } else if (pos.x == old_pos.x && pos.y == old_pos.y) {
                 setCrosshairs(flotPlot, id);
                 lockCrosshairs();
             }
         // plot selected
         }).bind("plotselected", function(event, ranges) {
             pOpt = flotPlot.getOptions();
             // activate zoom y
             if ($(chart_container_id + " .activate_zoom_y").is(':checked')) {
                 for (range in ranges) {
                     if (~range.indexOf('y')) {
                         if (range.match(/\d+/) != null) {
                             y_number = range.match(/\d+/)[0];
                             pOpt.yaxes[y_number-1].min = ranges[range].from;
                             pOpt.yaxes[y_number-1].max = ranges[range].to;
                             pOpt.yaxes[y_number-1].autoScale = "none";
                         }else {
                             pOpt.yaxes[0].min = ranges[range].from;
                             pOpt.yaxes[0].max = ranges[range].to;
                             pOpt.yaxes[0].autoScale = "none";
                         }
                     }
                 }
                 flotPlot.setupGrid(true);
                 flotPlot.draw();
             }

             flotPlot.clearSelection();
             // activate zoom x
             if ($(chart_container_id + " .activate_zoom_x").is(':checked') && ranges.xaxis != null) {
                 if (xaxisVarId == null) {
                     DATA_DISPLAY_TO_TIMESTAMP = ((DATA_TO_TIMESTAMP == ranges.xaxis.to) ? DATA_DISPLAY_TO_TIMESTAMP : ranges.xaxis.to);
                     DATA_DISPLAY_FROM_TIMESTAMP = ((DATA_FROM_TIMESTAMP == ranges.xaxis.from) ? DATA_DISPLAY_FROM_TIMESTAMP : ranges.xaxis.from);
                     if (DATA_DISPLAY_TO_TIMESTAMP < 0 && DATA_DISPLAY_FROM_TIMESTAMP < 0) {DATA_DISPLAY_WINDOW = DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP;}
                     else if (DATA_DISPLAY_TO_TIMESTAMP < 0) {DATA_DISPLAY_WINDOW = DATA_TO_TIMESTAMP - DATA_DISPLAY_FROM_TIMESTAMP;}
                     else if (DATA_DISPLAY_FROM_TIMESTAMP < 0) {DATA_DISPLAY_WINDOW = DATA_DISPLAY_TO_TIMESTAMP - DATA_FROM_TIMESTAMP;}
                     else {DATA_DISPLAY_WINDOW = DATA_DISPLAY_TO_TIMESTAMP-DATA_DISPLAY_FROM_TIMESTAMP;}
                     set_x_axes();
                 }else {
                   pOpt.xaxes[0].min = ranges.xaxis.from;
                   pOpt.xaxes[0].max = ranges.xaxis.to;
                   pOpt.xaxes[0].autoScale = "none";
                   update(true);
                 }
             }
         });

         // Since CSS transforms use the top-left corner of the label as the transform origin,
         // we need to center the y-axis label by shifting it down by half its width.
         // Subtract 20 to factor the chart's bottom margin into the centering.
         var chartTitle = $(chart_container_id + ' .chartTitle');
         chartTitle.css("margin-left", -chartTitle.width() / 2);
         var xaxisLabel = $(chart_container_id + ' .axisLabel.xaxisLabel');
         xaxisLabel.css("margin-left", -xaxisLabel.width() / 2);
         var yaxisLabel = $(chart_container_id + ' .axisLabel.yaxisLabel');
         yaxisLabel.css("margin-top", yaxisLabel.width() / 2 - 20);

         // The download function takes a CSV string, the filename and mimeType as parameters
         // Scroll/look down at the bottom of this snippet to see how download is called
         var download = function(content, fileName, mimeType) {
             var a = document.createElement('a');
             mimeType = mimeType || 'application/octet-stream';

             if (mimeType == 'image/png' && 'download' in a) {
                 a.href = content;
                 a.setAttribute('download', fileName);
                 document.body.appendChild(a);
                 a.click();
                 document.body.removeChild(a);
             } else if (navigator.msSaveBlob) { // IE10
                 navigator.msSaveBlob(new Blob([content], {
                 type: mimeType
                 }), fileName);
             } else if (URL && 'download' in a) { //html5 A[download]
                 a.href = URL.createObjectURL(new Blob([content], {
                   type: mimeType
                 }));
                 a.setAttribute('download', fileName);
                 document.body.appendChild(a);
                 a.click();
                 document.body.removeChild(a);
             } else {
                 location.href = 'data:application/octet-stream,' + encodeURIComponent(content); // only this mime type is supported
             }
         };
         // chrt save csv button
         $(chart_container_id + " .btn.btn-default.chart-save-csv").click(function() {
             // Example data given in question text
             var data = [['Label'], ['Unité'], ['Couleur'], ['Données']];
             mode = flotPlot.getXAxes()[0].options.mode;
             for (s=0; s<series.length; s++){
                 data[0][(s+1)*2-1] = "x";
                 data[1][(s+1)*2-1] = (mode = "time") ? "ms" : "";
                 data[2][(s+1)*2-1] = "";
                 data[0][(s+1)*2] = series[s].label;
                 data[1][(s+1)*2] = series[s].unit;
                 data[2][(s+1)*2] = series[s].color;
                 for (l=0; l<series[s].data.length; l++) {
                     data.push([]);
                     data[3+l][(s+1)*2-1] = series[s].data[l][0]
                     data[3+l][(s+1)*2] = series[s].data[l][1]
                 }
             }

             // Building the CSV from the Data two-dimensional array
             // Each column is separated by ";" and new line "\n" for next row
             var csvContent = '';
             data.forEach(function(infoArray, index) {
               dataString = infoArray.join(';');
               csvContent += index < data.length ? dataString + '\n' : dataString;
             });

             download(csvContent, 'download.csv', 'text/csv;encoding:utf-8');
         });
         // chart save picture button
         $(chart_container_id + " .btn.btn-default.chart-save-picture").click(function() {
             var originalCanvas1 = $(chart_container_id + ' .flot-base')[0]
             var originalCanvas2 = $(chart_container_id + ' .flot-overlay')[0]
             var originalCanvas3 = $(chart_container_id + ' .flot-svg')[0].children[0]
             var ctx = originalCanvas2.getContext("2d");
             ctx.fillStyle = "#FFFFFF";
             ctx.fillRect(0, 0, originalCanvas2.width, originalCanvas2.height);
             var sources = [originalCanvas2, originalCanvas1, originalCanvas3]
             var destinationCanvas = document.getElementById("myCanvas");
             $.plot.composeImages(sources, destinationCanvas)
             //setTimeout(function() {window.open($('#myCanvas')[0].toDataURL('image/png'));}, 500);
             setTimeout(function() {download($('#myCanvas')[0].toDataURL('image/png'), 'image.png', 'image/png');}, 500);
             ctx.fillRect(0, 0, 0, 0);
         });
         // chart reset selection button
         $(chart_container_id + " .btn.btn-default.chart-ResetSelection").click(function() {
             e = jQuery.Event( "click" );
             jQuery(chart_container_id + " .btn.btn-default.chart-ZoomYToFit").trigger(e);
             jQuery(chart_container_id + " .btn.btn-default.chart-ZoomXToFit").trigger(e);
         });
         // chart zoom y to fit button
         $(chart_container_id + " .btn.btn-default.chart-ZoomYToFit").click(function() {
             pOpt = flotPlot.getOptions();
             for (y in pOpt.yaxes){
                 pOpt.yaxes[y].autoScale = "loose";
             }
             update(true);
         });
         // chart zoom x to fit button
         $(chart_container_id + " .btn.btn-default.chart-ZoomXToFit").click(function() {
             if (xaxisVarId == null) {
                 DATA_DISPLAY_FROM_TIMESTAMP = -1;
                 DATA_DISPLAY_TO_TIMESTAMP = -1;
                 DATA_DISPLAY_WINDOW = DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP;
                 set_x_axes();
             }else {
               pOpt = flotPlot.getOptions();
                 pOpt.xaxes[0].autoScale = "exact";
                 update(true);
             }
         });
     }

     // update the chart
     function update(force){
         // PREPARE THE CHART :
         if(!prepared ){
             if($(chart_container_id).is(":visible")){
                 prepared = true;
                 prepare();
             }else{
                 return;
             }
         }
         // UPDATE DATA :
         if($(chart_container_id).is(":visible") || force){
             // only update if plot is visible
             // add the selected data series to the "series" variable
             old_series = series;
             new_data_bool = false;
             series = [];
             start_id = 0;
             j=0;
             jk=1;
             // for each variable
             for (var key in keys){
                 original_key = keys[key];
                 aggregatedtType = document.querySelector(legend_table_id + ' .aggregation-type-option[data-id="' + original_key + '"]');
                 if (aggregatedtType !== null && ! isNaN(parseInt(aggregatedtType.value))) {
                     key = Number(get_aggregated_data(keys[key], DATA_DISPLAY_FROM_TIMESTAMP, DATA_DISPLAY_TO_TIMESTAMP, parseInt(aggregatedtType.value)));
                 }else {
                    key = original_key;
                 }
                 if (!variables.hasOwnProperty(key) && original_key in variables) {
                     variables[key] = variables[original_key]
                 }
                 if (key == original_key) {
                     variables[key].label = $(".legendLabel[data-key=" + original_key + "] .legendLabel-text")[0].textContent.replace(/\s/g, '')
                 }else {
                     variables[key].label = $(".legendLabel[data-key=" + original_key + "] .legendLabel-text")[0].textContent.replace(/\s/g, '') + " " + $(".legendLabel[data-key=" + original_key + "] span")[1].textContent.replace(/\s/g, '');
                 }

                 //key = keys[key];
                 xkey = xaxisVarId;
                 // if the variable checkbox is check, update data
                 if($(legend_checkbox_id+original_key).is(':checked') && typeof(DATA[key]) === 'object'){
                     if (DATA_DISPLAY_TO_TIMESTAMP > 0 && DATA_DISPLAY_FROM_TIMESTAMP > 0){
                         start_id = find_index_sub_gte(DATA[key],DATA_DISPLAY_FROM_TIMESTAMP,0);
                         stop_id = find_index_sub_lte(DATA[key],DATA_DISPLAY_TO_TIMESTAMP,0);
                     }else if (DATA_DISPLAY_FROM_TIMESTAMP > 0 && DATA_DISPLAY_TO_TIMESTAMP < 0){
                         start_id = find_index_sub_gte(DATA[key],DATA_DISPLAY_FROM_TIMESTAMP,0);
                         stop_id = find_index_sub_lte(DATA[key],DATA_TO_TIMESTAMP,0);
                     }else if (DATA_DISPLAY_FROM_TIMESTAMP < 0 && DATA_DISPLAY_TO_TIMESTAMP > 0){
                         if (DATA_DISPLAY_TO_TIMESTAMP < DATA[key][0][0]){continue;}
                         start_id = find_index_sub_gte(DATA[key],DATA_FROM_TIMESTAMP,0);
                         stop_id = find_index_sub_lte(DATA[key],DATA_DISPLAY_TO_TIMESTAMP,0);
                     }else {
                         start_id = find_index_sub_gte(DATA[key],DATA_FROM_TIMESTAMP,0);
                         stop_id = find_index_sub_lte(DATA[key],DATA_TO_TIMESTAMP,0);
                     }
                     if (typeof(start_id) == "undefined") {
                        //console.log('start_id for var id ', key, 'is undefined');
                         continue;
                     }else {
                         chart_data = DATA[key].slice(start_id,stop_id+1);
                     }
                     if (xkey == null) {
                         for (serie in old_series) {
                           if (new_data_bool === false && chart_data.length > 0 && key === old_series[serie]['key'] && chart_data.length !== old_series[serie]['data'].length && (old_series[serie]['data'].length == 0 || chart_data[0][0] !== old_series[serie]['data'][0][0] || chart_data[0][1] !== old_series[serie]['data'][0][1] || chart_data[chart_data.length-1][0] !== old_series[serie]['data'][old_series[serie]['data'].length-1][0] && chart_data[chart_data.length-1][1] !== old_series[serie]['data'][old_series[serie]['data'].length-1][-1])) {
                             new_data_bool = true;
                           }
                         }
                         series.push({"data":chart_data,"color":variables[key].color,"yaxis":variables[key].yaxis+1,"label":variables[key].label,"unit":variables[key].unit, "key":key, "points": {"show": axes[variables[key].yaxis].points,}, "stack": axes[variables[key].yaxis].stack, "bars": {"show": axes[variables[key].yaxis].bars}, "lines": {"show": axes[variables[key].yaxis].lines, "steps": axes[variables[key].yaxis].steps, "fill": axes[variables[key].yaxis].fill,},});
                     }else if (xkey !== null && typeof(DATA[xkey]) === 'object'){
                         if (DATA_DISPLAY_TO_TIMESTAMP > 0 && DATA_DISPLAY_FROM_TIMESTAMP > 0){
                             start_xid = find_index_sub_gte(DATA[xkey],DATA_DISPLAY_FROM_TIMESTAMP,0);
                             stop_xid = find_index_sub_lte(DATA[xkey],DATA_DISPLAY_TO_TIMESTAMP,0);
                         }else if (DATA_DISPLAY_FROM_TIMESTAMP > 0 && DATA_DISPLAY_TO_TIMESTAMP < 0){
                             start_xid = find_index_sub_gte(DATA[xkey],DATA_DISPLAY_FROM_TIMESTAMP,0);
                             stop_xid = find_index_sub_lte(DATA[xkey],DATA_TO_TIMESTAMP,0);
                         }else if (DATA_DISPLAY_FROM_TIMESTAMP < 0 && DATA_DISPLAY_TO_TIMESTAMP > 0){
                             if (DATA_DISPLAY_TO_TIMESTAMP < DATA[key][0][0]){continue;}
                             start_xid = find_index_sub_gte(DATA[xkey],DATA_FROM_TIMESTAMP,0);
                             stop_xid = find_index_sub_lte(DATA[xkey],DATA_DISPLAY_TO_TIMESTAMP,0);
                         }else {
                             start_xid = find_index_sub_gte(DATA[xkey],DATA_FROM_TIMESTAMP,0);
                             stop_xid = find_index_sub_lte(DATA[xkey],DATA_TO_TIMESTAMP,0);
                         }
                         if (typeof(start_xid) == "undefined") {
                             continue;
                         }else {
                             chart_x_data = DATA[xkey].slice(start_xid,stop_xid+1);
                         };
                         new_data=[];
                         if (chart_data.length > 0 && chart_x_data.length > 0){
                             chart_data_min = chart_data[0][1]
                             chart_data_max = chart_data[0][1]
                             x_data_min = chart_x_data[0][1]
                             x_data_max = chart_x_data[0][1]
                             ix=0;
                             for (iy=0; iy < chart_data.length; iy++) {
                                 xf=0;
                                 if (chart_x_data.length > 1){
                                     while (ix < chart_x_data.length && xf == 0) {
                                         if (chart_x_data[ix][0] >= chart_data[iy][0]) {
                                             if (ix == 0) {
                                                 fx = linearInterpolation(chart_data[iy][0], chart_x_data[ix][0], chart_x_data[ix][1], chart_x_data[ix+1][0], chart_x_data[ix+1][1]);
                                             }else {
                                                 fx = linearInterpolation(chart_data[iy][0], chart_x_data[ix-1][0], chart_x_data[ix-1][1], chart_x_data[ix][0], chart_x_data[ix][1]);
                                             }
                                             new_data.push([fx,chart_data[iy][1]]);
                                             chart_data_min = Math.min(chart_data_min, chart_data[iy][1])
                                             chart_data_max = Math.max(chart_data_max, chart_data[iy][1])
                                             x_data_min = Math.min(x_data_min, fx)
                                             x_data_max = Math.max(x_data_max, fx)
                                             xf=1;
                                             ix-=1;
                                         }
                                         ix+=1;
                                     }
                                     if (xf == 0) {
                                         fx = linearInterpolation(chart_data[iy][0], chart_x_data[chart_x_data.length-2][0], chart_x_data[chart_x_data.length-2][1], chart_x_data[chart_x_data.length-1][0], chart_x_data[chart_x_data.length-1][1]);
                                         new_data.push([fx,chart_data[iy][1]]);
                                         chart_data_min = Math.min(chart_data_min, chart_data[iy][1])
                                         chart_data_max = Math.max(chart_data_max, chart_data[iy][1])
                                         x_data_min = Math.min(x_data_min, fx)
                                         x_data_max = Math.max(x_data_max, fx)
                                         xf=1;
                                     }
                                 }else if (chart_x_data.length > 0){
                                     new_data.push([chart_x_data[0][1],chart_data[iy][1]]);
                                     chart_data_min = Math.min(chart_data_min, chart_data[iy][1])
                                     chart_data_max = Math.max(chart_data_max, chart_data[iy][1])
                                     iy = chart_data.length;
                                 }
                             }
                         }else {
                             chart_data_min = null;
                             chart_data_max = null;
                         }
                         if (new_data.length > 0){
                             j += 1;
                             //plot Y with different axis
                             for (serie in old_series) {
                               if (new_data_bool === false && new_data.length > 0 && key === old_series[serie]['key'] && new_data.length !== old_series[serie]['data'].length && (old_series[serie]['data'].length == 0 || new_data[0][0] !== old_series[serie]['data'][0][0] || new_data[0][1] !== old_series[serie]['data'][0][1] || new_data[new_data.length-1][0] !== old_series[serie]['data'][old_series[serie]['data'].length-1][0] && new_data[new_data.length-1][1] !== old_series[serie]['data'][old_series[serie]['data'].length-1][-1] || chart_x_data[0][0] !== old_series[serie]['xdata'][0][0] || chart_x_data[0][1] !== old_series[serie]['xdata'][0][1] || chart_x_data[chart_x_data.length-1][0] !== old_series[serie]['xdata'][old_series[serie]['xdata'].length-1][0] && chart_x_data[chart_x_data.length-1][1] !== old_series[serie]['xdata'][old_series[serie]['xdata'].length-1][-1])) {
                                 new_data_bool = true;
                               }
                             }
                             series.push({"data":new_data, "xdata":chart_x_data,"color":variables[key].color,"yaxis":variables[key].yaxis+1,"label":variables[key].label,"unit":variables[key].unit,"chart_data_min":chart_data_min,"chart_data_max":chart_data_max,"x_data_min":x_data_min,"x_data_max":x_data_max, "key":key, "points": {"show": axes[variables[key].yaxis].points,}, "stack": axes[variables[key].yaxis].stack, "bars": {"show": axes[variables[key].yaxis].bars}, "lines": {"show": axes[variables[key].yaxis].lines, "steps": axes[variables[key].yaxis].steps, "fill": axes[variables[key].yaxis].fill,},});
                         }
                     }
                 }
                 jk += 1;
             }
             if (new_data_bool || old_series.length == 0 || series.length == 0 || old_series.length != series.length || force) {

               //update y window
               pOpt = flotPlot.getOptions();
               if (xaxisVarId == null) {
                 if (DATA_DISPLAY_TO_TIMESTAMP > 0 && DATA_DISPLAY_FROM_TIMESTAMP > 0){
                       pOpt.xaxes[0].min = DATA_DISPLAY_FROM_TIMESTAMP;
                       pOpt.xaxes[0].max = DATA_DISPLAY_TO_TIMESTAMP;

                   }else if (DATA_DISPLAY_FROM_TIMESTAMP > 0 && DATA_DISPLAY_TO_TIMESTAMP < 0){
                       pOpt.xaxes[0].min = DATA_DISPLAY_FROM_TIMESTAMP;
                       pOpt.xaxes[0].max = DATA_TO_TIMESTAMP;
                   }else if (DATA_DISPLAY_FROM_TIMESTAMP < 0 && DATA_DISPLAY_TO_TIMESTAMP > 0){
                       pOpt.xaxes[0].min = DATA_FROM_TIMESTAMP;
                       pOpt.xaxes[0].max = DATA_DISPLAY_TO_TIMESTAMP;
                   }else{
                       pOpt.xaxes[0].min = DATA_FROM_TIMESTAMP;
                       pOpt.xaxes[0].max = DATA_TO_TIMESTAMP;
                   }
                   pOpt.xaxes[0].key=0;
               }else {


                   // Reset min and max for xaxis and yaxes when no data
                   allYAxesEmpty = true;
                   for (y = 0;y < pOpt.yaxes.length;y++){
                       if (j != 0){
                           yAxesEmpty = true;
                           for (k = 1;k <= j;k++){
                               S = series[k-1];
                               if (S['yaxis']-1 == y) {yAxesEmpty = false;}
                           }
                           if (yAxesEmpty == true) {
                               pOpt.yaxes[y].min = null;
                               pOpt.yaxes[y].max = null;
                           }else {allYAxesEmpty = false;}
                       }else {
                           pOpt.yaxes[y].min = null;
                           pOpt.yaxes[y].max = null;
                           pOpt.xaxes[0].min = null;
                           pOpt.xaxes[0].max = null;
                       }
                   }
                   if (allYAxesEmpty == true) {
                       pOpt.xaxes[0].min = null;
                       pOpt.xaxes[0].max = null;
                   }

                   pOpt.xaxes[0].key=xkey
               }
               // update flot plot
               flotPlot.setData(series);
               flotPlot.setupGrid(true);
               flotPlot.draw();

               // Change the color of the axis
               if (xaxisVarId !== null && jk != 1){
                   for (k = 1;k <= jk;k++){
                       S = series[k-1];
                       if (typeof S !== 'undefined') {
                           $(chart_container_id + ' .axisLabels.y' + S['yaxis'] + 'Label').css('fill',S['color'])
                           $(chart_container_id + ' .flot-y' + S['yaxis'] + '-axis text').css('fill',S['color'])
                       }
                   }
               }
             }
         }
     }

     // resize the chart when the navigator window dimensiosn changed
     function resize() {
         if (typeof(flotPlot) !== 'undefined') {
             flotPlot.resize();
             flotPlot.setupGrid(true);
             flotPlot.draw();
         }
     }
 }

 // Gauge
 /**
  * A 240° circular chart with a data range
  * @param {number} id The container id where to display the chart
  * @param {numer} min_value Range minimum value
  * @param {number} max_value Range maximum value
  * @param {Array<object>} threshold_values Datas
  */
 function Gauge(id, min_value, max_value, threshold_values){
     var options = {
         series: {
             gauges: {
                 show: true,
                 frame: {
                     show: false
                 },
                 gauge: {
                     min: min_value,
                     max: max_value,
                 },
                 cell: {
                     border: {
                         show: false,
                     },
                 },
                 label: {
                     show: false,
                 },
                 threshold: {
                     values: threshold_values,
                 }
             },
         },
     },
     series = [],		// just the active data series
     keys   = [],		// list of variable keys (ids)
     variable_names = [], // list of all variable names
     variables = {},     // list of all variable
     flotPlot,			// handle to plot
     prepared = false,	// is the chart prepared

     // chart container areas
     chart_container_id = '#chart-container-'+id, // the HTML element where the chart is displayed
     legend_table_id = '#chart-legend-table-' + id, // table of legend
     legend_checkbox_id = '#chart-legend-checkbox-' + id + '-', // legend of checkbox, when checked will display the linked variable in the chart
     legend_checkbox_status_id = '#chart-legend-checkbox-status-' + id + '-', // legend of checkbox status

     // the object
     plot = this;

     // public functions
     plot.update 			= update;
     plot.prepare 			= prepare;
     plot.resize 			= resize;

     //getter
     plot.getSeries 			= function () { return series ;};
     plot.getFlotObject		= function () { return flotPlot;};
     plot.getKeys			= function (){ return keys;};
     plot.getVariableNames	= function (){ return variable_names;};

     plot.getInitStatus		= function () { if(InitDone){return InitRetry}else{return false;}};
     plot.getId				= function () {return id;};
     plot.getChartContainerId= function () {return chart_container_id;};

     // init data
     val_id=$(chart_container_id).data('id');
     val_inst=$(".variable-config[data-id=" + val_id + "]")
     variable_name = $(val_inst).data('name');
     variable_key = $(val_inst).data('key');
     variables[variable_key] = {'color':$(val_inst).data('color'),'yaxis':1}
     keys.push(variable_key);
     variable_names.push(variable_name);
     variables[variable_key].label = variable_name
     variables[variable_key].unit = $(val_inst).data('unit');

     //options["series"]["gauges"]["gauge"] = {"background": {"color": $(val_inst).data('color')}}

     // prepare the chart and display it even without data
     function prepare(){
     }

     // update the chart
     function update(force){
         // prepare the chart
         prepared = true;
         if(prepared && ($(chart_container_id).is(":visible") || force)){
             // only update if plot is visible
             // add the selected data series to the "series" variable
             series = [];
             for (var key in keys){
                 key = keys[key];
                 if (key in DATA) {
                     data=[[min_value, DATA[key][DATA[key].length - 1][1]]]
                     series.push({"data":data, "label":variables[key].label});
                 }
             }
             // draw the chart if we have data
             if (series.length > 0) {
                 var plotCanvas = $('<div></div>');
                 elem = $(chart_container_id + ' .chart-placeholder');

                 //mhw = Math.min(elem.parent().height() * 1.3, elem.parent().width());
                 mhw = elem.parent().width();
                 elem.parent().parent().css('height', mhw/1.3);
                 elem.parent().parent().find('.loading-gauge').text("");
                 elem.parent().parent().find('.gauge-title').css("display", "inherit");

                 fontScale = parseInt(30, 10) / 100;
                 fontSize = Math.min(mhw / 5, 100) * fontScale;

                 options["series"]["gauges"]["value"] = {"font": {"size": fontSize}};

                 var plotCss = {
                     top: '0px',
                     margin: 'auto',
                     position: 'relative',
                     height: (elem.parent().height() * 0.9) + 'px',
                     width: mhw + 'px'
                 };

                 elem.css(plotCss)
                 //elem.append(plotCanvas);
                 flotPlot = $.plot(elem, series, options);
             }
         }
     }

     // resize the chart when the navigator window dimensiosn changed
     function resize() {
         if (typeof(flotPlot) !== 'undefined') {
             flotPlot.resize();
             update();
         }
     }
 }

 // Pie
 function labelFormatter(label, series) {
     return "<div style='font-size:8pt; text-align:center; padding:2px; color:" + series.color + ";'>" + label + "<br/>" + Math.round(series.percent) + "%</div>";
     //return "<div style='font-size:8pt; text-align:center; padding:2px; color:" + series.color + ";'>" + label + "<br/>" + Math.round(series.percent) + "%<br/>" + series.data[0][1] + " " + series.unit + "</div>";
 }
 /**
  * A chart with radius and innierRadius options
  * @param {number} id The container id where to display the chart
  * @param {number} radius The pie radius
  * @param {number} innerRadius The pie inner radius
  */
 function Pie(id, radius, innerRadius){
     var options = {
         series: {
             pie: {
                 show: true,
                 innerRadius: innerRadius,
                 label: {
                     show: true,
                     radius: radius,
                     formatter: labelFormatter,
                     background:{
                       opacity: 0.5,
       								 color: "#FFF"
                     }
                     //threshold: 0.05
                 }
             }
         },
         legend: {
             show: false
         },
         grid: {
             hoverable: true,
             clickable: true
         },
     },
     series = [],		// just the active data series
     keys   = [],		// list of variable keys (ids)
     variable_names = [], // list of all variable names
     variables = {},     // list of all variable
     flotPlot,			// handle to plot
     prepared = false,	// is the chart prepared
     chart_container_id = '#chart-container-'+id, // the HTML element where the chart is displayed
     legend_table_id = '#chart-legend-table-' + id, // table of legend
     legend_checkbox_id = '#chart-legend-checkbox-' + id + '-', // legend of checkbox, when checked will display the linked variable in the chart
     legend_checkbox_status_id = '#chart-legend-checkbox-status-' + id + '-', // legend of checkbox status
     plot = this; // the object

     // public functions
     plot.update 			= update;
     plot.prepare 			= prepare;
     plot.resize 			= resize;
     plot.updateLegend 		= updateLegend;

     // getter
     plot.getSeries 			= function () { return series ;};
     plot.getFlotObject		= function () { return flotPlot;};
     plot.getKeys			= function (){ return keys;};
     plot.getVariableNames	= function (){ return variable_names;};

     plot.getInitStatus		= function () { if(InitDone){return InitRetry;}else{return false;}};
     plot.getId				= function () {return id;};
     plot.getChartContainerId= function () {return chart_container_id;};

     // init data
     $.each($(legend_table_id + ' .variable-config'),function(key,val){
         val_inst = $(val);
         variable_name = val_inst.data('name');
         variable_key = val_inst.data('key');
         variables[variable_key] = {'color':val_inst.data('color'),'yaxis':1};
         keys.push(variable_key);
         variable_names.push(variable_name);
         unit = "";
         label = "";
         $.each($(legend_table_id + ' .legendSeries'),function(kkey,val){
             val_inst = $(val);
             if (variable_key == val_inst.find(".variable-config").data('key')){
                 variables[variable_key].label = val_inst.find(".legendLabel").text().replace(/\s/g, '');
                 variables[variable_key].unit = val_inst.find(".legendUnit").text().replace(/\s/g, '');
             }
         });
     });

     //Show interpolated value in legend
     function updateLegend() {
         var pos = flotPlot.c2p({left:flotPlot.getOptions().crosshair.lastPosition.x, top:flotPlot.getOptions().crosshair.lastPosition.y});
         var axes = flotPlot.getAxes();

         if (pos.x < axes.xaxis.min || pos.x > axes.xaxis.max ||
             pos.y < axes.yaxis.min || pos.y > axes.yaxis.max) {
             return;
         }

         var i, j, dataset = flotPlot.getData();

         for (i = 0; i < dataset.length; ++i) {
             var series = dataset[i];
             var key = series.key
             // Find the nearest points, x-wise
             for (j = 0; j < series.data.length; ++j) {
                 if (series.data[j][0] > pos.x) {
                     break;
                 }
             }
             // Now Interpolate
             var y,
                 p1 = series.data[j - 1],
                 p2 = series.data[j];
             if (p1 == null && typeof(p2) != "undefined") {
                 y = p2[1];
             } else if (p2 == null && typeof(p1) != "undefined") {
                 y = p1[1];
             } else if (typeof(12) != "undefined" && typeof(p2) != "undefined") {
                 y = p1[1] + (p2[1] - p1[1]) * (pos.x - p1[0]) / (p2[0] - p1[0]);
             }
             if (typeof(y) === "number") {
                 $(legend_value_id+key).text(y.toFixed(2));
             }
         }
     }

     // prepare the chart and display it even without data
     function prepare(){
         // prepare legend table sorter
         if (keys.length > 0) {
             $(legend_table_id).tablesorter({sortList: [[2,0]]});
         }

         // add onchange function to every checkbox in legend / shows or hides the variable linked to the checked/unchecked checkbox
         $.each(variables,function(key,val){
             $(legend_checkbox_id+key).change(function() {
                 plot.update(true);
                 if ($(legend_checkbox_id+key).is(':checked')){
                     $(legend_checkbox_status_id+key).html(1);
                 }else{
                     $(legend_checkbox_status_id+key).html(0);
                 }
             });
         });
         // add onchange function to make_all_none checkbox in legend / shows or hides the chart's variables
         $(legend_checkbox_id+'make_all_none').change(function() {
             if ($(legend_checkbox_id+'make_all_none').is(':checked')){
                 $.each(variables,function(key,val){
                     $(legend_checkbox_status_id+key).html(1);
                     $(legend_checkbox_id+key)[0].checked = true;
                 });
             }else{
                 $.each(variables,function(key,val){
                     $(legend_checkbox_status_id+key).html(0);
                     $(legend_checkbox_id+key)[0].checked = false;
                  });
             }
             plot.update(true);
         });
         // expand the pie to the maximum width
         main_chart_area = $(chart_container_id).closest('.main-chart-area');


         contentAreaHeight = main_chart_area.parent().height();
         mainChartAreaHeight = main_chart_area.height();

         // resize the main chart area if the content height exceed the main chart's
         if (contentAreaHeight>mainChartAreaHeight){
             main_chart_area.height(contentAreaHeight);
         }

         //add info on mouse over a slice
         $(chart_container_id + ' .chart-placeholder').bind("plothover", function (event, pos, item) {
             var eventDoc, doc, body;

            event = window.event; // IE-ism

            // If pageX/Y aren't available and clientX/Y are,
            // calculate pageX/Y - logic taken from jQuery.
            // (This is to support old IE)
            if (event.pageX == null && event.clientX != null) {
                eventDoc = (event.target && event.target.ownerDocument) || document;
                doc = eventDoc.documentElement;
                body = eventDoc.body;

                event.pageX = event.clientX +
                    (doc && doc.scrollLeft || body && body.scrollLeft || 0) -
                    (doc && doc.clientLeft || body && body.clientLeft || 0);
                event.pageY = event.clientY +
                    (doc && doc.scrollTop  || body && body.scrollTop  || 0) -
                    (doc && doc.clientTop  || body && body.clientTop  || 0 );
            }

             if (item && typeof item.datapoint != 'undefined' && item.datapoint.length > 1) {
                 var x = item.datapoint[0].toFixed(2),
                     y = item.datapoint[1][0][1].toFixed(2);
                 y_label = (typeof item.series.label !== 'undefined') ? item.series.label : "T";
                 y_unit = (typeof item.series.unit !== 'undefined') ? item.series.unit : "";
                 $("#tooltip").html(y_label + " (" + x + " %) = " + y + " " + y_unit)
                     .css({top: event.pageY+5, left: event.pageX+5, "z-index": 91})
                     .show();
                     //.fadeIn(200);
             } else {
                 $("#tooltip").hide();
             }
         })

         // Since CSS transforms use the top-left corner of the label as the transform origin,
         // we need to center the y-axis label by shifting it down by half its width.
         // Subtract 20 to factor the chart's bottom margin into the centering.
         var chartTitle = $(chart_container_id + ' .chartTitle');
         chartTitle.css("margin-left", -chartTitle.width() / 2);
         var xaxisLabel = $(chart_container_id + ' .axisLabel.xaxisLabel');
         xaxisLabel.css("margin-left", -xaxisLabel.width() / 2);
         var yaxisLabel = $(chart_container_id + ' .axisLabel.yaxisLabel');
         yaxisLabel.css("margin-top", yaxisLabel.width() / 2 - 20);

         // draw the chart if we have data
         if (series.length > 0) {
             flotPlot = $.plot($(chart_container_id + ' .chart-placeholder'), series, options);
             // update the plot
             update(false);
         }else {
             //prepared = false;
         }
     }

     // update the chart
     function update(force){
         // prepare the chart
         if(!prepared ){
             if($(chart_container_id).is(":visible")){
                 prepared = true;
                 prepare();
             }else{
                 return;
             }
         }
         // update the chart
         if(prepared && ($(chart_container_id).is(":visible") || force)){
             // only update if plot is visible
             // add the selected data series to the "series" variable
             series = [];
             for (var key in keys){
                 key = keys[key];
                 if($(legend_checkbox_id+key).is(':checked') && typeof(DATA[key]) === 'object'){
                     series.push({"data":DATA[key][DATA[key].length - 1], "label":variables[key].label,"unit":variables[key].unit, "color":variables[key].color});
                 }
             }
             if (series.length > 0 || force) {
                 if (typeof flotPlot !== 'undefined') {
                     // update flot plot
                     flotPlot.setData(series);
                     flotPlot.setupGrid(true);
                     flotPlot.draw();
                 }else {
                     flotPlot = $.plot($(chart_container_id + ' .chart-placeholder'), series, options)
                 }
             }
         }
     }

     // resize the chart when the navigator window dimensiosn changed
     function resize() {
         if (typeof(flotPlot) !== 'undefined') {
             flotPlot.resize();
             flotPlot.setupGrid(true);
             flotPlot.draw();
         }
     }
 }


 //                             -----------------------------------------------------------
 //                                                    Charts Settings
 //                             -----------------------------------------------------------

 // CHART SELECTION :
 /**
  * Depending on the checked check box, zoom x or y activated for each x y axes chart
  * @returns void
  */
 function set_chart_selection_mode(){

     // ZOOM MODE :

     var mode = "";
     $.each($('.xy-chart-container'),function(key,val){
         // get identifier of the chart
         id = val.id.substring(19);

         // active the zoom mode according to the checked checkbox
         if ($('#xy-chart-container-' + id +' .activate_zoom_x').is(':checked') && $('#xy-chart-container-' + id +' .activate_zoom_y').is(':checked')){
             mode = "xy";
         }else if($('#xy-chart-container-' + id +' .activate_zoom_y').is(':checked')){
             mode = "y";
         }else if($('#xy-chart-container-' + id +' .activate_zoom_x').is(':checked')){
             mode = "x";
         }
         $.each(PyScadaPlots,function(plot_id){
             if(typeof(PyScadaPlots[plot_id].getFlotObject()) !== 'undefined' && PyScadaPlots[plot_id].getId() === id){
                 PyScadaPlots[plot_id].getFlotObject().getOptions().selection.mode = mode;
             }
         });
     });
     $.each($('.chart-container'),function(key,val){
         // get identifier of the chart
         id = val.id.substring(16);

         // active the zoom mode according to the checked checkbox
         if ($('#chart-container-' + id +' .activate_zoom_x').is(':checked') && $('#chart-container-' + id +' .activate_zoom_y').is(':checked')){
             mode = "xy";
         }else if($('#chart-container-' + id +' .activate_zoom_y').is(':checked')){
             mode = "y";
         }else if($('#chart-container-' + id +' .activate_zoom_x').is(':checked')){
             mode = "x";
         }
         $.each(PyScadaPlots,function(plot_id){
             if(typeof(PyScadaPlots[plot_id].getFlotObject()) !== 'undefined' && PyScadaPlots[plot_id].getId() === id){
                 PyScadaPlots[plot_id].getFlotObject().getOptions().selection.mode = mode;
             }
         });
     });
 }


 // X AXES
 /**
  * For each chart container, update charts then update timeline
  * @returns void
  */
 function set_x_axes(){
     if(!progressbar_resize_active){
         updatePyScadaPlots(true);
         // update the progressbar
         update_timeline();
     }
 }


 // UPDATE TIMELINE
 /**
  * Update the timeline axe depending on data timestamp variables
  * @returns void
  */
 function update_timeline(){
     if (DATA_DISPLAY_TO_TIMESTAMP < 0){
         $('#timeline-time-to-label').html("");
         min_to = 0;
     }else{
         //var min_to = ((DATA_TO_TIMESTAMP - DATA_DISPLAY_TO_TIMESTAMP)/60/1000);
         //$('#timeline-time-to-label').html("-" + min_to.toPrecision(3) + "min");
         var date = new Date(DATA_DISPLAY_TO_TIMESTAMP);
         $("#timeline-time-to-label").html(date.toLocaleString());
     }
     var min_full = ((DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP)/60/1000);
     if (DATA_DISPLAY_FROM_TIMESTAMP < 0 ){
         var min_from = Math.min(min_full,((DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP)/60/1000));
         $('#timeline-time-from-label').html("");
     }else{
         var min_from = Math.min(min_full,((DATA_TO_TIMESTAMP - DATA_DISPLAY_FROM_TIMESTAMP)/60/1000));
         //$('#timeline-time-from-label').html("-" + min_from.toPrecision(3) + "min");
         var date = new Date(DATA_DISPLAY_FROM_TIMESTAMP);
         $("#timeline-time-from-label").html(date.toLocaleString());
     }
     if (DATA_DISPLAY_FROM_TIMESTAMP < 0 && DATA_DISPLAY_TO_TIMESTAMP < 0){
         $('#timeline').css("width", "100%");
         $('#timeline').css("left", "0px");
     }else{
         $('#timeline').css("width", (Math.min(100,(DATA_DISPLAY_WINDOW/60/1000/min_full * 100)).toString()) + "%");
         $('#timeline').css("left",Math.max(0,Math.min((100-(min_from/min_full * 100)),100)).toString() + "%");
     }
     //$('#timeline-time-left-label').html("-" + min_full.toPrecision(3) + "min");
     //var date = new Date(DATA_FROM_TIMESTAMP);
     //$("#timeline-time-left-label").html(date.toLocaleString());

     // Update DateTime pickers
     if ($("#" + window.location.hash.substr(1) + ".show_daterangepicker").length || $("#" + window.location.hash.substr(1) + ".show_timeline").length) {
         daterange_set(moment(DATA_FROM_TIMESTAMP), moment(DATA_TO_TIMESTAMP));
     }
     if (DATERANGEPICKER_SET == false) {
         set_datetimepicker();
     }
 }


// Date range picker
 /**
  * Set the date time range picker
  * @returns void
  */
 function set_datetimepicker() {
     if ($(".show_daterangepicker").length) {
         $('#daterange').daterangepicker({
             "showDropdowns": true,
             "timePicker": true,
             "timePicker24Hour": true,
             "timePickerSeconds": true,
             ranges: {
                 'Last 10 Minutes': [moment().subtract(10, 'minutes'), moment()],
                 'Last 30 Minutes': [moment().subtract(30, 'minutes'), moment()],
                 'Last Hour': [moment().subtract(1, 'hours'), moment()],
                 'Last 2 Hour': [moment().subtract(2, 'hours'), moment()],
                 'Last 6 Hour': [moment().subtract(6, 'hours'), moment()],
                 'Last 12 Hour': [moment().subtract(12, 'hours'), moment()],
                 'Today': [moment().startOf('day'), moment()],
                 'Yesterday': [moment().subtract(1, 'days').startOf('day'), moment().subtract(1, 'days').endOf('day')],
                 'Last 7 Days': [moment().subtract(6, 'days'), moment()],
                 'Last 30 Days': [moment().subtract(29, 'days'), moment()],
                 'This Month': [moment().startOf('month'), moment()],
                 'Previous Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
                 'Last Month': [moment().subtract(1, 'month'), moment()],
                 'Last 2 Month': [moment().subtract(2, 'month'), moment()],
                 'Last 6 Month': [moment().subtract(6, 'month'), moment()],
                 'This Year': [moment().startOf('year'), moment()],
                 'Previous Year': [moment().subtract(1, 'year').startOf('year'), moment().subtract(1, 'year').endOf('year')],
                 'Last Year': [moment().subtract(1, 'year'), moment()],
             },
             "locale": {
                 "format": daterange_format,
                 "separator": " - ",
                 "applyLabel": "Apply",
                 "cancelLabel": "Cancel",
                 "fromLabel": "From",
                 "toLabel": "To",
                 "customRangeLabel": "Custom",
                 "weekLabel": "W",
                 "daysOfWeek": [
                     "Mo",
                     "Tu",
                     "We",
                     "Th",
                     "Fr",
                     "Sa",
                     "Su",
                 ],
                 "monthNames": [
                     "January",
                     "February",
                     "March",
                     "April",
                     "May",
                     "June",
                     "July",
                     "August",
                     "September",
                     "October",
                     "November",
                     "December"
                 ],
                 "firstDay": 1
             },
             "alwaysShowCalendars": true,
             "linkedCalendars": false,
             "startDate": moment(),
             "endDate": moment().subtract(2, 'hours'),
             "opens": "left"
         }, function(start, end, label) {
             LOADING_PAGE_DONE = 0;
             set_loading_state(5, 0);
             daterange_cb(start, end);
             DATA_INIT_STATUS++;
             DATA_FROM_TIMESTAMP = start.unix() * 1000;
             if (label.indexOf('Last') !== -1 || label.indexOf('Today') !== -1 || label.indexOf('This Month') !== -1 || label.indexOf('This Year') !== -1) {
                 PREVIOUS_AUTO_UPDATE_ACTIVE_STATE = true;
             }else {
                 PREVIOUS_AUTO_UPDATE_ACTIVE_STATE = false;
             }
             DATA_TO_TIMESTAMP = Math.min(end.unix() * 1000, SERVER_TIME);
             DATA_BUFFER_SIZE = DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP;
             INIT_CHART_VARIABLES_DONE = false;
             $('.loadingAnimation').show()
         });
         $('#daterange').on('show.daterangepicker', function(ev, picker) {
             PREVIOUS_AUTO_UPDATE_ACTIVE_STATE = AUTO_UPDATE_ACTIVE
             PREVIOUS_END_DATE = moment.min(picker.endDate, moment()).unix();
             if($('.AutoUpdateButton').bootstrapSwitch('state') && AUTO_UPDATE_ACTIVE){
                 auto_update_click();
             };
         });
         $('#daterange').on('hide.daterangepicker', function(ev, picker) {
             if(!$('.AutoUpdateButton').bootstrapSwitch('state') && PREVIOUS_AUTO_UPDATE_ACTIVE_STATE){
                 auto_update_click();
             };
             DATA_DISPLAY_FROM_TIMESTAMP = -1;
             DATA_DISPLAY_TO_TIMESTAMP = -1;
             DATA_DISPLAY_WINDOW = DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP;
             set_x_axes();
         });
     }
     DATERANGEPICKER_SET = true;
}



 //                             -----------------------------------------------------------
 //                                           Charts and Color's Functions
 //                             -----------------------------------------------------------

 // UPDATE :
 /**
  * Draw as many charts as requested
  * @param {boolean} force
  * @returns void
  */
 function updatePyScadaPlots(force=false) {
     $.each(PyScadaPlots,function(plot_id){
         var self = this, doBind = function() {
             PyScadaPlots[plot_id].update(force);
             PyScadaPlots[plot_id].resize();
         };
         $.browserQueue.add(doBind, this);
     });
 }

 // CROSSHAIRS :

 // Set Crosshairs
 /**
  * Set crosshairs on 'flotPlot'
  * @param {object} flotPlot The chart
  * @param {*} id
  * @returns void
  */
 function setCrosshairs(flotPlot, id) {
     //test if function setCrosshairs exist in hooks.drawOverlay before add it
     $('.chart-legend-value-' + id).removeClass('type-numeric');
     pOpt=flotPlot.getOptions();
     $.each(PyScadaPlots,function(plot_id){
         if(typeof(pOpt.crosshair) !== 'undefined' && pOpt.crosshair.lastPosition.x !== -1  && pOpt.crosshair.lastPosition.x !== 0 && !pOpt.crosshair.locked) {
             if(typeof(PyScadaPlots[plot_id].getFlotObject()) !== 'undefined' && typeof(PyScadaPlots[plot_id].getFlotObject().getOptions) !== 'undefined' && PyScadaPlots[plot_id].getFlotObject().getOptions().xaxes.length === pOpt.xaxes.length){
                 if (PyScadaPlots[plot_id].getFlotObject().getOptions().xaxes.length === 1 && pOpt.xaxes.length === 1 && PyScadaPlots[plot_id].getFlotObject().getOptions().xaxes[0].key === pOpt.xaxes[0].key) {
                     PyScadaPlots[plot_id].getFlotObject().setCrosshair(flotPlot.c2p({left:pOpt.crosshair.lastPosition.x, top:pOpt.crosshair.lastPosition.y}))
                     $('.chart-legend-value-' + PyScadaPlots[plot_id].getId()).removeClass('type-numeric');
                     setTimeout(PyScadaPlots[plot_id].updateLegend(), 50);
                     if (PyScadaPlots[plot_id].getId() == id) {
                         PyScadaPlots[plot_id].getFlotObject().getOptions().crosshair.mode = 'xy';
                     }else {
                         PyScadaPlots[plot_id].getFlotObject().getOptions().crosshair.mode = 'x';
                     }
                 }else {
                     PyScadaPlots[plot_id].getFlotObject().setCrosshair();
                     PyScadaPlots[plot_id].getFlotObject().getOptions().crosshair.mode = 'xy';
                     $('.chart-legend-value-' + PyScadaPlots[plot_id].getId()).addClass('type-numeric');
                 }
             }
         }
     });
 }
 // Delete Crosshairs
 /**
  * Delete every crosshairs on 'flotPlot'
  * @param {object} flotPlot The chart
  * @returns void
  */
 function delCrosshairs(flotPlot) {
     $.each(PyScadaPlots,function(plot_id){
         if (typeof PyScadaPlots[plot_id].getFlotObject() !== 'undefined' && typeof(PyScadaPlots[plot_id].getFlotObject().getOptions) !== 'undefined' && typeof(PyScadaPlots[plot_id].getFlotObject().setCrosshair) !== 'undefined') {
             PyScadaPlots[plot_id].getFlotObject().setCrosshair();
             PyScadaPlots[plot_id].getFlotObject().getOptions().crosshair.mode = 'xy';
         }
         $('.chart-legend-value-' + PyScadaPlots[plot_id].getId()).addClass('type-numeric');
     });
 }
 // Unlock Crosshairs
 /**
  * Unlock each crosshairs on 'flotPlot'
  * @param {object} flotPlot The chart
  * @returns void
  */
 function unlockCrosshairs(flotPlot) {
     $.each(PyScadaPlots,function(plot_id){
         if (typeof PyScadaPlots[plot_id].getFlotObject() !== 'undefined' && typeof(PyScadaPlots[plot_id].getFlotObject().getOptions) !== 'undefined' && typeof(PyScadaPlots[plot_id].getFlotObject().unlockCrosshair) !== 'undefined') {
             PyScadaPlots[plot_id].getFlotObject().unlockCrosshair();
         }
     });
 }
 // Lock Crosshairs
 /**
  * Lock each crosshairs on each chart
  */
 function lockCrosshairs() {
     $.each(PyScadaPlots,function(plot_id){
         if (typeof PyScadaPlots[plot_id].getFlotObject() !== 'undefined') {
             PyScadaPlots[plot_id].getFlotObject().lockCrosshair();
         }
     });
 }


 // COLOR GRADIENT :
 /**
  *  Color gradient
  * @param {number} fadeFraction
  * @param {Color} rgbColor1
  * @param {Color} rgbColor2
  * @param {Color} rgbColor3
  * @returns {string} return a color gradient
  */
 function colorGradient(fadeFraction, rgbColor1, rgbColor2, rgbColor3) {
     var color1 = rgbColor1;
     var color2 = rgbColor2;
     var fade = fadeFraction;

     // Do we have 3 colors for the gradient? Need to adjust the params.
     if (rgbColor3) {
       fade = fade * 2;

       // Find which interval to use and adjust the fade percentage
       if (fade >= 1) {
         fade -= 1;
         color1 = rgbColor2;
         color2 = rgbColor3;
       }
     }

     var diffRed = color2.red - color1.red;
     var diffGreen = color2.green - color1.green;
     var diffBlue = color2.blue - color1.blue;

     var gradient = {
       red: parseInt(Math.floor(parseInt(color1.red) + (diffRed * fade)), 10),
       green: parseInt(Math.floor(parseInt(color1.green) + (diffGreen * fade)), 10),
       blue: parseInt(Math.floor(parseInt(color1.blue) + (diffBlue * fade)), 10),
     };

     return 'rgb(' + gradient.red + ',' + gradient.green + ',' + gradient.blue + ')';
 }

 /**
  *  Fill aggregated type and period for each variable and for all selectors
  */
function setAggregatedLists() {
    c=document.querySelectorAll('.aggregation-type-option');
    for (cc in c) {
      if (typeof(c[cc]) == 'object') {
        var_id = c[cc].getAttribute('data-id');
        widget_id = c[cc].getAttribute('data-widget-id');
        a=get_period_fields(var_id);
        b=filter_aggregation_type_for_period_list(a);
        for (v in b) {
          c[cc].add(new Option(b[v], v));
          if (!document.querySelectorAll('#aggregation-type-all-select-' + widget_id + ' option[value="' + v + '"]').length) {
            document.querySelector('#aggregation-type-all-select-' + widget_id).add(new Option(b[v], v));
          }
        }
        c[cc].onchange = function(){
            updatePyScadaPlots(true);
            setAggregatedPeriodList(widget_id, var_id);
            widget_id = this.dataset['widgetId'];
            var_id = this.dataset['id'];
            if (this.value == "null") {
                document.querySelector('#chart-legend-options-span-' + widget_id + '-' + var_id).innerHTML = "";
            }else {
                document.querySelector('#chart-legend-options-span-' + widget_id + '-' + var_id).innerHTML = "(" + this.selectedOptions[0].text + ")";
            }
        };
        document.querySelector('#aggregation-type-all-select-' + widget_id).onchange = function(){
            widget_id = this.dataset['widgetId'];
            c = document.querySelectorAll('.aggregation-type-option[data-widget-id="' + widget_id + '"]')
            for (cc in c) {
                for (o in c[cc].options) {
                    if (this.value == c[cc][o].value){
                        c[cc].value = this.value;
                        var_id = c[cc].dataset['id'];
                        if (this.value == "null") {
                            document.querySelector('#chart-legend-options-span-' + widget_id + '-' + var_id).innerHTML = "";
                        }else {
                            document.querySelector('#chart-legend-options-span-' + widget_id + '-' + var_id).innerHTML = "(" + this.selectedOptions[0].text + ")";
                        }
                    };
                }
            }
            if (this.value == "null") {
                document.querySelector('#chart-legend-options-span-' + widget_id).innerHTML = "";
            }else {
                document.querySelector('#chart-legend-options-span-' + widget_id).innerHTML = "(" + this.selectedOptions[0].text + ")";
            }
            updatePyScadaPlots(true);
        };
      }
    }
}

function setAggregatedPeriodList(widget_id, var_id) {
    a=get_period_fields(var_id);
    b=filter_period_fields_by_type(a, );
    document.querySelector("li-aggregation-all-period-select-" + widget_id + "-" + var_id);
}


 //---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 //---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

 //                                                     CLIENT-SERVER

 //---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 //---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


 //                             -----------------------------------------------------------
 //                                                    Page's Settings
 //                             -----------------------------------------------------------


 // PAGES
 /**
  * Show page
  * @returns void
  */
 function show_page() {
     // hide all pages
     $(".sub-page").hide();
     // show page
     if (window.location.hash.length > 0) {
         $(window.location.hash).show();
     }else{
         window.location.hash = $('ul.navbar-nav li a').first().attr("href");
     }
 }


 // PROGRESS BAR :
 /**
  * Set the window progress bar
  * @returns void
  */
 function progressbarSetWindow( event, ui ) {
     updatePyScadaPlots(true);

     progressbar_resize_active = false;
 }


 // TIMELINE :

 // Timeline Resize
 /**
  * Resize the timeline if window size changed
  * @returns void
  */
 function timeline_resize( event, ui ) {
     var window_width = ui.size.width/($('#timeline-border').width()-10);
     var window_left = ui.position.left/($('#timeline-border').width()-10);
     var min_full = (DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP);

     if (window_left < 0.02){
         if ((window_width+window_left) < 0.98){
             DATA_DISPLAY_TO_TIMESTAMP = DATA_FROM_TIMESTAMP + min_full * (window_width+window_left);
             DATA_DISPLAY_WINDOW = DATA_DISPLAY_TO_TIMESTAMP - DATA_FROM_TIMESTAMP
         }else{
             DATA_DISPLAY_TO_TIMESTAMP = -1;
             DATA_DISPLAY_WINDOW = DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP
         }

         DATA_DISPLAY_FROM_TIMESTAMP = -1;
     }else{
         DATA_DISPLAY_FROM_TIMESTAMP = DATA_FROM_TIMESTAMP + min_full * window_left;
         if ((window_width+window_left) < 0.98){
             DATA_DISPLAY_TO_TIMESTAMP = DATA_FROM_TIMESTAMP + min_full * (window_width+window_left);
             DATA_DISPLAY_WINDOW = DATA_DISPLAY_TO_TIMESTAMP - DATA_DISPLAY_FROM_TIMESTAMP
         }else{
             DATA_DISPLAY_TO_TIMESTAMP = -1;
             DATA_DISPLAY_WINDOW = DATA_TO_TIMESTAMP - DATA_DISPLAY_FROM_TIMESTAMP
         }
     }
     update_timeline();
 }
 // Timeline Drag
 /**
  * ?
  * @returns void
  */
 function timeline_drag( event, ui ) {
     var window_left = ui.position.left/($('#timeline-border').width()-10);
     var min_full = (DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP);

     if (window_left < 0.02){
         DATA_DISPLAY_FROM_TIMESTAMP = -1
         DATA_DISPLAY_TO_TIMESTAMP = DATA_FROM_TIMESTAMP + DATA_DISPLAY_WINDOW
     }else{
         DATA_DISPLAY_FROM_TIMESTAMP = DATA_FROM_TIMESTAMP + min_full * window_left;
         DATA_DISPLAY_TO_TIMESTAMP = DATA_DISPLAY_FROM_TIMESTAMP + DATA_DISPLAY_WINDOW;
         if (DATA_DISPLAY_TO_TIMESTAMP >= DATA_TO_TIMESTAMP){
             DATA_DISPLAY_TO_TIMESTAMP = -1;
             DATA_DISPLAY_WINDOW = DATA_TO_TIMESTAMP - DATA_DISPLAY_FROM_TIMESTAMP;
         }
     }
     update_timeline();
 }

 // toggle daterangepicker :
 /**
  * Shows or hides date range picker
  * @returns void
  */
 function toggle_daterangepicker(){
     // Show/hide daterangepicker
     if (window.location.hash.substr(1) !== '') {
         if ($("#" + window.location.hash.substr(1) + ".show_daterangepicker").length) {
             $(".daterangepicker_parent").removeClass("hidden");
         }else {
             $(".daterangepicker_parent").addClass("hidden");
         }
     }
 }

 // Shows or hides timeline :
 /**
  * Toggle timeline
  * @returns void
  */
 function toggle_timeline(){
     // Show/hide timeline
     if (window.location.hash.substr(1) !== '') {
         if ($("#" + window.location.hash.substr(1) + ".show_timeline").length) {
             $(".timeline").removeClass("hidden");
         }else {
             $(".timeline").addClass("hidden");
         }
     }
 }

 //                             -----------------------------------------------------------
 //                                                   Page's Functions
 //                             -----------------------------------------------------------

 // FORM :
 /**
  * Check form value
  * @param {number} id_form Form to check
  * @returns {boolean} Return an error status
  */
 function check_form(id_form) {

     err = false;
     tabinputs = $.merge($('#'+id_form+ ' :text:visible'),$('#'+id_form+ ' :input:not(:text):hidden'));

     for (i=0;i<tabinputs.length;i++){ //test if there is an empty or non numeric value

         value = $(tabinputs[i]).val();
         id = $(tabinputs[i]).attr('id');

         var_name = $(tabinputs[i]).attr("name");
         val=$('.variable-config[data-id='+id.replace('-value', '')+']');
         key = parseInt($(val).data('key'));

         item_type = $(val).data('type');
         value_class = $(val).data('value-class');

         min = $(val).data('min');
         max = $(val).data('max');
         min_type = $(val).data('min-type');
         max_type = $(val).data('max-type');


         if (min_type == 'lte') {min_type_char = ">=";} else {min_type_char = ">";}
         if (max_type == 'gte') {max_type_char = "<=";} else {max_type_char = "<";}

         if (value == "" || value == null){
             $(tabinputs[i]).parents(".input-group").addClass("has-error");
             $(tabinputs[i]).parents(".input-group").find('.help-block').remove();
             $(tabinputs[i]).parents(".input-group").append('<span id="helpBlock-' + id + '" class="help-block">Please provide a value !</span>');
             err = true;
         }else {
             $(tabinputs[i]).parents(".input-group").find('.help-block').remove();
             check_mm = check_min_max(parseFloat(value), parseFloat(min), parseFloat(max), min_type, max_type);
             if (check_mm == -1) {
                 $(tabinputs[i]).parents(".input-group").addClass("has-error");
                 $(tabinputs[i]).parents(".input-group").append('<span id="helpBlock-' + id + '" class="help-block">Enter a value ' + min_type_char + ' ' + min + '</span>');
                 err = true;
             }else if (check_mm == 1) {
                 $(tabinputs[i]).parents(".input-group").addClass("has-error");
                 $(tabinputs[i]).parents(".input-group").append('<span id="helpBlock-' + id + '" class="help-block">Enter a value ' + max_type_char + ' ' + max + '</span>');
                 err = true;
             }else if (check_mm == 0) {
                 $(tabinputs[i]).parents(".input-group").removeClass("has-error");
                 if (isNaN(value)) {
                     if (item_type == "variable_property" && value_class == 'STRING') {
                     }else {
                         $(tabinputs[i]).parents(".input-group").addClass("has-error");
                         $(tabinputs[i]).parents(".input-group").append('<span id="helpBlock-' + id + '" class="help-block">The value must be a number ! Use dot not coma.</span>');
                         err = true;
                     }
                 }
             }
         }
     }

     tabselects = $('#'+id_form+ ' .select');

     for (i=0;i<tabselects.length;i++){ //test if there is an empty value
         value = $(tabselects[i]).val();
         id = $(tabselects[i]).attr('id');
         var_name = $(tabselects[i]).data("name");
         val=$('.variable-config[data-id='+id.replace('-value', '')+']');
         key = parseInt($(val).data('key'));
         item_type = $(val).data('type');
         value_class = $(val).data('value-class');
         min = $(val).data('min');
         max = $(val).data('max');
         min_type = $(val).data('min-type');
         max_type = $(val).data('max-type');
         if (min_type == 'lte') {min_type_char = ">=";} else {min_type_char = ">";}
         if (max_type == 'gte') {max_type_char = "<=";} else {max_type_char = "<";}

         if (value == "" || value == null){
             $(tabselects[i]).parents(".input-group").addClass("has-error");
             $(tabselects[i]).parents(".input-group").find('.help-block').remove();
             $(tabselects[i]).parents(".input-group").append('<span id="helpBlock-' + id + '" class="help-block">Please provide a value !</span>');
             err = true;
         }else {
             $(tabselects[i]).parents(".input-group").find('.help-block').remove();
             check_mm = check_min_max(parseFloat(value), parseFloat(min), parseFloat(max), min_type, max_type);
             if (check_mm == -1) {
                 $(tabselects[i]).parents(".input-group").addClass("has-error");
                 $(tabselects[i]).parents(".input-group").append('<span id="helpBlock-' + id + '" class="help-block">Enter a value ' + min_type_char + ' ' + min + '</span>');
                 err = true;
             }else if (check_mm == 1) {
                 $(tabselects[i]).parents(".input-group").addClass("has-error");
                 $(tabselects[i]).parents(".input-group").append('<span id="helpBlock-' + id + '" class="help-block">Enter a value ' + max_type_char + ' ' + max + '</span>');
                 err = true;
             }else if (check_mm == 0) {
                 $(tabselects[i]).parents(".input-group").removeClass("has-error");
                 if (isNaN(value)) {
                     if (item_type == "variable_property" && value_class == 'STRING') {
                     }else {
                         $(tabselects[i]).parents(".input-group").addClass("has-error");
                         $(tabselects[i]).parents(".input-group").append('<span id="helpBlock-' + id + '" class="help-block">The value must be a number ! Use dot not coma.</span>');
                         err = true;
                     }
                 }
             }
         }
     }
     return err;
 }


 // INITS :

 // Show Init
 /**
  * Show initialization status
  * @returns void
  */
 function show_init_status(){
     //$(".loadingAnimation").show();
     INIT_STATUS_COUNT = INIT_STATUS_COUNT + 1;
 }

 // Hide Init
 /**
  * Hide initialization status
  * @returns void
  */
 function hide_init_status(){
     INIT_STATUS_COUNT = INIT_STATUS_COUNT -1;
     if (INIT_STATUS_COUNT <= 0){
         //$(".loadingAnimation").hide();
     }
 }


 //LOADINGS :

 // Set and Show Loading
 /**
  * Set and show loading state
  * @param {number} key Element id where to show the loading state
  * @param {number} value Value to display
  * @returns void
  */
 function set_loading_state(key, value) {
     loading_states[key] = value;
     $('#page-load-label').show();
     $('#page-load-state').show();
     $('#page-load-label').text(loading_labels[key]);
     if ($('#page-load-state').length > 0) {
         $('#page-load-state')[0].setAttribute('value', (Number.parseFloat(loading_states[key]).toFixed(2)));
     }
 }

 // Hide Loading
 /**
  * Hide loading state
  * @returns void
  */
 function hide_loading_state() {
     $('#page-load-label').hide();
     $('#page-load-state').hide();
 }

 // UPDATES :

 // Show Status
 /**
  * Show 'AutoUpdateStatus'
  * @returns void
  */
 function show_update_status(){
     $(".AutoUpdateStatus").css("color", "");
     $(".AutoUpdateStatus").show();
     UPDATE_STATUS_COUNT++;
 }

 // Hide Status
 /**
  * Hide 'AutoUpdateStatus'
  * @returns void
  */
 function hide_update_status(){
     UPDATE_STATUS_COUNT--;
     if (UPDATE_STATUS_COUNT <= 0){
         $(".AutoUpdateStatus").hide();
         UPDATE_STATUS_COUNT = 0;
     }
 }

 // Auto Update
 /**
  * 'AutoUpdateButton' event
  * @param {boolean} toggleState
  */
 function auto_update_click(toggleState=true){
     if( toggleState) {
         $('.AutoUpdateButton').bootstrapSwitch('toggleState');
     }
     AUTO_UPDATE_ACTIVE = $('.AutoUpdateButton').bootstrapSwitch('state');
     if (AUTO_UPDATE_ACTIVE) {
         // deactivate auto update
     } else {
         // activate auto update
         JSON_ERROR_COUNT = 0;
         //data_handler();
     }
 }


 // NOTIFICATIONS :

 // Add Notification
 /**
  * Display an error/information message
  * @param {string} message Message to display
  * @param {number} level Level of notification
  * @param {number} timeout Notification timeout
  * @param {boolean} clearable Is clearable ?
  * @returns void
  */
 function add_notification(message, level,timeout,clearable) {
     timeout = typeof timeout !== 'undefined' ? timeout : 7000;
     clearable = typeof clearable !== 'undefined' ? clearable : true;

     var right = 4;
     var top = 55;
     if ($('#notification_area').children().hasClass('notification')) {
         top = Number($('#notification_area .notification').last().css('top').replace(/[^\d\.]/g, '')) + 56;
         right = Number($('#notification_area .notification').last().css('right').replace(/[^\d\.]/g, ''));
     }
     if (top > 400) {
         right = right + 50;
         top = 55;
     }
     if (right > 150) {
         $('#notification_area').empty();
         right = 4;
         top = 55;
     }

     //<0 - Debug
     //1 - Emergency
     //2 - Critical
     //3 - Errors
     //4 - Alerts
     //5 - Warnings
     //6 - Notification (webnotice)
     //7 - Information (webinfo)
     //8 - Notification (notice)
     //9 - Information (info)
     if (level === 1) {
         level = 'danger';
         message_pre = 'Emergency! ';
     } else if (level === 2) {
         level = 'danger';
         message_pre = 'Critical! ';
     } else if (level === 3) {
         level = 'danger';
         message_pre = 'Error! ';
     } else if (level === 4) {
         level = 'danger';
         message_pre = 'Alert! ';
     } else if (level === 5) {
         level = 'warning';
         message_pre = 'Warning! ';
     }else if (level === 6) {
         level = 'success';
         message_pre = 'Notice ';
     }else if (level === 7) {
         level = 'info';
         message_pre = 'Info ';
     }else if (level === 8) {
         level = 'success';
         message_pre = 'Notice ';
     }else if (level === 9) {
         level = 'info';
         message_pre = 'Info ';
     }
     if(clearable){
         $('#notification_area').append('<div id="notification_Nb' + NOTIFICATION_COUNT + '" class="notification alert alert-' + level + ' alert-dismissable" style="position: fixed; top: ' + top + 'px; right: ' + right + 'px; z-index: 2000"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button><strong>' + message_pre + '</strong>' + new Date().toLocaleTimeString() + ': ' + message + '</div>');
     }else{
         $('#notification_area_2').append('<div id="notification_Nb' + NOTIFICATION_COUNT + '" class="notification alert alert-' + level + '" ><strong>'+ message_pre + '</strong>' + new Date().toLocaleTimeString() + ': ' + message + '</div>');
     }
     if (timeout){
         setTimeout('$("#notification_Nb' + NOTIFICATION_COUNT + '").alert("close");', timeout);
     }
     NOTIFICATION_COUNT = NOTIFICATION_COUNT + 1;
     console.log(message_pre + new Date().toLocaleTimeString() + ': ' + message);
 }

 // Raise Data
 /**
  * Display a 'date out of date' error notification
  * @returns void
  */
 function raise_data_out_of_date_error(){
     if (!DATA_OUT_OF_DATE){
         DATA_OUT_OF_DATE = true;
         DATA_OUT_OF_DATE_ALERT_ID = add_notification('displayed data is out of date!',4,false,false);
     }
 }

 // CLear Date
 /**
  * Close the 'data out of date' error notification
  * @returns void
  */
 function clear_data_out_of_date_error(){
     if (DATA_OUT_OF_DATE){
         DATA_OUT_OF_DATE = false;
         $('#'+DATA_OUT_OF_DATE_ALERT_ID).alert("close");
     }
 }


 // UPDATE LOG :
 /**
  * Update logs
  * @returns {boolean}
  */
 function update_log() {
     if (LOG_FETCH_PENDING_COUNT){return false;}
     LOG_FETCH_PENDING_COUNT = true;
     if(LOG_LAST_TIMESTAMP === 0){
         if(SERVER_TIME > 0){
                 LOG_LAST_TIMESTAMP = SERVER_TIME;
         }else{
             LOG_FETCH_PENDING_COUNT = false;
             return false;
         }
     }

     show_update_status();

     $.ajax({
         url: ROOT_URL+'json/log_data/',
         type: 'post',
         dataType: "json",
         timeout: 29000,
         data: {timestamp: LOG_LAST_TIMESTAMP},
         methode: 'post',
         success: function(data) {
             $.each(data,function(key,val){
                     if("timestamp" in data[key]){
                         if (LOG_LAST_TIMESTAMP<data[key].timestamp){
                             LOG_LAST_TIMESTAMP = data[key].timestamp;
                         }
                         add_notification(data[key].message,+data[key].level);
                     }
                 });
             hide_update_status();
             LOG_FETCH_PENDING_COUNT = false;
         },
         error: function(x, t, m) {
             hide_update_status();
             LOG_FETCH_PENDING_COUNT = false;
         }
     });
 }


 // REFRESH LOGO :
 /**
  * Refresh logo
  * @param {number} key Element id where to refresh the logo
  * @param {object} type
  * @returns void
  */
 function refresh_logo(key, type){
     if (type == "variable") {type_short="var";} else {type_short = "prop";}
     $.each($(".control-item.type-numeric." + type_short + "-" + key + " img"), function(k,v){
         $(v).remove();
     });
     key = key.toString();
     //if ($(".variable-config[data-refresh-requested-timestamp][data-key=" + key + "][data-type=" + type + "]").attr('data-refresh-requested-timestamp')>$(".variable-config[data-value-timestamp][data-key=" + key + "][data-type=" + type + "]").attr('data-value-timestamp')) {
     if (get_config_from_hidden_config(type, 'id', key, 'refresh-requested-timestamp')>get_config_from_hidden_config(type, 'id', key, 'value-timestamp')) {
         $.each($(".control-item.type-numeric." + type_short + "-" + key), function(k,v){
             val_temp=$(v).html();
             $(v).prepend('<img style="height:14px;" src="/static/pyscada/img/load.gif" alt="refreshing">');
             //$(v).html('<img style="height:14px;" src="/static/pyscada/img/load.gif" alt="refreshing">' + val_temp);
         });
     }else {
         $.each($(".control-item.type-numeric." + type_short + "-" + key + " img"), function(k,v){
             $(v).remove();
         });
     }
 }


 // CHECK MIN MAX :
 /**
  * Check if 'value' is between min max
  * @param {number} value Value to check
  * @param {number} min
  * @param {number} max
  * @param {number} min_strict
  * @param {number} max_strict
  * @returns {boolean}
  */
 function check_min_max(value, min, max, min_strict, max_strict) {

     min_strict = typeof min_strict !== 'undefined' ? min_strict : "lte";
     max_strict = typeof max_strict !== 'undefined' ? max_strict : "gte";
     min = typeof min !== 'undefined' ? min : false;
     max = typeof max !== 'undefined' ? max : false;

     if (min_strict == "lt" && parseFloat(value) <= parseFloat(min) && min !== false) {
         return -1;
     }
     if (min_strict == "lte" && parseFloat(value) < parseFloat(min) && min !== false) {
         return -1;
     }
     if (max_strict == "gt" && parseFloat(value) >= parseFloat(max) && max !== false) {
         return 1;
     }
     if (max_strict == "gte" && parseFloat(value) > parseFloat(max) && max !== false) {
         return 1;
     }
     return 0;
 }


 //                             -----------------------------------------------------------
 //                                                     Client-Server
 //                             -----------------------------------------------------------

 // from http://debuggable.com/posts/run-intense-js-without-freezing-the-browser:480f4dd6-f864-4f72-ae16-41cccbdd56cb
 // on 11.04.2014
 $.browserQueue = {
     _timer: null,
     _queue: [],
     add: function(fn, context, time) {
         var setTimer = function(time) {
             $.browserQueue._timer = setTimeout(function() {
                 time = $.browserQueue.add();
                 if ($.browserQueue._queue.length) {
                     setTimer(time);
                 }
             }, time || 2);
         }

         if (fn) {
             $.browserQueue._queue.push([fn, context, time]);
             if ($.browserQueue._queue.length == 1) {
                 setTimer(time);
             }
             return;
         }

         var next = $.browserQueue._queue.shift();
         if (!next) {
             return 0;
         }
         next[0].call(next[1] || window);
         return next[2];
     },
     clear: function() {
         clearTimeout($.browserQueue._timer);
         $.browserQueue._queue = [];
     }
 };

 $.ajaxSetup({
     crossDomain: false, // obviates need for sameOrigin test
     beforeSend: function(xhr, settings) {
         if (!csrfSafeMethod(settings.type)) {
             xhr.setRequestHeader("X-CSRFToken", CSRFTOKEN);
         }
     }
 });


 //                             -----------------------------------------------------------
 //                                             Client-Server's Functions
 //                             -----------------------------------------------------------

 // HTTP SAFE METHOD :
 /**
  * Return a HTTP methods
  * @param {object} method
  * @returns {object}
  */
 function csrfSafeMethod(method) {
     // these HTTP methods do not require CSRF protection
     return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
 }

 // DATE :

 // Set Date Range
 /**
  * Set date range
  * @param {number} start Date range start
  * @param {number} end Date range stop
  * @returns void
  */
 function daterange_set(start, end) {
     //$('#daterange').data('daterangepicker').setStartDate(start);
     //$('#daterange').data('daterangepicker').setEndDate(end);
     daterange_cb(start, end);
 }

 // Date Range Cb
 /**
  * Set 'daterange span' and adapt content padding top on navbar size
  * @param {number} start Date range start
  * @param {number} end Date range stop
  */
 function daterange_cb(start, end) {
     //
     //
     $('#daterange span').html(start.format(daterange_format) + ' - ' + end.format(daterange_format));
 }


 //                             -----------------------------------------------------------
 //                                                    Click Events
 //                             -----------------------------------------------------------

 // FORM :

 //form/read-task
 $('button.read-task-set').click(function(){
     t = SERVER_TIME;
     key = $(this).data('key');
     type = $(this).data('type');
     type = type.replace("_", "");
     console.log(key, type);
     //$(".variable-config[data-key=" + key + "][data-type=" + type + "]").attr('data-refresh-requested-timestamp',t)
     set_config_from_hidden_config("variable","id",key,"refresh-requested-timestamp",t)
     set_config_from_hidden_config("variableproperty","id",key,"refresh-requested-timestamp",t)
     refresh_logo(key, type);
     data_type = $(this).data('type');
     $(this)[0].disabled = true;
     $.ajax({
         type: 'post',
         url: ROOT_URL+'form/read_task/',
         data: {key:key, type:data_type},
         success: function (data) {

         },
         error: function(data) {
             add_notification('read task failed',3);
         }
     });
     $(this)[0].disabled = false;
 });

 //form/write_task/
 $('button.write-task-set').click(function(){
     key = $(this).data('key');
     id = $(this).attr('id');
     value = $("#"+id+"-value").val();
     item_type = $(this).data('type');
     min = $(this).data('min');
     max = $(this).data('max');
     value_class = $(this).data('value-class');
     min_type = $(this).data('min-type');
     max_type = $(this).data('max-type');
     if (min_type == 'lte') {min_type_char = ">=";} else {min_type_char = ">";}
     if (max_type == 'gte') {max_type_char = "<=";} else {max_type_char = "<";}
     if (value == "" || value == null) {
         $(this).parents(".input-group").addClass("has-error");
         $(this).parents(".input-group").find('.help-block').remove()
         $(this).parents(".input-group-btn").after('<span id="helpBlock-' + id + '" class="help-block">Please provide a value !</span>');
     }else {
         $(this).parents(".input-group").find('.help-block').remove();
         check_mm = check_min_max(parseFloat(value), parseFloat(min), parseFloat(max), min_type, max_type);
         if (check_mm == -1) {
             $(this).parents(".input-group").addClass("has-error");
             $(this).parents(".input-group-btn").after('<span id="helpBlock-' + id + '" class="help-block">Enter a value ' + min_type_char + ' ' + min + '</span>');
         }else if (check_mm == 1) {
             $(this).parents(".input-group").addClass("has-error");
             $(this).parents(".input-group-btn").after('<span id="helpBlock-' + id + '" class="help-block">Enter a value ' + max_type_char + ' ' + max + '</span>');
         }else if (check_mm == 0) {
             $(this).parents(".input-group").removeClass("has-error")
             if (isNaN(value)) {
                 if (item_type == "variable_property" && value_class == 'STRING'){
                     $.ajax({
                         type: 'post',
                         url: ROOT_URL+'form/write_property2/',
                         data: {variable_property:key, value:value},
                         success: function (data) {

                         },
                         error: function(data) {
                             add_notification('Operation not permitted (prop ' + key + ")",3);
                         }
                     });
                 }else {
                     $(this).parents(".input-group").addClass("has-error");
                     $(this).parents(".input-group-btn").after('<span id="helpBlock-' + id + '" class="help-block">The value must be a number ! Use dot not coma.</span>');
                 };
             }else {
                 $.ajax({
                     type: 'post',
                     url: ROOT_URL+'form/write_task/',
                     data: {key:key, value:value, item_type:item_type},
                     success: function (data) {

                     },
                     error: function(data) {
                         add_notification('Operation not permitted (var ' + key + ")",3);
                     }
                 });
             };
         };
     };
 });
 // set
 $('button.write-task-form-set').click(function(){
     id_form = $(this.form).attr('id');
     if (check_form(id_form)) {return;}

     tabinputs = $.merge(tabinputs,$('#'+id_form+ ' :input:button.type-bool'));
     for (i=0;i<tabinputs.length;i++){
         value = $(tabinputs[i]).val();
         id = $(tabinputs[i]).attr('id');
         val=$('.variable-config[data-id='+id.replace('-value', '')+']')
         var_name = $(val).data("name");
         key = parseInt($(val).data('key'));
         item_type = $(val).data('type');

         if ($(tabinputs[i]).hasClass('btn-success')){
             id = $(tabinputs[i]).attr('id');
             //$('#'+id).removeClass('update-able');
             $.ajax({
                 type: 'post',
                 url: ROOT_URL+'form/write_task/',
                 data: {key:key,value:1,item_type:item_type},
                 success: function (data) {
                 },
                 error: function(data) {
                     add_notification('Operation not permitted (bool ' + key + ")",3);
                 }
             });
         }else if ($(tabinputs[i]).hasClass('btn-default')){
             id = $(tabinputs[i]).attr('id');
             //$('#'+id).removeClass('update-able');
             $.ajax({
                 type: 'post',
                 url: ROOT_URL+'form/write_task/',
                 data: {key:key,value:0,item_type:item_type},
                 success: function (data) {
                 },
                 error: function(data) {
                     add_notification('Operation not permitted (bool ' + key + ")",3);
                 }
             });
         }else{
             $.ajax({
                 type: 'post',
                 url: ROOT_URL+'form/write_task/',
                 data: {key:key, value:value, item_type:item_type},
                 success: function (data) {

                 },
                 error: function(data) {
                     add_notification('Operation not permitted (var ' + key + ")",3);
                     alert("Form Set NOK inputs "+data+" - key "+key+" - value "+value+" - item_type "+item_type + " - name "+var_name)
                 }
             });
         };
     };
     for (i=0;i<tabselects.length;i++){ //test if there is an empty value
         value = $(tabselects[i]).val();
         var_name = $(tabselects[i]).data("name");
         key = $(tabselects[i]).data('key');
         item_type = $(tabselects[i]).data('type');
         if (isNaN(value)){
             if (item_type == "variable_property"){
                 $.ajax({
                     type: 'post',
                     url: ROOT_URL+'form/write_property2/',
                     data: {variable_property:var_name, value:value},
                     success: function (data) {

                     },
                     error: function(data) {
                         add_notification('Operation not permitted (dropdown ' + key + ")",3);
                     }
                 });
             }else {
                 add_notification("select is " + item_type + " and not a number",3);
             };
         }else {
             $.ajax({
                 type: 'post',
                 url: ROOT_URL+'form/write_task/',
                 data: {key:key, value:value, item_type:item_type},
                 success: function (data) {

                 },
                 error: function(data) {
                     add_notification('Operation not permitted (dropdown ' + key + ")",3);
                     alert("Form Set NOK selects "+data+" - key "+key+" - value "+value+" - item_type "+item_type + " - name "+var_name)
                 }
             });
         };
     };
 });
 // button
 $('input.write-task-btn').click(function(){
     key = $(this).data('key');
     id = $(this).attr('id');
     item_type = $(this).data('type');
     $('#'+id).removeClass('update-able');
     $(".variable-config[data-refresh-requested-timestamp][data-key=" + key + "][data-type=" + item_type + "]").attr('data-refresh-requested-timestamp', SERVER_TIME)
     $(".variable-config2[data-refresh-requested-timestamp][data-id=" + key + "]").attr('data-refresh-requested-timestamp', SERVER_TIME)
     if($(this).hasClass('btn-default')){
         $('#'+id).removeClass('btn-default')
         $('#'+id).addClass('btn-success');
     }else if ($(this).hasClass('btn-success')){
         $('#'+id).addClass('btn-default')
         $('#'+id).removeClass('btn-success');
     }
 });

 $('button.write-task-btn').click(function(){
     key = $(this).data('key');
     id = $(this).attr('id');
     item_type = $(this).data('type');
     $('#'+id).removeClass('update-able');
     $(".variable-config[data-refresh-requested-timestamp][data-key=" + key + "][data-type=" + item_type + "]").attr('data-refresh-requested-timestamp', SERVER_TIME)
     $(".variable-config2[data-refresh-requested-timestamp][data-id=" + key + "]").attr('data-refresh-requested-timestamp', SERVER_TIME)
     if($(this).hasClass('btn-default')){
         $.ajax({
             type: 'post',
             url: ROOT_URL+'form/write_task/',
             data: {key:key,value:1,item_type:item_type},
             success: function (data) {
                 $('#'+id).removeClass('btn-default')
                 $('#'+id).addClass('btn-success');
             },
             error: function(data) {
                 add_notification('Operation not permitted (bool ' + key + ")",3);
             }
         });
     }else if ($(this).hasClass('btn-success')){
         $.ajax({
             type: 'post',
             url: ROOT_URL+'form/write_task/',
             data: {key:key,value:0,item_type:item_type},
             success: function (data) {
                 $('#'+id).addClass('btn-default')
                 $('#'+id).removeClass('btn-success');
             },
             error: function(data) {
                 add_notification('Operation not permitted (bool ' + key + ")",3);
             }
         });
     }
 });


 // fix drop down problem
 $( document ).ready(function() {
     // show buttons
     $(".loadingAnimation").parent().show();
     $(".AutoUpdateStatus").parent().parent().show();
     $(".ReadAllTask").parent().parent().show();
     $(".AutoUpdateButtonParent").show();

     // init loading states
     set_loading_state(1, 40);

     // padding top content

     // Show current page or first
     show_page();

     // move overlapping side menus
     // left
     var menu_pos = $('footer')[0].clientHeight + 6;
     $.each($('.side-menu.left'),function(key,val){
         $(val).attr("style","bottom: " + menu_pos + "px;");
         menu_pos = menu_pos + val.clientHeight + 10;
     });
     // right
     menu_pos = $('footer')[0].clientHeight + 6;
     $.each($('.side-menu.right'),function(key,val){
         $(val).attr("style","bottom: " + menu_pos + "px;");
         menu_pos = menu_pos + val.clientHeight + 10;
     });

     // sidemenus
     //left
     $('.side-menu.left').mouseenter(function(){
         $(this).stop().animate({"left":0},500);
     }).mouseleave(function(){
         ow = $(this).outerWidth();
         $(this).stop().animate({"left":-(ow - 11)},500);
     });
     // right
     $('.side-menu.right').mouseenter(function(){
         $(this).stop().animate({"right":0},500);
     }).mouseleave(function(){
         ow = $(this).outerWidth();
         $(this).stop().animate({"right":-(ow - 11)},500);
     });
     // bottom
     $('.side-menu.bottom').css('margin-left',- $('.side-menu.bottom').outerWidth(true)/2);
     $('.side-menu.bottom').stop().animate({"bottom":-($('.side-menu.bottom').outerHeight(true) - 31)},500);
     $('.side-menu.bottom').mouseenter(function(){
         $(this).stop().animate({"bottom":0},500);
     }).mouseleave(function(){
         outerHeight = $(this).outerHeight(true);
         $(this).stop().animate({"bottom":-(outerHeight - 31)},500);
     });

     set_loading_state(1, loading_states[1] + 10);


     // prevent reloading by existent
     window.onbeforeunload = function() {
         return "you realy wan't to reload/leave the page?";
     };
     $(window).on('hashchange', function() {
         // nav menu click event
         if (window.location.hash.length > 0) {
             $('ul.navbar-nav li.active').removeClass('active');
             $('a[href$="' + window.location.hash + '"]').parent('li').addClass('active');
             show_page();
         }
         toggle_daterangepicker();
         toggle_timeline();
         updatePyScadaPlots(false);
     });

     set_loading_state(1, loading_states[1] + 10);


     // Activate tooltips
     $('[data-toggle*="tooltip"]').tooltip();

     // Setup drop down menu
     $('.dropdown-toggle').dropdown();

     // Setup auto-update switch button
     $('.AutoUpdateButton').removeClass('hidden');
     $('.AutoUpdateButton').bootstrapSwitch({
         onInit: function(event) {
             $('.bootstrap-switch-id-AutoUpdateButton').tooltip({title:"Auto update data", placement:"bottom"});
         }
       });

     // Fix input element click problem
     $('.dropdown input, .dropdown label, .dropdown button').click(function(e) {
         e.stopPropagation();
     });
     set_loading_state(1, loading_states[1] + 10);

     // init
     $.each($('.bar-container'),function(key,val){
         // get identifier of the chart
         id = val.id.substring(16);
         min = $(val).data('min');
         max = $(val).data('max');
         if ( min === null ) {min = 0;}
         if ( max === null ) {max = 100;}

         // add a new Plot
         PyScadaPlots.push(new Bar(id, min, max));
     });
     $.each($('.chart-container'),function(key,val){
         // get identifier of the chart
         id = val.id.substring(16);
         if ($(val).data('xaxis').id == 'False') {xaxisVarId = null;} else {xaxisVarId = $(val).data('xaxis').id;}
         if ($(val).data('xaxis').linlog == 'True') {xaxisLinLog = true;} else {xaxisLinLog = false;}
         // add a new Plot
         PyScadaPlots.push(new PyScadaPlot(id, xaxisVarId, xaxisLinLog));
     });
     $.each($('.pie-container'),function(key,val){
         // get identifier of the chart
         id = val.id.substring(16);
         radius = $(val).data('radius').radius / 100;
         innerRadius = $(val).data('radius').innerRadius / 100;
         // add a new Plot
         PyScadaPlots.push(new Pie(id, radius, innerRadius));
     });
     $.each($('.gauge-container'),function(key,val){
         // get identifier of the chart
         id = val.id.substring(16);
         min = $(val).data('params').min;
         max = $(val).data('params').max;
         if ( min === null ) {min = 0;}
         if ( max === null ) {max = 100;}

         thresholdValues = JSON.parse($(val).data('params').threshold_values);

         max2 = max;
         for (v in thresholdValues) {if (v != "max") {max2 = Math.max(max2, v);}
     }
         threshold_values = [];
         for (var v in thresholdValues) {
             if (v == "max") {v = max2;thresholdValues[v]=thresholdValues['max'];}
             threshold_values.push({value:v, color:thresholdValues[v]})
         }
         if ( threshold_values === "" ) {threshold_values = [];}
         // add a new Plot
         PyScadaPlots.push(new Gauge(id, min, max, threshold_values));
     });

     $.each($('.variable-config'),function(key,val){
         key = parseInt($(val).data('key'));
         init_type = parseInt($(val).data('init-type'));
         item_type = $(val).data('type');
         if(item_type == '' || typeof(item_type) == 'undefined'){
             item_type = "variable";
         }

         if( VARIABLE_PROPERTY_KEYS.indexOf(key)==-1 && item_type === "variable_property"){
             VARIABLE_PROPERTY_KEYS.push(key);
         }else if (VARIABLE_KEYS.indexOf(key)==-1 && item_type === "variable"){
             VARIABLE_KEYS.push(key);
         }
         if (typeof(STATUS_VARIABLE_KEYS[key]) == 'undefined' && init_type==0 && item_type === "variable"){
             STATUS_VARIABLE_KEYS[key] = 0;
         }
         if (typeof(CHART_VARIABLE_KEYS[key]) == 'undefined' && init_type==1 && item_type === "variable"){
             CHART_VARIABLE_KEYS[key] = 0;
         }
         if (typeof(VARIABLE_PROPERTIES[key]) == 'undefined' && item_type === "variable_property"){
             VARIABLE_PROPERTIES[key] = 0;
         }
     });

     // Add calculated aggregated variable to CHART_VARIABLE_KEYS
     $.each($('.calculatedvariable-config2'),function(key,val){
         id = parseInt($(val).data('store-variable'));
         CHART_VARIABLE_KEYS[id] = 0;
     });

     set_loading_state(1, loading_states[1] + 10);


     // zoom selection mode
     $('.activate_zoom_x').change(function() {
         set_chart_selection_mode();
     });
     $('.activate_zoom_y').change(function() {
         set_chart_selection_mode();
     });

     setTimeout(function() {data_handler();}, 5000);
     set_chart_selection_mode();


     // timeline setup
     $( "#timeline" ).resizable({
         handles: "e, w",
         containment: "#timeline-border",
         stop: progressbarSetWindow,
         start: function( event, ui ) {progressbar_resize_active = true;},
         resize: timeline_resize,
         maxWidth: $('#timeline-border').width()-10
     });
     $('#timeline-border').bind('resize', function(){
         $( "#timeline" ).resizable("option", "maxWidth",$('#timeline-border').width()-10);
     });
     $('#timeline').draggable({
         axis: "x",
         containment: "#timeline-border",
         drag: timeline_drag,
         start: function( event, ui ) {progressbar_resize_active = true;},
         stop: progressbarSetWindow,
     });

     // Send request data to all devices
     $('.ReadAllTask').click(function(e) {
       $.ajax({
           url: ROOT_URL+'form/read_all_task/',
           type: "POST",
           data:{},
           success: function (data) {
             document.querySelectorAll('.hidden.variable-config2').forEach(function(e) {
                e.setAttribute('data-refresh-requested-timestamp',SERVER_TIME);
             });
             document.querySelectorAll('.hidden.variable-config2').forEach(function(e) {
                 var type = "variable";
                 var key = e.getAttribute('data-id');
                 refresh_logo(key, type);
             })

             document.querySelectorAll('.hidden.variableproperty-config2').forEach(function(e) {
                e.setAttribute('data-refresh-requested-timestamp',SERVER_TIME);
             });
             document.querySelectorAll('.hidden.variableproperty-config2').forEach(function(e) {
                 var type = "variableproperty";
                 var key = e.getAttribute('data-id');
                 refresh_logo(key, type);
             })
           },
           error: function(x, t, m) {
               add_notification('Request all data failed', 1);
           },
         });
     });

     // auto update function
     $(".AutoUpdateButton").on('switchChange.bootstrapSwitch', function(e, d) {
         auto_update_click(false);
     });
     $('#PlusTwoHoursButton').click(function(e) {
     if (INIT_CHART_VARIABLES_DONE){
         $('#PlusTwoHoursButton').addClass("disabled");
         DATA_INIT_STATUS++;
         DATA_BUFFER_SIZE = DATA_BUFFER_SIZE + 120*60*1000;
         DATA_FROM_TIMESTAMP = DATA_FROM_TIMESTAMP - 120*60*1000;
         INIT_CHART_VARIABLES_DONE = false;
     }
     });

     // show timeline and daterangepicker
     toggle_daterangepicker();
     toggle_timeline();

     set_loading_state(1, loading_states[1] + 10);


     // Resize charts on windows resize
     $(window).resize(function() {
       $.each(PyScadaPlots,function(plot_id){
             var self = this, doBind = function() {
                 PyScadaPlots[plot_id].resize();
             };
             $.browserQueue.add(doBind, this);
       });
     });
     set_loading_state(1, loading_states[1] + 10);

     // Prevent closing dropdown on click
     $('.dropdown-menu').click(function(e) {
         e.stopPropagation();
     });

     set_loading_state(1, 100);
     hide_loading_state();

     // Set and show refresh rate input
     document.querySelectorAll('.refresh-rate-input').forEach(item => {item.oninput = function () {
         document.querySelectorAll('.refresh-rate-output').forEach(item => {item.innerHTML = this.value});
         document.querySelectorAll('.refresh-rate-input').forEach(item => {item.value = this.value});
         REFRESH_RATE = this.value;
     }});
     document.querySelectorAll('.refresh-rate-output').forEach(item => {item.innerHTML= document.querySelector('.refresh-rate-input').value});
     document.querySelectorAll('.refresh-rate-li').forEach(item => {item.classList.remove('hidden')});
     document.querySelectorAll('.refresh-rate-divider').forEach(item => {item.classList.remove('hidden')});

     // Fill aggregated lists
     setAggregatedLists();
 });
