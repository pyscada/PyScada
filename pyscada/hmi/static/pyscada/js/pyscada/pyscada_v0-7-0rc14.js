/* Javascript library for the PyScada web client based on jquery and flot,

version 0.7.0rc14

Copyright (c) 2013-2019 Martin Schröder, Camille Lavayssière
Licensed under the GPL.

*/
var version = "0.7.0rc14"
var NOTIFICATION_COUNT = 0
var UPDATE_STATUS_COUNT = 0;
var INIT_STATUS_COUNT = 0;
var PyScadaPlots = [];
var DATA_OUT_OF_DATE = false;
var DATA_OUT_OF_DATE_ALERT_ID = '';
var JSON_ERROR_COUNT = 0;
var AUTO_UPDATE_ACTIVE = true;
var SINGLE_UPDATE = false;
var PREVIOUS_AUTO_UPDATE_ACTIVE_STATE = false;
var LOG_LAST_TIMESTAMP = 0;
var DATA_TO_TIMESTAMP = 0;
var DATA_FROM_TIMESTAMP = 0;
var DATA_DISPLAY_FROM_TIMESTAMP = -1;
var DATA_DISPLAY_TO_TIMESTAMP = -1;
var DATA_DISPLAY_WINDOW = 20*60*1000;
var DATA_BUFFER_SIZE = 300*60*1000; // size of the data buffer in ms
var progressbar_resize_active = false;
var SERVER_TIME = 0;
var LAST_QUERY_TIME = 0;
var CSRFTOKEN = $.cookie('csrftoken');
var FETCH_DATA_TIMEOUT = 5000;
var LOG_FETCH_PENDING_COUNT = false;
var REFRESH_RATE = 2500;
var CACHE_TIMEOUT = 15000; // in milliseconds
var ROOT_URL = window.location.protocol+"//"+window.location.host + "/";
var VARIABLE_KEYS = [];
var VARIABLE_PROPERTY_KEYS = [];
var STATUS_VARIABLE_KEYS = {count:function(){var c = 0;for (key in this){c++;} return c-2;},keys:function(){var k = [];for (key in this){if (key !=="keys" && key !=="count"){k.push(key);}} return k;}};
var CHART_VARIABLE_KEYS = {count:function(){var c = 0;for (key in this){c++;} return c-2;},keys:function(){var k = [];for (key in this){if (key !=="keys" && key !=="count"){k.push(key);}} return k;}};
var DATA = {}; // holds the fetched data from the server
var VARIABLE_PROPERTIES = {};
var VARIABLE_PROPERTIES_DATA = {}
var DATA_INIT_STATUS = 0; // status 0: nothing done, 1:
var UPDATE_X_AXES_TIME_LINE_STATUS = false;
var FETCH_DATA_PENDING = 0;
var INIT_STATUS_VARIABLES_DONE = false;
var INIT_CHART_VARIABLES_DONE = false;
var INIT_CHART_VARIABLES_COUNT = 0;
var X_AXIS = 0; // id of xaxis for XY charts
// the code
var debug = 0;
var DataFetchingProcessCount = 0;


function show_update_status(){
    $("#AutoUpdateStatus").css("color", "")
    $("#AutoUpdateStatus").show();
    UPDATE_STATUS_COUNT++;
}

function hide_update_status(){
    UPDATE_STATUS_COUNT--;
    if (UPDATE_STATUS_COUNT <= 0){
        $("#AutoUpdateStatus").hide();
        UPDATE_STATUS_COUNT = 0;
    }
}

function auto_update_click(){
    if (AUTO_UPDATE_ACTIVE) {
        // deactivate auto update
        AUTO_UPDATE_ACTIVE = false;
        $("#AutoUpdateButton").addClass("glyphicon-play");
        $("#AutoUpdateButton").removeClass("glyphicon-pause");
        $("#AutoUpdateButton").attr("data-original-title", "Auto update data OFF");
        $("#AutoUpdateButton").tooltip('hide')
    } else {
        // activate auto update
        AUTO_UPDATE_ACTIVE = true;
        $("#AutoUpdateButton ").addClass("glyphicon-pause");
        $("#AutoUpdateButton ").removeClass("glyphicon-play");
        $("#AutoUpdateButton").attr("data-original-title", "Auto update data ON");
        $("#AutoUpdateButton").tooltip('hide')
        JSON_ERROR_COUNT = 0;
        //data_handler();
    }
}

function show_init_status(){
    $("#loadingAnimation").show();
    INIT_STATUS_COUNT = INIT_STATUS_COUNT + 1;
}

function hide_init_status(){
    INIT_STATUS_COUNT = INIT_STATUS_COUNT -1;
    if (INIT_STATUS_COUNT <= 0){
        $("#loadingAnimation").hide();
    }
}

function raise_data_out_of_date_error(){
    if (!DATA_OUT_OF_DATE){
        DATA_OUT_OF_DATE = true;
        DATA_OUT_OF_DATE_ALERT_ID = add_notification('displayed data is out of date!',4,false,false);
    }
}

function clear_data_out_of_date_error(){
    if (DATA_OUT_OF_DATE){
        DATA_OUT_OF_DATE = false;
        $('#'+DATA_OUT_OF_DATE_ALERT_ID).alert("close");
    }
}

function check_buffer(key){
    if ((DATA[key][0][0] < DATA_FROM_TIMESTAMP)){
        stop_id = find_index_sub_lte(DATA[key],DATA_FROM_TIMESTAMP,0);
        DATA[key] = DATA[key].splice(stop_id);
    }
}

function add_fetched_data(key,value){
    if (typeof(value)==="object"){
        if (value.length >0){
            if (typeof(CHART_VARIABLE_KEYS[key]) === 'undefined'){
                // no history needed
                DATA[key] = [value.pop()];
                if (DATA[key][0] < DATA_FROM_TIMESTAMP){
                    //DATA_FROM_TIMESTAMP = value[0][0];
                    UPDATE_X_AXES_TIME_LINE_STATUS = true;
                }
            }else {
                if (typeof(DATA[key]) == "undefined"){
                    DATA[key] = value;
                } else {
                    var v_t_min = value[0][0];
                    var v_t_max = value[value.length-1][0];
                    var d_t_min = DATA[key][0][0];
                    var d_t_max = DATA[key][DATA[key].length-1][0];

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
                    } else if (v_t_max > d_t_min && v_t_min < d_t_min){
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
                        console.log(key + ' : no new data');
                    }
                }
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

function data_handler(){

    if(AUTO_UPDATE_ACTIVE || SINGLE_UPDATE){
        SINGLE_UPDATE = false
        if(DATA_TO_TIMESTAMP==0){
        // fetch the SERVER_TIME
            data_handler_ajax(0,[],[],Date.now());
        }else{
            if(FETCH_DATA_PENDING<=0 && INIT_STATUS_VARIABLES_DONE && INIT_CHART_VARIABLES_DONE){
            // fetch new data
                data_handler_ajax(0, VARIABLE_KEYS, VARIABLE_PROPERTY_KEYS, LAST_QUERY_TIME);
            }
            // fetch historic data
            if(FETCH_DATA_PENDING<=1){
                if(!INIT_STATUS_VARIABLES_DONE){
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
                        if(var_count >= 5){SINGLE_UPDATE = true;break;}
                    }
                    if(var_count>0){
                        data_handler_ajax(1,vars,props,timestamp);
                    }else{
                        INIT_STATUS_VARIABLES_DONE = true;
                    }
                }else if (!INIT_CHART_VARIABLES_DONE){
                    var var_count = 0;
                    var vars = [];
                    var props = [];
                    if (DATA_FROM_TIMESTAMP == -1){
                        var timestamp = SERVER_TIME;
                    }else{
                        var timestamp = DATA_FROM_TIMESTAMP;
                    }


                    for (var key in CHART_VARIABLE_KEYS){
                       if(CHART_VARIABLE_KEYS[key]<=DATA_INIT_STATUS){
                            CHART_VARIABLE_KEYS[key]++;
                            var_count++;
                            INIT_CHART_VARIABLES_COUNT++;
                            vars.push(key);
                            if (typeof(DATA[key]) == 'object'){
                                timestamp = Math.max(timestamp,DATA[key][0][0])
                            }
                            if(var_count >= 10){SINGLE_UPDATE = true;break;}
                       }
                    }
                    if(var_count>0){
                        if (timestamp === DATA_FROM_TIMESTAMP){
                            timestamp = DATA_DISPLAY_TO_TIMESTAMP;
                        }
                        if (timestamp == -1){
                            //var timestamp = SERVER_TIME;
                            var timestamp = DATA_TO_TIMESTAMP;
                        }
                        //data_handler_ajax(1,vars,props,timestamp-120*60*1000,timestamp);
                        data_handler_ajax(1,vars,props,DATA_FROM_TIMESTAMP,timestamp);
                    }else{
                        INIT_CHART_VARIABLES_DONE = true;
                        $('#PlusTwoHoursButton').removeClass("disabled");
                    }
                }
            }
        }
    }

    // call the data handler periodically
    if(!INIT_STATUS_VARIABLES_DONE || !INIT_CHART_VARIABLES_DONE){
        // initialisation is active
        setTimeout(function() {data_handler();}, REFRESH_RATE/2.0);
    }else{
        setTimeout(function() {data_handler();}, REFRESH_RATE);
    }
}

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

function data_handler_done(fetched_data){
    update_charts = true;
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
        LAST_QUERY_TIME = 0;
    }
    if (typeof(fetched_data['variable_properties'])==="object"){
        VARIABLE_PROPERTIES_DATA = fetched_data['variable_properties'];
        delete fetched_data['variable_properties'];
    }else{
        VARIABLE_PROPERTIES_DATA = {}
    }
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
            update_data_values('prop-' + key,value,null);
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
    if (UPDATE_X_AXES_TIME_LINE_STATUS){
        update_timeline();
    }
    // update all legend tables
    $('.legend table').trigger("update");
    $("#AutoUpdateButton").css("color", "");
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

function data_handler_fail(x, t, m) {
    //check if we are unauthenticated
    if (x.status !== 0 && x.getResponseHeader("content-type") !== null && x.getResponseHeader("content-type").indexOf("text/html") !== -1) {
        add_notification("Authentication failed, reload the page", 2, 0);
        location.reload();
    }

    if(JSON_ERROR_COUNT % 5 == 0)
        add_notification("Fetching data failed", 3);

    JSON_ERROR_COUNT = JSON_ERROR_COUNT + 1;
    if (JSON_ERROR_COUNT > 15) {
        $("#AutoUpdateStatus").css("color", "red")
        auto_update_click();
        add_notification("Fetching data failed limit reached, auto update deactivated.<br>Check your connectivity and active auto update in the top right corner.", 2, 0);
    } else if(JSON_ERROR_COUNT > 3){
        $("#AutoUpdateStatus").css("color", "orange")
        for (var key in VARIABLE_KEYS) {
            key = VARIABLE_KEYS[key];
            //add_fetched_data(key, [[DATA_TO_TIMESTAMP,Number.NaN]]);
        }
    }
    //hide_update_status();
    //$("#AutoUpdateButton").removeClass("btn-success");
    $("#AutoUpdateButton").css("color", "orange");
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

function update_data_values(key,val,time){
        if (key.split("-")[0] == "var") {type="variable"} else {type="variable_property"}

        if (time != null) {
            t = SERVER_TIME - time
            $(".type-numeric." + key).attr('data-original-title','last update ' + msToTime(t) + ' ago')
            $(".variable-config[data-value-timestamp][data-key=" + key.split("-")[1] + "][data-type=" + type + "]").attr('data-value-timestamp',time)
            polling_interval = $(".variable-config[data-device-polling_interval][data-key=" + key.split("-")[1] + "]").attr('data-device-polling_interval')
            if (time < SERVER_TIME - 10 * Math.max(1000 * polling_interval, REFRESH_RATE)) {
                $(".type-numeric." + key).parent().find('.glyphicon-alert').removeClass("hidden")
                $(".type-numeric." + key).parent().find('.glyphicon-exclamation-sign').addClass("hidden")
            }else if (time < SERVER_TIME - 3 * Math.max(1000 * polling_interval, REFRESH_RATE)) {
                $(".type-numeric." + key).parent().find('.glyphicon-alert').addClass("hidden")
                $(".type-numeric." + key).parent().find('.glyphicon-exclamation-sign').removeClass("hidden")
            }else {
                $(".type-numeric." + key).parent().find('.glyphicon-alert').addClass("hidden")
                $(".type-numeric." + key).parent().find('.glyphicon-exclamation-sign').addClass("hidden")
            }
        }

        if ($(".variable-config[data-refresh-requested-timestamp][data-key=" + key.split("-")[1] + "][data-type=" + type + "]").attr('data-refresh-requested-timestamp') != "" && time <= $(".variable-config[data-refresh-requested-timestamp][data-key=" + key.split("-")[1] + "][data-type=" + type + "]").attr('data-refresh-requested-timestamp')) {
            return;
        }

        if (typeof(val)==="number"){
            var r_val = Number(val);
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
            for (i = 0; i < $(".control-item.type-numeric." + key).length; ++i) {
                color_mode = $(".variable-config[data-color-mode][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-color-mode')
                if (color_mode != 1 ) {
                    r_val_temp = r_val
                    if (typeof $(".variable-config[data-timestamp-conversion][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-timestamp-conversion') != 'undefined' && $(".variable-config[data-timestamp-conversion][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-timestamp-conversion') != 0){
                        r_val_temp=timestamp_conversion($(".control-item.type-numeric." + key)[i].id,val);
                    }else if (typeof $(".variable-config[data-dictionary][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-dictionary') != 'undefined' && $(".variable-config[data-dictionary][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-dictionary') != 0){
                        r_val_temp=dictionary($(".control-item.type-numeric." + key)[i].id,val);
                    }
                    $("#" + $(".control-item.type-numeric." + key)[i].id).html(r_val_temp + " " + $(".variable-config[data-unit][data-key=" + key.split("-")[1] + "]").attr('data-unit'));
                }
                if ($(".variable-config[data-color-type][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-color-type') != 0 && $(".variable-config[data-color-mode][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-color-mode') != 0){
                    $($(".control-item.type-numeric." + key)[i]).css("background-color", update_data_colors($(".control-item.type-numeric." + key)[i].id,val))
                }
            }
            if (DATA_DISPLAY_FROM_TIMESTAMP > 0 && time < DATA_DISPLAY_FROM_TIMESTAMP) {
            }else if (DATA_DISPLAY_TO_TIMESTAMP > 0 && time > DATA_DISPLAY_TO_TIMESTAMP) {
            }else if (DATA_FROM_TIMESTAMP > 0 && time < DATA_FROM_TIMESTAMP) {
            }else if (DATA_TO_TIMESTAMP > 0 && time > DATA_TO_TIMESTAMP) {
            }else { $(".legendValue.type-numeric." + key).html(r_val); };
            $(".label .type-numeric." + key).html(r_val);
            $('input.'+ key).attr("placeholder",r_val);
            // unixtime
            var date = new Date(val*1000);
            $(".type-numeric.unixtime_local_date_time." + key).html(date.toLocaleString());
            $(".type-numeric.unixtime_utc_date_time." + key).html(date.toUTCString());
            $(".type-numeric.hex_str_full." + key).html(val.toString(16).toUpperCase());
        }

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
                val = 0
                //$(".type-numeric." + key).html(0);
                $('input.'+ key).attr("placeholder",0);
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
                val = 1
                $('button.btn-default.write-task-btn.' + key).addClass("update-able");
                $('button.update-able.write-task-btn.' + key).removeClass("btn-default");
                $('button.update-able.write-task-btn.' + key).addClass("btn-success");
                //$(".type-numeric." + key).html(1);
                $('input.'+ key).attr("placeholder",1);
            }
            $(".label .type-numeric." + key).html(val);
            if (DATA_DISPLAY_FROM_TIMESTAMP > 0 && time < DATA_DISPLAY_FROM_TIMESTAMP) {
            }else if (DATA_DISPLAY_TO_TIMESTAMP > 0 && time > DATA_DISPLAY_TO_TIMESTAMP) {
            }else if (DATA_FROM_TIMESTAMP > 0 && time < DATA_FROM_TIMESTAMP) {
            }else if (DATA_TO_TIMESTAMP > 0 && time > DATA_TO_TIMESTAMP) {
            }else { $(".legendValue.type-numeric." + key).html(val); };
            for (i = 0; i < $(".control-item.type-numeric." + key).length; ++i) {
                color_mode = $(".variable-config[data-color-mode][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-color-mode')
                if (color_mode != 1 ) {
                    r_val_temp = val
                    if (typeof($(".variable-config[data-timestamp-conversion][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-timestamp-conversion')) != 'undefined' && $(".variable-config[data-timestamp-conversion][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-timestamp-conversion') != 0){
                        r_val_temp=timestamp_conversion($(".control-item.type-numeric." + key)[i].id,val);
                    }else if (typeof($(".variable-config[data-dictionary][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-dictionary')) == 'string' && $(".variable-config[data-dictionary][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-dictionary') != ""){
                        r_val_temp=dictionary($(".control-item.type-numeric." + key)[i].id,val);
                    }
                    $("#" + $(".control-item.type-numeric." + key)[i].id).html(r_val_temp);
                }
                if ($(".variable-config[data-color-type][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-color-type') != 0 && $(".variable-config[data-color-mode][data-id=" + $(".control-item.type-numeric." + key)[i].id + "]").attr('data-color-mode') != 0){
                    $("#" + $(".control-item.type-numeric." + key)[i].id).css("background-color", update_data_colors($(".control-item.type-numeric." + key)[i].id,val))
                }
            }
        }
        if (typeof(val)==="object" && val === null){
            $(".type-numeric." + key).html(val);
            $('input.'+ key).attr("placeholder",val);
        }
        if (typeof(val)==="string"){
            $(".type-numeric." + key).html(val);
            $('input.'+ key).attr("placeholder",val);
        }

        refresh_logo(key.split("-")[1], type);
}

function refresh_logo(key, type){
    if (type == "variable") {type_short="var"} else {type_short = "prop"};
    $.each($(".control-item.type-numeric." + type_short + "-" + key + " img"), function(k,v){
        $(v).remove();
    });
    if ($(".variable-config[data-refresh-requested-timestamp][data-key=" + key + "][data-type=" + type + "]").attr('data-refresh-requested-timestamp')>$(".variable-config[data-value-timestamp][data-key=" + key + "][data-type=" + type + "]").attr('data-value-timestamp')) {
        $.each($(".control-item.type-numeric." + type_short + "-" + key), function(k,v){
            val_temp=$(v).html();
            $(v).prepend('<img style="height:14px;" src="/static/pyscada/img/load.gif" alt="refreshing">')
            //$(v).html('<img style="height:14px;" src="/static/pyscada/img/load.gif" alt="refreshing">' + val_temp);
        })
    }else {
        $.each($(".control-item.type-numeric." + type_short + "-" + key + " img"), function(k,v){
            $(v).remove();
        });
    }
}

function timestamp_conversion(id,val){
    if ($(".variable-config[data-timestamp-conversion][data-id=" + id + "]").attr('data-timestamp-conversion') == 1){
        // convert timestamp to local date
        val = new Date(val).toDateString();
    }else if ($(".variable-config[data-timestamp-conversion][data-id=" + id + "]").attr('data-timestamp-conversion') == 2){
        // convert timestamp to local time
        val = new Date(val).toTimeString();
    }else if ($(".variable-config[data-timestamp-conversion][data-id=" + id + "]").attr('data-timestamp-conversion') == 3){
        // convert timestamp to local date and time
        val = new Date(val).toUTCString();
    }
    return val;
}

function dictionary(id,val){
    if ($(".variable-config[data-dictionary][data-id=" + id + "]").attr('data-dictionary')){
        // apply dictionary
        t = JSON.parse($(".variable-config[data-dictionary][data-id=" + id + "]").attr('data-dictionary'))
        if (val in t) {
            val = t[val]
        }
    }
    return val;
}

function update_data_colors(id,val){
    color_type = $(".variable-config[data-color-type][data-id=" + id + "]").attr('data-color-type')
    color_mode = $(".variable-config[data-color-mode][data-id=" + id + "]").attr('data-color-mode')
    color_level_1_type = $(".variable-config[data-level-1-type][data-id=" + id + "]").attr('data-level-1-type')
    color_level_2_type = $(".variable-config[data-level-2-type][data-id=" + id + "]").attr('data-level-2-type')
    color_level_1 = $(".variable-config[data-level-1][data-id=" + id + "]").attr('data-level-1')
    color_level_2 = $(".variable-config[data-level-2][data-id=" + id + "]").attr('data-level-2')
    color_1 = $(".variable-config[data-color-1][data-id=" + id + "]").attr('data-color-1')
    color_2 = $(".variable-config[data-color-2][data-id=" + id + "]").attr('data-color-2')
    color_3 = $(".variable-config[data-color-3][data-id=" + id + "]").attr('data-color-3')

    if ($(".variable-config[data-value-class][data-id=" + id + "]").attr('data-value-class') == 'BOOLEAN') {
        color_type = 1
        color_level_1 = 1
        color_level_1_type = 1
        if (val == false) { val = 0 } else if ( val == true ) { val = 1 }
    }

    color = null

    if (color_type == 1) {
        if (color_level_1_type == 0) {
            if (val <= color_level_1) {
                color = color_1
            }else {
                color = color_2
            }
        }else if (color_level_1_type == 1) {
            if (val < color_level_1) {
                color = color_1
            }else {
                color = color_2
            }
        }
    }else if (color_type == 2) {
        if (color_level_1_type == 0) {
            if (val <= color_level_1) {
                color = color_1
            }else if (color_level_2_type == 0) {
                if (val <= color_level_2) {
                    color = color_2
                }else {
                    color = color_3
                }
            }else {
                if (val < color_level_2) {
                    color = color_2
                }else {
                    color = color_3
                }
            }
        }else if (color_level_1_type == 1) {
            if (val < color_level_1) {
                color = color_1
            }else if (color_level_2_type == 0) {
                if (val <= color_level_2) {
                    color = color_2
                }else {
                    color = color_3
                }
            }else {
                if (val < color_level_2) {
                    color = color_2
                }else {
                    color = color_3
                }
            }
        }
    }else if (color_type == 3) {
        if (val <= color_level_1) {
            color = color_1
        }else if (val >= color_level_2) {
            color = color_2
        }else {
            fade = (val-color_level_1)/(color_level_2-color_level_1);
            color_1_new = new Color(color_1.match(/\d+/g)[0],color_1.match(/\d+/g)[1],color_1.match(/\d+/g)[2])
            color_2_new = new Color(color_2.match(/\d+/g)[0],color_2.match(/\d+/g)[1],color_2.match(/\d+/g)[2])
            color = colorGradient(fade, color_1_new, color_2_new)
        }
    }

    //console.log(id + " " + color_mode + " " + color_type + " " + color);
    return color;
}

function Color(red,green,blue) {
    this.red = red;
    this.green = green;
    this.blue = blue;
}

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

function set_x_axes(){
    if(!progressbar_resize_active){
        $.each(PyScadaPlots,function(plot_id){
            var self = this, doBind = function() {
                PyScadaPlots[plot_id].update(false);
            };
            $.browserQueue.add(doBind, this);
        });
        // update the progressbar
        update_timeline();
    }
}

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
    var date = new Date(DATA_FROM_TIMESTAMP);
    $("#timeline-time-left-label").html(date.toLocaleString());

    // Update DateTime pickers
    $("#datetimepicker_from").datetimepicker('enable');
    $('#datetimepicker_from').datetimepicker('date', new Date(DATA_FROM_TIMESTAMP))
    $("#datetimepicker_to").datetimepicker('enable');
    $('#datetimepicker_to').datetimepicker('date', new Date(DATA_TO_TIMESTAMP))
}

function progressbarSetWindow( event, ui ) {
    $.each(PyScadaPlots,function(plot_id){
        var self = this, doBind = function() {
            PyScadaPlots[plot_id].update(false);
        };
        $.browserQueue.add(doBind, this);
    });

    progressbar_resize_active = false;
}

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

function PyScadaPlot(id, plotPoints, plotLines, lineSteps, yaxisUniqueScale){
    var options = {
        legend: {
            position: "nw",
            show: false,
            container: null,
            //container: document.getElementById("legendContainer"),
            //container: $(".legendContainer")[0],
            //container: $('#chart-legend-' + id + ' .legend')[0],
        },
        series: {
            shadowSize: 0,
            lines: {
                show: plotLines,
                lineWidth: 3,
                steps: lineSteps,
                fill: false,
            },
            points: {
                show: plotPoints,
                radius: 4,
                symbol: "cross",
            },
        bars: {
                show: false,
                barWidth: [1, false],
                align: "center",
            },
        },
        xaxis: {
            mode: "time",
            ticks: $('#chart-container-'+id).data('xaxisTicks'),
            timeformat: "%d/%m/%Y<br>%H:%M:%S",
            timezone: "browser",
            timeBase: "milliseconds",
            autoScale: "none"
        },
        yaxis: {
            position: "left",
            autoScale: "loose",
            autoScaleMargin: 0.1,
            min: null,
            max: null,
        },
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
    flotPlot,			// handle to plot
    prepared = false,	//
    legend_id = '#chart-legend-' + id,
    legend_table_id = '#chart-legend-table-' + id,
    chart_container_id = '#chart-container-'+id,
    legend_checkbox_id = '#chart-legend-checkbox-' + id + '-',
    legend_checkbox_status_id = '#chart-legend-checkbox-status-' + id + '-',
    legend_value_id = '#chart-legend-value-' + id + '-',
    variables = {},
    plot = this;


    // public functions
    plot.update 			= update;
    plot.prepare 			= prepare;
    plot.resize 			= resize;
    plot.updateLegend 		= updateLegend;
    plot.getSeries 			= function () { return series };
    plot.getFlotObject		= function () { return flotPlot};
    plot.getKeys			= function (){ return keys};
    plot.getVariableNames	= function (){ return variable_names};

    plot.getInitStatus		= function () { if(InitDone){return InitRetry}else{return false}};
    plot.getId				= function () {return id};
    plot.getChartContainerId= function () {return chart_container_id};
    // init data
    $.each($(legend_table_id + ' .variable-config'),function(key,val){
        val_inst = $(val);
        variable_name = val_inst.data('name');
        variable_key = val_inst.data('key');
        variables[variable_key] = {'color':val_inst.data('color'),'yaxis':1}
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


    function prepare(){
        // prepare legend table sorter
        $(legend_table_id).tablesorter({sortList: [[2,0]]});

        // add onchange function to every checkbox in legend
        $.each(variables,function(key,val){
            $(legend_checkbox_id+key).change(function() {
                plot.update(false);
                if ($(legend_checkbox_id+key).is(':checked')){
                    $(legend_checkbox_status_id+key).html(1);
                }else{
                    $(legend_checkbox_status_id+key).html(0);
                }
            });
        });
        //
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
            plot.update(false);
         });
        // expand the chart to the maximum width
        main_chart_area  = $(chart_container_id).closest('.main-chart-area');


        contentAreaHeight = main_chart_area.parent().height();
        mainChartAreaHeight = main_chart_area.height();

        if (contentAreaHeight>mainChartAreaHeight){
            main_chart_area.height(contentAreaHeight);
        }

        flotPlot = $.plot($(chart_container_id + ' .chart-placeholder'), series, options);
        set_chart_selection_mode();
        // update the plot
        update(false);

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
                opts = item.series.xaxis.options
                if (opts.mode == "time") {
                    dG = $.plot.dateGenerator(Number(item.datapoint[0].toFixed(0)), opts)
                    dF = $.plot.formatDate(dG, opts.timeformat, opts.monthNames, opts.dayNames);
                    var x = dF,
                        y = item.datapoint[1].toFixed(2);
                }else {
                    var x = item.datapoint[0].toFixed(2),
                        y = item.datapoint[1].toFixed(2);
                }
                y_label = (typeof item.series.label !== 'undefined') ? item.series.label : "T"
                y_unit = (typeof item.series.unit !== 'undefined') ? item.series.unit : ""
                $("#tooltip").html(y_label + " (" + x + ") = " + y + " " + y_unit)
                    .css({top: item.pageY+5, left: item.pageX+5, "z-index": 91})
                    .show();
                    //.fadeIn(200);
            } else {
                $("#tooltip").hide();
            }

            setCrosshairs(flotPlot, id);

        }).bind("mouseleave", function (event, pos, item) {
            if(! flotPlot.getOptions().crosshair.locked) {
                delCrosshairs(flotPlot);
            }
        }).bind("mousedown", function (e) {
            var offset = flotPlot.getPlaceholder().offset();
            var plotOffset = flotPlot.getPlotOffset();
            pos={};
            pos.x = clamp(0, e.pageX - offset.left - plotOffset.left, flotPlot.width());
            pos.y = clamp(0, e.pageY - offset.top - plotOffset.top, flotPlot.height());
			flotPlot.getOptions().crosshair.lastPositionMouseDown = pos
		}).bind("mouseup", function (e) {
			var offset = flotPlot.getPlaceholder().offset();
            var plotOffset = flotPlot.getPlotOffset();
            pos={};
            pos.x = clamp(0, e.pageX - offset.left - plotOffset.left, flotPlot.width());
            pos.y = clamp(0, e.pageY - offset.top - plotOffset.top, flotPlot.height());
			old_pos = flotPlot.getOptions().crosshair.lastPositionMouseDown
			if (flotPlot.getOptions().crosshair.locked) {
			    flotPlot.getOptions().crosshair.lastPosition.x = pos.x
			    flotPlot.getOptions().crosshair.lastPosition.y = pos.y
			    unlockCrosshairs(flotPlot);
                setCrosshairs(flotPlot, id);
			} else if (pos.x == old_pos.x && pos.y == old_pos.y) {
                setCrosshairs(flotPlot, id)
                lockCrosshairs();
			}
		}).bind("plotselected", function(event, ranges) {
            pOpt = flotPlot.getOptions();
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
            if ($(chart_container_id + " .activate_zoom_x").is(':checked') && ranges.xaxis != null) {
                DATA_DISPLAY_TO_TIMESTAMP = ranges.xaxis.to;
                DATA_DISPLAY_FROM_TIMESTAMP = ranges.xaxis.from;
                DATA_DISPLAY_WINDOW = DATA_DISPLAY_TO_TIMESTAMP-DATA_DISPLAY_FROM_TIMESTAMP;
                set_x_axes();
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
        }

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

        $(chart_container_id + " .btn.btn-default.chart-ResetSelection").click(function() {
            e = jQuery.Event( "click" );
            jQuery(chart_container_id + " .btn.btn-default.chart-ZoomYToFit").trigger(e);
            jQuery(chart_container_id + " .btn.btn-default.chart-ZoomXToFit").trigger(e);
        });

        $(chart_container_id + " .btn.btn-default.chart-ZoomYToFit").click(function() {
            pOpt = flotPlot.getOptions();
            pOpt.yaxes[0].autoScale = "loose";
            update(false);
        });
        $(chart_container_id + " .btn.btn-default.chart-ZoomXToFit").click(function() {
            DATA_DISPLAY_FROM_TIMESTAMP = -1;
            DATA_DISPLAY_TO_TIMESTAMP = -1;
            DATA_DISPLAY_WINDOW = DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP
            set_x_axes();
        });
    }


    function update(force){
        if(!prepared ){
            if($(chart_container_id).is(":visible")){
                prepared = true;
                prepare();
            }else{
                return;
            }
        }
        if($(chart_container_id).is(":visible") || force){
            // only update if plot is visible
            // add the selected data series to the "series" variable
            series = [];
            start_id = 0;
            for (var key in keys){
                key = keys[key];
                if($(legend_checkbox_id+key).is(':checked') && typeof(DATA[key]) === 'object'){
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
                        continue;
                    }else {
                        chart_data = DATA[key].slice(start_id,stop_id+1);
                    };
                    // append last value
                    //if (chart_data.length >= 1){
                    //    if (DATA_DISPLAY_TO_TIMESTAMP < 0){
                    //        chart_data.push([DATA_TO_TIMESTAMP,chart_data[chart_data.length-1][1]]);
                    //    }else{
                    //        chart_data.push([DATA_DISPLAY_TO_TIMESTAMP,chart_data[chart_data.length-1][1]]);
                    //    }
                    //}
                    series.push({"data":chart_data,"color":variables[key].color,"yaxis":variables[key].yaxis,"label":variables[key].label,"unit":variables[key].unit, "key":key});
                }
            }

            // update x window
            pOpt = flotPlot.getOptions();

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

            pOpt.xaxes[0].key=0

            // update flot plot
            flotPlot.setData(series);
            flotPlot.setupGrid(true);
            flotPlot.draw();
        }
    }

    function resize() {
        if (typeof(flotPlot) !== 'undefined') {
            flotPlot.resize();
            flotPlot.setupGrid(true);
            flotPlot.draw();
        }
    }
}

function XYPlot(id, xaxisVarId, xaxisLinLog, plotPoints, plotLines, lineSteps, yaxisUniqueScale){
    var options = {
        yaxes: [],
        xaxis: {
            mode: (xaxisLinLog == true ? "log" : null),
            autoScale: "exact",
            showTickLabels: "all"
        },
        series: {
            lines: {
                show: plotLines,
                lineWidth: 3,
                steps: lineSteps,
            },
            points: {
                show: plotPoints,
                radius: 4,
                symbol: "cross",
            }
        },
        legend: {
            show: false
        },
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
            //to show points informations
            hoverable: true,
            clickable: true
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
    flotPlot,			// handle to plot
    prepared = false,	//
    legend_id = '#chart-legend-' + id,
    legend_table_id = '#chart-legend-table-' + id,
    chart_container_id = '#xy-chart-container-'+id,
    legend_checkbox_id = '#chart-legend-checkbox-' + id + '-',
    legend_checkbox_status_id = '#chart-legend-checkbox-status-' + id + '-',
    legend_value_id = '#chart-legend-value-' + id + '-',
    variables = {},
    plot = this;


    // public functions
    plot.update 			= update;
    plot.prepare 			= prepare;
    plot.resize 			= resize;
    plot.updateLegend 		= updateLegend;
    plot.getSeries 			= function () { return series };
    plot.getFlotObject		= function () { return flotPlot};
    plot.getKeys			= function (){ return keys};
    plot.getVariableNames	= function (){ return variable_names};

    plot.getInitStatus		= function () { if(InitDone){return InitRetry}else{return false}};
    plot.getId				= function () {return id};
    plot.getChartContainerId= function () {return chart_container_id};
    // init data
    k=1
    $.each($(legend_table_id + ' .variable-config'),function(key,val){
        val_inst = $(val);
        variable_name = val_inst.data('name');
        variable_key = val_inst.data('key');
        variables[variable_key] = {'color':val_inst.data('color'),'yaxis':k}
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
        if (options.yaxes[k-1] == null) {
            options.yaxes[k-1] = {};
        };
        if(k%2){pos="left";}else{pos="right";};
        tf = function (value, axis) {
            return value.toFixed(axis.tickDecimals) + ((typeof axis.options.unit != "undefined") ? axis.options.unit : '');
        };
        if (variables[variable_key].unit != "") {
            lb = variables[variable_key].label.replace(/\s/g, '') + " (" + variables[variable_key].unit + ")";
        }else{
            lb = variables[variable_key].label.replace(/\s/g, '');
        }
        options.yaxes[k-1].position = pos;
        options.yaxes[k-1].tickFormatter = tf;
        if (yaxisUniqueScale == false) {
            options.yaxes[k-1].axisLabel = lb;
            //options.yaxes[k-1].axisLabelUseCanvas = true;
            //options.yaxes[k-1].axisLabelFontSizePixels = 12;
            //options.yaxes[k-1].axisLabelFontFamily = 'Verdana, Arial';
            //options.yaxes[k-1].axisLabelPadding = 3;
            //options.yaxes[k-1].axisLabelColour = variables[variable_key]['color'];
        }
        if (yaxisUniqueScale == false || $(legend_table_id + ' .variable-config').length == 1) {
            options.yaxes[k-1].unit = variables[variable_key].unit;
        }else {
            options.yaxes[k-1].unit = ""
        }
        options.yaxes[k-1].labelWidth = null;
        options.yaxes[k-1].reserveSpace = false;
        k += 1;
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
            if (p1 == null) {
                y = p2[1];
            } else if (p2 == null) {
                y = p1[1];
            } else {
                y = p1[1] + (p2[1] - p1[1]) * (pos.x - p1[0]) / (p2[0] - p1[0]);
            }
            if(typeof(y) === "number"){$(legend_value_id+key).text(y.toFixed(2));};
        }
    }


    function prepare(){
        // prepare legend table sorter
        $(legend_table_id).tablesorter({sortList: [[2,0]]});

        // add onchange function to every checkbox in legend
        $.each(variables,function(key,val){
            $(legend_checkbox_id+key).change(function() {
                flotPlot.clearTextCache();
                plot.update(false);
                if ($(legend_checkbox_id+key).is(':checked')){
                    $(legend_checkbox_status_id+key).html(1);
                }else{
                    $(legend_checkbox_status_id+key).html(0);
                }
            });
        });
        //
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
            flotPlot.clearTextCache();
            plot.update(false);
         });
        // expand the chart to the maximum width
        main_chart_area  = $(chart_container_id).closest('.main-chart-area');


        contentAreaHeight = main_chart_area.parent().height();
        mainChartAreaHeight = main_chart_area.height();

        if (contentAreaHeight>mainChartAreaHeight){
            main_chart_area.height(contentAreaHeight);
        }

        //
        flotPlot = $.plot($(chart_container_id + ' .chart-placeholder'), series, options)
        set_chart_selection_mode();
        // update the plot
        update(false);

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
                opts = item.series.xaxis.options
                if (opts.mode == "time") {
                    dG = $.plot.dateGenerator(Number(item.datapoint[0].toFixed(0)), opts)
                    dF = $.plot.formatDate(dG, opts.timeformat, opts.monthNames, opts.dayNames);
                    var x = dF,
                        y = item.datapoint[1].toFixed(2);
                }else {
                    var x = item.datapoint[0].toFixed(2),
                        y = item.datapoint[1].toFixed(2);
                }
                $("#tooltip").html(item.series.label + "(" + x + ") = " + y + " " + item.series.unit)
                    .css({top: item.pageY+5, left: item.pageX+5, "z-index": 91})
                    .show();
                    //.fadeIn(200);
            } else {
                $("#tooltip").hide();
            }

            setCrosshairs(flotPlot, id);

        }).bind("mouseleave", function (event, pos, item) {
            if(! flotPlot.getOptions().crosshair.locked) {
                delCrosshairs(flotPlot);
            }
        }).bind("mousedown", function (e) {
            var offset = flotPlot.getPlaceholder().offset();
            var plotOffset = flotPlot.getPlotOffset();
            pos={};
            pos.x = clamp(0, e.pageX - offset.left - plotOffset.left, flotPlot.width());
            pos.y = clamp(0, e.pageY - offset.top - plotOffset.top, flotPlot.height());
			flotPlot.getOptions().crosshair.lastPositionMouseDown = pos
		}).bind("mouseup", function (e) {
			var offset = flotPlot.getPlaceholder().offset();
            var plotOffset = flotPlot.getPlotOffset();
            pos={};
            pos.x = clamp(0, e.pageX - offset.left - plotOffset.left, flotPlot.width());
            pos.y = clamp(0, e.pageY - offset.top - plotOffset.top, flotPlot.height());
			old_pos = flotPlot.getOptions().crosshair.lastPositionMouseDown
			if (flotPlot.getOptions().crosshair.locked) {
			    flotPlot.getOptions().crosshair.lastPosition.x = pos.x
			    flotPlot.getOptions().crosshair.lastPosition.y = pos.y
			    unlockCrosshairs(flotPlot);
                setCrosshairs(flotPlot, id);
			} else if (pos.x == old_pos.x && pos.y == old_pos.y) {
                setCrosshairs(flotPlot, id)
                lockCrosshairs();
			}
		}).bind("plotselected", function(event, ranges) {
            pOpt = flotPlot.getOptions();
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
                update(false);
            }
            pOpt = flotPlot.getOptions();
            if ($(chart_container_id + " .activate_zoom_x").is(':checked') && ranges.xaxis != null) {
                pOpt.xaxes[0].min = ranges.xaxis.from;
                pOpt.xaxes[0].max = ranges.xaxis.to;
                pOpt.xaxes[0].autoScale = "none";
                update(false);
            }
            flotPlot.clearSelection();
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
        }

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

        $(chart_container_id + " .btn.btn-default.chart-ResetSelection").click(function() {
            e = jQuery.Event( "click" );
            jQuery(chart_container_id + " .btn.btn-default.chart-ZoomYToFit").trigger(e);
            jQuery(chart_container_id + " .btn.btn-default.chart-ZoomXToFit").trigger(e);
        });

        $(chart_container_id + " .btn.btn-default.chart-ZoomYToFit").click(function() {
            pOpt = flotPlot.getOptions();
            for (y in pOpt.yaxes){
                pOpt.yaxes[y].autoScale = "loose";
            }
            update(false);
        });
        $(chart_container_id + " .btn.btn-default.chart-ZoomXToFit").click(function() {
            pOpt = flotPlot.getOptions();
            pOpt.xaxes[0].autoScale = "exact";
            update(false);
        });
    }


    function update(force){
        if(!prepared ){
            if($(chart_container_id).is(":visible")){
                prepared = true;
                prepare();
            }else{
                return;
            }
        }
        if($(chart_container_id).is(":visible") || force){
            // only update if plot is visible
            // add the selected data series to the "series" variable
            series = [];
            start_id = 0;
            j=0;
            jk=1;
            for (var key in keys){
                key = keys[key];
                xkey = xaxisVarId
                if($(legend_checkbox_id+key).is(':checked') && typeof(DATA[key]) === 'object' && typeof(DATA[xkey]) === 'object'){
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
                        continue;
                    }else {
                        chart_data = DATA[key].slice(start_id,stop_id+1);
                    };
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
                        for (iy=0; iy < chart_data.length; iy++) {
                            ix=0;
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
                                    }
                                    ix+=1;
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
                    };
                    $.each($(legend_table_id + ' .legendSeries'),function(kkey,val){
                        val_inst = $(val);
                        if (key == val_inst.find(".variable-config").data('key')){
                            label = val_inst.find(".legendLabel").text();
                            unit = val_inst.find(".legendUnit").text();
                        }
                    });
                    if (new_data.length > 0){
                        j += 1;
                        if (yaxisUniqueScale) {yj = 1} else {yj = jk}
                        //plot Y with defferents axis
                        series.push({"data":new_data, "xdata":chart_x_data,"color":variables[key].color,"yaxis":yj,"label":variables[key].label,"unit":variables[key].unit,"chart_data_min":chart_data_min,"chart_data_max":chart_data_max,"x_data_min":x_data_min,"x_data_max":x_data_max, "key":key});
                    };
                };
                jk += 1;
            };

            //update y window
            pOpt = flotPlot.getOptions();
            if (j != 0){
                for (k = 1;k <= j;k++){
                    S = series[k-1]
                    if (typeof S !== 'undefined') {
                        if (yaxisUniqueScale == false || $(legend_table_id + ' .variable-config').length == 1) {
                            pOpt.yaxes[S['yaxis']-1].unit = S['unit'];
                        }else {
                            options.yaxes[S['yaxis']-1].unit = ""
                        }
                        pOpt.alignTicksWithAxis = 1;
                        if (k==1) {
                            pOpt.yaxes[S['yaxis']-1].chart_data_min = S['chart_data_min'];
                            pOpt.yaxes[S['yaxis']-1].chart_data_max = S['chart_data_max'];
                        }else {
                            pOpt.yaxes[S['yaxis']-1].chart_data_min = Math.min(S['chart_data_min'],pOpt.yaxes[S['yaxis']-1].chart_data_min);
                            pOpt.yaxes[S['yaxis']-1].chart_data_max = Math.max(S['chart_data_max'],pOpt.yaxes[S['yaxis']-1].chart_data_max);
                        }
                    }
                }
            }

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

            // update flot plot
            flotPlot.setData(series);
            flotPlot.setupGrid(true);
            flotPlot.draw();

            // Change the color of the axis
            if (jk != 1 && yaxisUniqueScale == false){
                for (k = 1;k <= jk;k++){
                    S = series[k-1]
                    if (typeof S !== 'undefined') {
                        $(chart_container_id + ' .axisLabels.y' + S['yaxis'] + 'Label').css('fill',S['color'])
                        $(chart_container_id + ' .flot-y' + S['yaxis'] + '-axis text').css('fill',S['color'])
                    }
                }
            }
        }
    }

    function resize() {
        if (typeof(flotPlot) !== 'undefined') {
            flotPlot.resize();
            flotPlot.setupGrid(true);
            flotPlot.draw();
        }
    }
}

function Pie(id){
    var options = {
        series: {
            pie: {
                show: true,
                innerRadius: 0.4,
                label: {
                    show: true,
                    //radius: 1,
                    //formatter: labelFormatter,
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
    flotPlot,			// handle to plot
    prepared = false,	//
    chart_container_id = '#chart-container-'+id,
    legend_table_id = '#chart-legend-table-' + id,
    legend_checkbox_id = '#chart-legend-checkbox-' + id + '-',
    legend_checkbox_status_id = '#chart-legend-checkbox-status-' + id + '-',
    variables = {},
    plot = this;

    // public functions
    plot.update 			= update;
    plot.prepare 			= prepare;
    plot.resize 			= resize;
    plot.getSeries 			= function () { return series };
    plot.getFlotObject		= function () { return flotPlot};
    plot.getKeys			= function (){ return keys};
    plot.getVariableNames	= function (){ return variable_names};

    plot.getInitStatus		= function () { if(InitDone){return InitRetry}else{return false}};
    plot.getId				= function () {return id};
    plot.getChartContainerId= function () {return chart_container_id};

    // init data
    $.each($(legend_table_id + ' .variable-config'),function(key,val){
        val_inst = $(val);
        variable_name = val_inst.data('name');
        variable_key = val_inst.data('key');
        variables[variable_key] = {'color':val_inst.data('color'),'yaxis':1}
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

    function labelFormatter(label, series) {
		return "<div style='font-size:8pt; text-align:center; padding:2px; color:white;'>" + label + "<br/>" + Math.round(series.percent) + "%</div>";
	}

    function prepare(){
        // prepare legend table sorter
        $(legend_table_id).tablesorter({sortList: [[2,0]]});

        // add onchange function to every checkbox in legend
        $.each(variables,function(key,val){
            $(legend_checkbox_id+key).change(function() {
                plot.update(false);
                if ($(legend_checkbox_id+key).is(':checked')){
                    $(legend_checkbox_status_id+key).html(1);
                }else{
                    $(legend_checkbox_status_id+key).html(0);
                }
            });
        });
        //
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
            plot.update(false);
        });
        // expand the pie to the maximum width
        main_chart_area = $(chart_container_id).closest('.main-chart-area');


        contentAreaHeight = main_chart_area.parent().height();
        mainChartAreaHeight = main_chart_area.height();

        if (contentAreaHeight>mainChartAreaHeight){
            main_chart_area.height(contentAreaHeight);
        }

        // Since CSS transforms use the top-left corner of the label as the transform origin,
        // we need to center the y-axis label by shifting it down by half its width.
        // Subtract 20 to factor the chart's bottom margin into the centering.
        var chartTitle = $(chart_container_id + ' .chartTitle');
        chartTitle.css("margin-left", -chartTitle.width() / 2);
        var xaxisLabel = $(chart_container_id + ' .axisLabel.xaxisLabel');
        xaxisLabel.css("margin-left", -xaxisLabel.width() / 2);
        var yaxisLabel = $(chart_container_id + ' .axisLabel.yaxisLabel');
        yaxisLabel.css("margin-top", yaxisLabel.width() / 2 - 20);

        if (series.length > 0) {
            flotPlot = $.plot($(chart_container_id + ' .chart-placeholder'), series, options)
            // update the plot
            update(false);
        }else {
            //prepared = false;
        }
    };

    function update(force){
        if(!prepared ){
            if($(chart_container_id).is(":visible")){
                prepared = true;
                prepare();
            }else{
                return;
            }
        }
        if(prepared && ($(chart_container_id).is(":visible") || force)){
            // only update if plot is visible
            // add the selected data series to the "series" variable
            series = [];
            for (var key in keys){
                key = keys[key];
                if($(legend_checkbox_id+key).is(':checked') && typeof(DATA[key]) === 'object'){
                    series.push({"data":DATA[key][DATA[key].length - 1], "label":variables[key].label,"unit":variables[key].unit, "color":variables[key].color});
                };
            };
            if (series.length > 0) {
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

    function resize() {
        if (typeof(flotPlot) !== 'undefined') {
            flotPlot.resize();
            flotPlot.setupGrid(true);
            flotPlot.draw();
        }
    }
}

function clamp(min, value, max) {
    return value < min ? min : (value > max ? max : value);
}

function delCrosshairs(flotPlot) {
        $.each(PyScadaPlots,function(plot_id){
            if (typeof PyScadaPlots[plot_id].getFlotObject() !== 'undefined') {
                PyScadaPlots[plot_id].getFlotObject().setCrosshair();
                PyScadaPlots[plot_id].getFlotObject().getOptions().crosshair.mode = 'xy'
            }
            $('.chart-legend-value-' + PyScadaPlots[plot_id].getId()).addClass('type-numeric');
        });
}

function unlockCrosshairs(flotPlot) {
        $.each(PyScadaPlots,function(plot_id){
            if (typeof PyScadaPlots[plot_id].getFlotObject() !== 'undefined') {
                PyScadaPlots[plot_id].getFlotObject().unlockCrosshair();
            }
        });
}

function lockCrosshairs() {
        $.each(PyScadaPlots,function(plot_id){
            if (typeof PyScadaPlots[plot_id].getFlotObject() !== 'undefined') {
                PyScadaPlots[plot_id].getFlotObject().lockCrosshair();
            }
        });
}

function setCrosshairs(flotPlot, id) {
    //test if function setCrosshairs exist in hooks.drawOverlay before add it
    $('.chart-legend-value-' + id).removeClass('type-numeric');
    pOpt=flotPlot.getOptions();
    $.each(PyScadaPlots,function(plot_id){
        if(typeof(pOpt.crosshair) !== 'undefined' && pOpt.crosshair.lastPosition.x !== -1  && pOpt.crosshair.lastPosition.x !== 0 && !pOpt.crosshair.locked) {
            if(typeof(PyScadaPlots[plot_id].getFlotObject()) !== 'undefined' && PyScadaPlots[plot_id].getFlotObject().getOptions().xaxes.length === pOpt.xaxes.length){
                if (PyScadaPlots[plot_id].getFlotObject().getOptions().xaxes.length === 1 && pOpt.xaxes.length === 1 && PyScadaPlots[plot_id].getFlotObject().getOptions().xaxes[0].key === pOpt.xaxes[0].key) {
                    PyScadaPlots[plot_id].getFlotObject().setCrosshair(flotPlot.c2p({left:pOpt.crosshair.lastPosition.x, top:pOpt.crosshair.lastPosition.y}))
                    $('.chart-legend-value-' + PyScadaPlots[plot_id].getId()).removeClass('type-numeric');
                    setTimeout(PyScadaPlots[plot_id].updateLegend(), 50);
                    if (PyScadaPlots[plot_id].getId() == id) {
                        PyScadaPlots[plot_id].getFlotObject().getOptions().crosshair.mode = 'xy'
                    }else {
                        PyScadaPlots[plot_id].getFlotObject().getOptions().crosshair.mode = 'x'
                    }
                }else {
                    PyScadaPlots[plot_id].getFlotObject().setCrosshair();
                    PyScadaPlots[plot_id].getFlotObject().getOptions().crosshair.mode = 'xy'
                    $('.chart-legend-value-' + PyScadaPlots[plot_id].getId()).addClass('type-numeric');
                }
            }
        }
    });
}

function find_index(a,t){
    var i = a.length; //or 10
    while(i--){
        if (a[i]<=t){
            return i
        }
    }
}

function find_index_sub_lte(a,t,d){
    var i = a.length; //or 10
    while(i--){
        if (a[i][d]<=t){
            return i
        }
    }
}

function find_index_sub_gte(a,t,d){
    var i = 0; //or 10
    while(i < a.length){
        if (a[i][d]>=t){
            return i
        }
        i++;
    }
}

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

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", CSRFTOKEN);
        }
    }
});

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

//form/read-task

$('button.read-task-set').click(function(){
    t = SERVER_TIME
    key = $(this).data('key');
    type = $(this).data('type');
    $(".variable-config[data-key=" + key + "][data-type=" + type + "]").attr('data-refresh-requested-timestamp',t)
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
})

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
    if (min_type == 'lte') {min_type_char = ">="} else {min_type_char = ">"};
    if (max_type == 'gte') {max_type_char = "<="} else {max_type_char = "<"};
    if (value == "" || value == null) {
        $(this).parents(".input-group").addClass("has-error");
        $(this).parents(".input-group").find('.help-block').remove()
        $(this).parents(".input-group-btn").after('<span id="helpBlock-' + id + '" class="help-block">Please provide a value !</span>');
    }else {
        $(this).parents(".input-group").find('.help-block').remove()
        check_mm = check_min_max(parseFloat(value), parseFloat(min), parseFloat(max), min_type, max_type)
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
                            add_notification('write property failed',3);
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
                        add_notification('write task failed',3);
                    }
                });
            };
        };
    };
});

$('button.write-task-form-set').click(function(){
    err = false;
    id_form = $(this.form).attr('id');
    tabinputs = $.merge($('#'+id_form+ ' :text'),$('#'+id_form+ ' :input:hidden'));
    for (i=0;i<tabinputs.length;i++){ //test if there is an empty or non numeric value
        value = $(tabinputs[i]).val();
        id = $(tabinputs[i]).attr('id');
        var_name = $(tabinputs[i]).attr("name");
        val=$('.variable-config[data-id='+id.replace('-value', '')+']')
        key = parseInt($(val).data('key'));
        item_type = $(val).data('type');
        value_class = $(val).data('value-class');
        min = $(val).data('min');
        max = $(val).data('max');
        min_type = $(val).data('min-type');
        max_type = $(val).data('max-type');
        if (min_type == 'lte') {min_type_char = ">="} else {min_type_char = ">"};
        if (max_type == 'gte') {max_type_char = "<="} else {max_type_char = "<"};

        if (value == "" || value == null){
            $(tabinputs[i]).parents(".input-group").addClass("has-error");
            $(tabinputs[i]).parents(".input-group").find('.help-block').remove()
            $(tabinputs[i]).parents(".input-group").append('<span id="helpBlock-' + id + '" class="help-block">Please provide a value !</span>');
            err = true;
        }else {
            $(tabinputs[i]).parents(".input-group").find('.help-block').remove()
            check_mm = check_min_max(parseFloat(value), parseFloat(min), parseFloat(max), min_type, max_type)
            if (check_mm == -1) {
                $(tabinputs[i]).parents(".input-group").addClass("has-error");
                $(tabinputs[i]).parents(".input-group").append('<span id="helpBlock-' + id + '" class="help-block">Enter a value ' + min_type_char + ' ' + min + '</span>');
                err = true;
            }else if (check_mm == 1) {
                $(tabinputs[i]).parents(".input-group").addClass("has-error");
                $(tabinputs[i]).parents(".input-group").append('<span id="helpBlock-' + id + '" class="help-block">Enter a value ' + max_type_char + ' ' + max + '</span>');
                err = true;
            }else if (check_mm == 0) {
                $(tabinputs[i]).parents(".input-group").removeClass("has-error")
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
    };
    tabselects = $('#'+id_form+ ' .select');
    for (i=0;i<tabselects.length;i++){ //test if there is an empty value
        value = $(tabselects[i]).val();
        id = $(tabselects[i]).attr('id');
        var_name = $(tabselects[i]).data("name");
        val=$('.variable-config[data-id='+id.replace('-value', '')+']')
        key = parseInt($(val).data('key'));
        item_type = $(val).data('type');
        value_class = $(val).data('value-class');
        min = $(val).data('min');
        max = $(val).data('max');
        min_type = $(val).data('min-type');
        max_type = $(val).data('max-type');
        if (min_type == 'lte') {min_type_char = ">="} else {min_type_char = ">"};
        if (max_type == 'gte') {max_type_char = "<="} else {max_type_char = "<"};

        if (value == "" || value == null){
            $(tabselects[i]).parents(".input-group").addClass("has-error");
            $(tabselects[i]).parents(".input-group").find('.help-block').remove()
            $(tabselects[i]).parents(".input-group").append('<span id="helpBlock-' + id + '" class="help-block">Please provide a value !</span>');
            err = true;
        }else {
            $(tabselects[i]).parents(".input-group").find('.help-block').remove()
            check_mm = check_min_max(parseFloat(value), parseFloat(min), parseFloat(max), min_type, max_type)
            if (check_mm == -1) {
                $(tabselects[i]).parents(".input-group").addClass("has-error");
                $(tabselects[i]).parents(".input-group").append('<span id="helpBlock-' + id + '" class="help-block">Enter a value ' + min_type_char + ' ' + min + '</span>');
                err = true;
            }else if (check_mm == 1) {
                $(tabselects[i]).parents(".input-group").addClass("has-error");
                $(tabselects[i]).parents(".input-group").append('<span id="helpBlock-' + id + '" class="help-block">Enter a value ' + max_type_char + ' ' + max + '</span>');
                err = true;
            }else if (check_mm == 0) {
                $(tabselects[i]).parents(".input-group").removeClass("has-error")
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
    };
    if (err) {return;}

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
                    add_notification('form boolean true write task failed',3);
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
                    add_notification('form boolean false write task failed',3);
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
                    add_notification('form write task failed',3);
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
                        add_notification('form dropdown write property failed',3);
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
                    add_notification('form dropdown write task failed',3);
                    alert("Form Set NOK selects "+data+" - key "+key+" - value "+value+" - item_type "+item_type + " - name "+var_name)
                }
            });
        };
    };
});

$('input.write-task-btn').click(function(){
        key = $(this).data('key');
        id = $(this).attr('id');
        item_type = $(this).data('type');
        $('#'+id).removeClass('update-able');
        $(".variable-config[data-refresh-requested-timestamp][data-key=" + key + "][data-type=" + item_type + "]").attr('data-refresh-requested-timestamp', SERVER_TIME)
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
                    add_notification('boolean true write task failed',3);
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
                    add_notification('boolean false write task failed',3);
                }
            });
        }
});

function set_chart_selection_mode(){
    var mode = "";
    $.each($('.xy-chart-container'),function(key,val){
        // get identifier of the chart
        id = val.id.substring(19);
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

// fix drop down problem
$( document ).ready(function() {
    // Activate tooltips
    $('[data-toggle*="tooltip"]').tooltip()

    // Setup drop down menu
    $('.dropdown-toggle').dropdown();

    // Fix input element click problem
    $('.dropdown input, .dropdown label, .dropdown button').click(function(e) {
        e.stopPropagation();
    });
    // init
    $.each($('.chart-container'),function(key,val){
        // get identifier of the chart
        id = val.id.substring(16);
        if ($(val).data('yaxis').plotpoints == 'True') {plotPoints = true} else {plotPoints = false}
        if ($(val).data('yaxis').plotlines == 'True') {plotLines = true} else {plotLines = false}
        if ($(val).data('yaxis').steplines == 'True') {lineSteps = true} else {lineSteps = false}
        if ($(val).data('yaxis').uniquescale == 'True') {yaxisUniqueScale = true} else {yaxisUniqueScale = false}
        // add a new Plot
        PyScadaPlots.push(new PyScadaPlot(id, plotPoints, plotLines, lineSteps, yaxisUniqueScale));
    });
    $.each($('.xy-chart-container'),function(key,val){
        // get identifier of the chart
        id = val.id.substring(19);
        label = $(val).data('axes0Yaxis').label;
        xaxisVarId = $(val).data('xaxis').id;
        if ($(val).data('xaxis').linlog == 'True') {xaxisLinLog = true} else {xaxisLinLog = false}
        if ($(val).data('yaxis').plotpoints == 'True') {plotPoints = true} else {plotPoints = false}
        if ($(val).data('yaxis').plotlines == 'True') {plotLines = true} else {plotLines = false}
        if ($(val).data('yaxis').steplines == 'True') {lineSteps = true} else {lineSteps = false}
        if ($(val).data('yaxis').uniquescale == 'True') {yaxisUniqueScale = true} else {yaxisUniqueScale = false}
        CHART_VARIABLE_KEYS[xaxisVarId]=0;
        X_AXIS = xaxisVarId;
        // add a new XYPlot
        PyScadaPlots.push(new XYPlot(id, xaxisVarId, xaxisLinLog, plotPoints, plotLines, lineSteps, yaxisUniqueScale));
    });
    $.each($('.pie-container'),function(key,val){
        // get identifier of the chart
        id = val.id.substring(16);
        // add a new Plot
        PyScadaPlots.push(new Pie(id));
    });

    $.each($('.variable-config'),function(key,val){
        key = parseInt($(val).data('key'));
        init_type = parseInt($(val).data('init-type'));
        item_type = $(val).data('type');
        if(item_type == '' || typeof(item_type) == 'undefined'){
            item_type = "variable";
        }

        if( VARIABLE_PROPERTY_KEYS.indexOf(key)==-1 && item_type === "variable_property"){
            VARIABLE_PROPERTY_KEYS.push(key)
        }else if (VARIABLE_KEYS.indexOf(key)==-1 && item_type === "variable"){
            VARIABLE_KEYS.push(key)
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


    $('.activate_zoom_x').change(function() {
        set_chart_selection_mode();
    });
    $('.activate_zoom_y').change(function() {
        set_chart_selection_mode();
    });

    setTimeout(function() {data_handler()}, 5000);
    set_chart_selection_mode();
    $(window).on('hashchange', function() {
        if (window.location.hash.substr(1) !== '') {
            if ($("#" + window.location.hash.substr(1) + " .has_chart").length) {
                $("#show_timeline").removeClass("hidden");
            }else {
                $("#show_timeline").addClass("hidden");
            }
        }
    })
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
    $('#ReadAllTask').click(function(e) {
      $.ajax({
          url: ROOT_URL+'form/read_all_task/',
          type: "POST",
          data:{},
          success: function (data) {
            items = {}
            $.each($('.hidden.variable-config'), function(k,v) {
              items[v.attributes['data-type']['value'] + "-" + v.attributes['data-key']['value']] = {'type' : v.attributes['data-type']['value'], 'key' : v.attributes['data-key']['value']};
              if (typeof($(v).attr('data-refresh-requested-timestamp')) !== 'undefined') {
                $(v).attr('data-refresh-requested-timestamp',SERVER_TIME);
              };
            });
            $.each(items, function(k,v) {
              refresh_logo(v['key'], v['type'])
            });
          },
          error: function(x, t, m) {
              add_notification('Reauest all data failed', 1)
          },
        });
    });
    // auto update function
    $('#AutoUpdateButton').click(function(e) {
        auto_update_click();
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
    // show timeline init
    if (window.location.hash.substr(1) !== '') {
        if ($("#" + window.location.hash.substr(1) + " .has_chart").length) {
            $("#show_timeline").removeClass("hidden");
        } else {
            $("#show_timeline").addClass("hidden");
        };
    }


    // DateTime Picker
    $('#datetimepicker_from').datetimepicker({
        sideBySide: true,
        locale: 'fr',
        format: 'L LTS',
        allowInputToggle: true,
        disable: true,
    });
    $('#datetimepicker_to').datetimepicker({
        sideBySide: true,
        locale: 'fr',
        format: 'L LTS',
        useCurrent: false,
        allowInputToggle: true,
        disable: true,
        widgetPositioning: {horizontal: 'right'},
        widgetParent: $('#timeline'),
    });
    $("#datetimepicker_from").on("change.datetimepicker", function (e) {
        $('#datetimepicker_to').datetimepicker('minDate', e.date);
    }).focusout(function (e) {
        DATA_INIT_STATUS++;
        DATA_FROM_TIMESTAMP = $('#datetimepicker_from').datetimepicker('viewDate').unix() * 1000;
        DATA_BUFFER_SIZE = DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP;
        INIT_CHART_VARIABLES_DONE = false;
        SINGLE_UPDATE = true;
        if($('#AutoUpdateButton').hasClass('glyphicon-play') && PREVIOUS_AUTO_UPDATE_ACTIVE_STATE){
            auto_update_click();
        };
    }).click(function (e) {
        if (!$('#datetimepicker_from .bootstrap-datetimepicker-widget').length) {
            $('#datetimepicker_from').datetimepicker('show');
        };
    });
    $("#datetimepicker_from .datetimepicker-input").focusin(function (e) {
        PREVIOUS_AUTO_UPDATE_ACTIVE_STATE = AUTO_UPDATE_ACTIVE
        if($('#AutoUpdateButton').hasClass('glyphicon-pause') && AUTO_UPDATE_ACTIVE){
            auto_update_click();
        };
    });

    $("#datetimepicker_to").on("change.datetimepicker", function (e) {
        $('#datetimepicker_from').datetimepicker('maxDate', e.date);
        PREVIOUS_AUTO_UPDATE_ACTIVE_STATE = false;
    }).focusout(function (e) {
        DATA_INIT_STATUS++;
        DATA_TO_TIMESTAMP = Math.min($('#datetimepicker_to').datetimepicker('viewDate').unix() * 1000, SERVER_TIME);
        DATA_BUFFER_SIZE = DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP;
        INIT_CHART_VARIABLES_DONE = false;
        SINGLE_UPDATE = true;
        if($('#AutoUpdateButton').hasClass('glyphicon-play') && PREVIOUS_AUTO_UPDATE_ACTIVE_STATE){
            auto_update_click();
        };
    }).click(function (e) {
        //$('#datetimepicker_to').datetimepicker('maxDate', new Date(SERVER_TIME));
        if (!$('#datetimepicker_to .bootstrap-datetimepicker-widget').length) {
            $('#datetimepicker_to').datetimepicker('show');
        };
    });
    $("#datetimepicker_to .datetimepicker-input").focusin(function (e) {
        PREVIOUS_AUTO_UPDATE_ACTIVE_STATE = AUTO_UPDATE_ACTIVE
        if($('#AutoUpdateButton').hasClass('glyphicon-pause') && AUTO_UPDATE_ACTIVE){
            auto_update_click();
        };
    });

    // Resize charts on windows resize
    $(window).resize(function() {
      $.each(PyScadaPlots,function(plot_id){
            var self = this, doBind = function() {
                PyScadaPlots[plot_id].resize();
            };
            $.browserQueue.add(doBind, this);
        });
    });

    // Prevent closing dropdown on click
    $('.dropdown-menu').click(function(e) {
        e.stopPropagation();
    });
});
