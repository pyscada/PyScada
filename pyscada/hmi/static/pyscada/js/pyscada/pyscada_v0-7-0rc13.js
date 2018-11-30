/* Javascript library for the PyScada web client based on jquery and flot,

version 0.7.0rc13

Copyright (c) 2013-2018 Martin Schröder
Licensed under the GPL.

*/
var version = "0.7.0rc10"
var NOTIFICATION_COUNT = 0
var UPDATE_STATUS_COUNT = 0;
var INIT_STATUS_COUNT = 0;
var PyScadaPlots = [];
var DATA_OUT_OF_DATE = false;
var DATA_OUT_OF_DATE_ALERT_ID = '';
var JSON_ERROR_COUNT = 0;
var AUTO_UPDATE_ACTIVE = true;
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
                    DATA_FROM_TIMESTAMP = value[0][0];
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
                    } else if (v_t_max > d_t_min && v_t_min < d_t_min){
                        // data and value overlapping, value has older elements then data, prepend
                        stop_id = find_index_sub_lte(value,DATA[key][0][0],0);
                        if (typeof(stop_id) === "number" ){
                            DATA[key] = value.slice(0,stop_id).concat(DATA[key]);
                        }else{
                            console.log(key + ' : dropped data');
                        }
                    } else if (v_t_max > d_t_max && d_t_min < v_t_min){
                        // data and value overlapping, data has older elements then value, append
                        stop_id = find_index_sub_gte(value,DATA[key][DATA[key].length-1][0],0);
                        if (typeof(stop_id) === "number" ){
                            DATA[key] = DATA[key].concat(value.slice(stop_id));
                        }else{
                            console.log(key + ' : dropped data');
                        }
                    } else{
                        console.log(key + ' : dropped data');
                    }
                }
                if (value[0][0] < DATA_FROM_TIMESTAMP){
                    DATA_FROM_TIMESTAMP = value[0][0];
                    UPDATE_X_AXES_TIME_LINE_STATUS = true;
                }
            }
        }else{
            console.log(key + ' : value.length==0')
        }
    }
}


function data_handler(){
    // call the data handler periodically
    if(!INIT_STATUS_VARIABLES_DONE || !INIT_CHART_VARIABLES_DONE){
        // initialisation is active
        setTimeout(function() {data_handler();}, REFRESH_RATE/2.0);
    }else{
        setTimeout(function() {data_handler();}, REFRESH_RATE);
    }

    if(AUTO_UPDATE_ACTIVE){
        if(DATA_TO_TIMESTAMP==0){
        // fetch the SERVER_TIME
            data_handler_ajax(0,[],[],Date.now());
        }else{
            if(FETCH_DATA_PENDING<=0){
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
                        if(var_count >= 5){break;}
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
                    var timestamp = DATA_FROM_TIMESTAMP;
                    for (var key in CHART_VARIABLE_KEYS){
                       if(CHART_VARIABLE_KEYS[key]<=DATA_INIT_STATUS){
                            CHART_VARIABLE_KEYS[key]++;
                            var_count++;
                            INIT_CHART_VARIABLES_COUNT++;
                            vars.push(key);
                            if (typeof(DATA[key]) == 'object'){
                                timestamp = Math.max(timestamp,DATA[key][0][0])
                            }
                            if(var_count >= 10){break;}
                       }
                    }
                    if(var_count>0){
                        if (timestamp === DATA_FROM_TIMESTAMP){
                            timestamp = DATA_DISPLAY_TO_TIMESTAMP;
                        }
                        data_handler_ajax(1,vars,props,timestamp-120*60*1000,timestamp);
                    }else{
                        INIT_CHART_VARIABLES_DONE = true;
                        $('#PlusTwoHoursButton').removeClass("disabled");
                    }
                }
            }
        }
    }
}

function data_handler_ajax(init,variable_keys,variable_property_keys,timestamp_from,timestamp_to){
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
        DATA_TO_TIMESTAMP = DATA_FROM_TIMESTAMP = SERVER_TIME;
    }else{
        $.each(fetched_data, function(key, val) {
            add_fetched_data(parseInt(key),val);
        });
        if (DATA_TO_TIMESTAMP < timestamp){
            DATA_TO_TIMESTAMP = timestamp;
            if ((DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP)> DATA_BUFFER_SIZE){
                DATA_FROM_TIMESTAMP = DATA_TO_TIMESTAMP - DATA_BUFFER_SIZE;
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
                PyScadaPlots[plot_id].update();
            };
            $.browserQueue.add(doBind, this);
        });
        for (var key in VARIABLE_KEYS) {
            key = VARIABLE_KEYS[key];
            if (typeof(DATA[key]) == 'object'){
                update_data_values('var-' + key,DATA[key][DATA[key].length-1][1]);
            }
        }
        for (var key in VARIABLE_PROPERTIES_DATA) {
            value = VARIABLE_PROPERTIES_DATA[key];
            update_data_values('prop-' + key,value);
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
    $("#AutoUpdateButton").removeClass("btn-warning");
    $("#AutoUpdateButton").addClass("btn-success");
    if (JSON_ERROR_COUNT > 0) {
        JSON_ERROR_COUNT = JSON_ERROR_COUNT - 1;
    }
    hide_update_status();
    if(request_data.init===1){
        hide_init_status();
    }
    FETCH_DATA_PENDING--;
}

function data_handler_fail(x, t, m) {
    if(JSON_ERROR_COUNT % 5 == 0)
        add_notification(t, 3);

    JSON_ERROR_COUNT = JSON_ERROR_COUNT + 1;
    if (JSON_ERROR_COUNT > 60) {
        AUTO_UPDATE_ACTIVE = false;
        add_notification("error limit reached", 3);
    } else if(JSON_ERROR_COUNT > 3){
        for (var key in VARIABLE_KEYS) {
            key = VARIABLE_KEYS[key];
            add_fetched_data(key, [[DATA_TO_TIMESTAMP,Number.NaN]]);
        }
    }
    hide_update_status();
    $("#AutoUpdateButton").removeClass("btn-success");
    $("#AutoUpdateButton").addClass("btn-warning");
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
        message_pre = '<strong>Emergency!</strong> ';
    } else if (level === 2) {
        level = 'danger';
        message_pre = '<strong>Critical!</strong> ';
    } else if (level === 3) {
        level = 'danger';
        message_pre = '<strong>Error!</strong> ';
    } else if (level === 4) {
        level = 'danger';
        message_pre = '<strong>Alert!</strong> ';
    } else if (level === 5) {
        level = 'warning';
        message_pre = '<strong>Warning!</strong> ';
    }else if (level === 6) {
        level = 'success';
        message_pre = '<strong>Notice</strong> ';
    }else if (level === 7) {
        level = 'info';
        message_pre = '<strong>Info</strong> ';
    }else if (level === 8) {
        level = 'success';
        message_pre = '<strong>Notice</strong> ';
    }else if (level === 9) {
        level = 'info';
        message_pre = '<strong>Info</strong> ';
    }
    if(clearable){
        $('#notification_area').append('<div id="notification_Nb' + NOTIFICATION_COUNT + '" class="notification alert alert-' + level + ' alert-dismissable" style="position: fixed; top: ' + top + 'px; right: ' + right + 'px; "><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>'+message_pre+ new Date().toLocaleTimeString() + ': ' + message + '</div>');
    }else{
        $('#notification_area_2').append('<div id="notification_Nb' + NOTIFICATION_COUNT + '" class="notification alert alert-' + level + '" >'+message_pre+ new Date().toLocaleTimeString() + ': ' + message + '</div>');
    }
    if (timeout){
        setTimeout('$("#notification_Nb' + NOTIFICATION_COUNT + '").alert("close");', 7000);
    }else{
        id = 'notification_Nb' + NOTIFICATION_COUNT;
        NOTIFICATION_COUNT = NOTIFICATION_COUNT + 1;
        return id;
    }
    NOTIFICATION_COUNT = NOTIFICATION_COUNT + 1;
}

function update_data_values(key,val){
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
            $(".type-numeric." + key).html(r_val);
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
                
                $('button.btn-default.write-task-btn.' + key).addClass("update-able");
                $('button.update-able.write-task-btn.' + key).addClass("btn-default");
                $('button.update-able.write-task-btn.' + key).removeClass("btn-success");
                $(".type-numeric." + key).html(0);
                $('input.'+ key).attr("placeholder",0);
            } else {
                $(".label.type-bool." + key).removeClass("label-default");
                $(".label.type-bool." + key).removeClass("label-danger");
                $(".label.type-bool.status-blue." + key).addClass("label-primary");
                $(".label.type-bool.status-info." + key).addClass("label-info");
                $(".label.type-bool.status-green." + key).addClass("label-success");
                $(".label.type-bool.status-yello." + key).addClass("label-warning");
                $(".label.type-bool.status-red." + key).addClass("label-danger");
                $(".label.type-bool.status-red-inv." + key).addClass("label-default");
                $('button.btn-success.write-task-btn.' + key).addClass("update-able");
                $('button.update-able.write-task-btn.' + key).removeClass("btn-default");
                $('button.update-able.write-task-btn.' + key).addClass("btn-success");
                $(".type-numeric." + key).html(1);
                $('input.'+ key).attr("placeholder",1);
            }
        }
}

function set_x_axes(){
    if(!progressbar_resize_active){
        $.each(PyScadaPlots,function(plot_id){
            PyScadaPlots[plot_id].update();
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
        $("#timeline-time-to-label").html(date.toLocaleTimeString());
    }
    var min_full = ((DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP)/60/1000);
    if (DATA_DISPLAY_FROM_TIMESTAMP < 0 ){
        var min_from = Math.min(min_full,((DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP)/60/1000));
        $('#timeline-time-from-label').html("");
    }else{
        var min_from = Math.min(min_full,((DATA_TO_TIMESTAMP - DATA_DISPLAY_FROM_TIMESTAMP)/60/1000));
        //$('#timeline-time-from-label').html("-" + min_from.toPrecision(3) + "min");
        var date = new Date(DATA_DISPLAY_FROM_TIMESTAMP);
        $("#timeline-time-from-label").html(date.toLocaleTimeString());
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
    $("#timeline-time-left-label").html(date.toLocaleTimeString());
}

function progressbarSetWindow( event, ui ) {
    $.each(PyScadaPlots,function(plot_id){
            PyScadaPlots[plot_id].update();
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
function PyScadaPlot(id){
<<<<<<< HEAD:pyscada/hmi/static/pyscada/js/pyscada/pyscada.js
=======
    
>>>>>>> remotes/upstream/hmi:pyscada/hmi/static/pyscada/js/pyscada/pyscada_v0-7-0rc13.js
    var options = {
        xaxis: {
            mode: "time",
            ticks: $('#chart-container-'+id).data('xaxisTicks'),
            timeformat: "%H:%M:%S",
            timezone:"browser"
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
            }
        },
        lines: {
            steps:true
            }
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
    variables = {},
    plot = this;
    
    
    // public functions
    plot.update 			= update;
    plot.prepare 			= prepare;
    plot.getSeries 			= function () { return series };
    plot.getFlotObject		= function () { return flotPlot};
    plot.getKeys			= function (){ return keys};
    plot.getVariableNames	= function (){ return variable_names};

    plot.getInitStatus		= function () { if(InitDone){return InitRetry}else{return false}};
    plot.getId				= function () {return id};
    // init data
    $.each($(legend_table_id + ' .variable-config'),function(key,val){
        val_inst = $(val);
        variable_name = val_inst.data('name');
        variable_key = val_inst.data('key');
        variables[variable_key] = {'color':val_inst.data('color'),'yaxis':1}
        keys.push(variable_key);
        variable_names.push(variable_name);
    });
    
    
    function prepare(){
        // prepare legend table sorter
        $(legend_table_id).tablesorter({sortList: [[2,0]]});
        
        // add onchange function to every checkbox in legend
        $.each(variables,function(key,val){
            $(legend_checkbox_id+key).change(function() {
                plot.update();
                if ($(legend_checkbox_id+key).is(':checked')){
                    $(legend_checkbox_status_id+key).html(1);
                }else{
                    $(legend_checkbox_status_id+key).html(0);
                }
            });
        });
        //
        $(legend_checkbox_id+'make_all_none').change(function() {
                //console.log(legend_checkbox_id + 'changed');
                plot.update();
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
         });
        // expand the chart to the maximum width
        main_chart_area  = $(chart_container_id).closest('.main-chart-area');
        
        
        contentAreaHeight = main_chart_area.parent().height();
        mainChartAreaHeight = main_chart_area.height();
        
        if (contentAreaHeight>mainChartAreaHeight){
            main_chart_area.height(contentAreaHeight);
        }

        //
        flotPlot = $.plot($(chart_container_id + ' .chart-placeholder'), series, options);
        set_chart_selection_mode();
        // update the plot
        update();
        // bind 
        $(chart_container_id + ' .chart-placeholder').bind("plotselected", function(event, ranges) {
            pOpt = flotPlot.getOptions();

            if ($(chart_container_id + " .activate_zoom_y").is(':checked')) {
                for (range in ranges) {
                    if (~range.indexOf('y')) {
                        if (range.match(/\d+/) != null) {
                            y_number = range.match(/\d+/)[0];
                            pOpt.yaxes[y_number-1].min = ranges[range].from;
                            pOpt.yaxes[y_number-1].max = ranges[range].to;

                        }else {
                            pOpt.yaxes[0].min = ranges[range].from;
                            pOpt.yaxes[0].max = ranges[range].to;
                        }
                    }
                }
                flotPlot.setupGrid();
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
        var yaxisLabel = $(chart_container_id + ' .axisLabel.yaxisLabel');
        yaxisLabel.css("margin-top", yaxisLabel.width() / 2 - 20);
        
        
        $(chart_container_id + " .btn.btn-default.chart-ResetSelection").click(function() {
            DATA_DISPLAY_FROM_TIMESTAMP = -1;
            DATA_DISPLAY_TO_TIMESTAMP = -1;
            DATA_DISPLAY_WINDOW = DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP
            set_x_axes();
            pOpt = flotPlot.getOptions();
            aOpt = flotPlot.getYAxes();
            pOpt.yaxes[0].min = aOpt.datamin;
            pOpt.yaxes[0].max = aOpt.datamax;
            flotPlot.setupGrid();
            flotPlot.draw();
        });
        
        $(chart_container_id + " .btn.btn-default.chart-ZoomYToFit").click(function() {
            pOpt = flotPlot.getOptions();
            aOpt = flotPlot.getYAxes();
            pOpt.yaxes[0].min = aOpt.datamin;
            pOpt.yaxes[0].max = aOpt.datamax;
            flotPlot.setupGrid();
            flotPlot.draw();
        });
        $(chart_container_id + " .btn.btn-default.chart-ZoomXToFit").click(function() {
            DATA_DISPLAY_FROM_TIMESTAMP = -1;
            DATA_DISPLAY_TO_TIMESTAMP = -1;
            DATA_DISPLAY_WINDOW = DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP
            set_x_axes();
        });
    }


    function update(){
        if(!prepared ){
            if($(chart_container_id).is(":visible")){
                prepared = true;
                prepare();
            }else{
                return;
            }
        }
        if($(chart_container_id).is(":visible")){
            // only update if plot is visible
            // add the selected data series to the "series" variable
            series = [];
            start_id = 0;
            for (var key in keys){
                key = keys[key];
                if($(legend_checkbox_id+key).is(':checked') && typeof(DATA[key]) === 'object'){
                    if (DATA_DISPLAY_TO_TIMESTAMP > 0 && DATA_DISPLAY_FROM_TIMESTAMP > 0){
                        start_id = find_index_sub_lte(DATA[key],DATA_DISPLAY_FROM_TIMESTAMP,0);
                        stop_id = find_index_sub_lte(DATA[key],DATA_DISPLAY_TO_TIMESTAMP,0);
                        chart_data = DATA[key].slice(start_id,stop_id+1);
                    }else if (DATA_DISPLAY_FROM_TIMESTAMP > 0 && DATA_DISPLAY_TO_TIMESTAMP < 0){
                        start_id = find_index_sub_lte(DATA[key],DATA_DISPLAY_FROM_TIMESTAMP,0);
                        chart_data = DATA[key].slice(start_id);
                    }else if (DATA_DISPLAY_FROM_TIMESTAMP < 0 && DATA_DISPLAY_TO_TIMESTAMP > 0){
                        if (DATA_DISPLAY_TO_TIMESTAMP < DATA[key][0][0]){continue;}
                        stop_id = find_index_sub_lte(DATA[key],DATA_DISPLAY_TO_TIMESTAMP,0);
                        chart_data = DATA[key].slice(0,stop_id+1);
                    }else {
                        chart_data = DATA[key].slice();
                    }
                    // add data for step display
                    /*
                    if (chart_data.length > 2){
                        i = 1;
                        while (i < chart_data.length) {
                             if (chart_data[i][0] - chart_data[i - 1][0] > 1000.0 && chart_data[i][1] != chart_data[i - 1][1]){
                                chart_data.splice(i,0, [chart_data[i][0], chart_data[i - 1][1]]);
                                i += 2;
                            }else{
                                i += 1;
                            }
                        }
                    }
                    */
                    // append last value
                    if (chart_data.length >= 1){
                        if (DATA_DISPLAY_TO_TIMESTAMP < 0){
                            chart_data.push([DATA_TO_TIMESTAMP,chart_data[chart_data.length-1][1]]);
                        }else{
                            chart_data.push([DATA_DISPLAY_TO_TIMESTAMP,chart_data[chart_data.length-1][1]]);
                        }
                    }

                    series.push({"data":chart_data,"color":variables[key].color,"yaxis":variables[key].yaxis});
                }
            }
            // update flot plot
            flotPlot.setData(series);
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

            flotPlot.setupGrid();
            flotPlot.draw();
        }
    }
}

function XYPlot(id, xaxisVarId, xaxisLinLog, plotPoints, yaxisUniqueScale){
    var options = {
        yaxes: [],
        xaxis: {
            ticks: 5,
            mode: null
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
            //to show points informations
            hoverable: true,
            clickable: true
        },
        lines: { show: true },
        points: { show: plotPoints }
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
    variables = {},
    plot = this;


    // public functions
    plot.update 			= update;
    plot.prepare 			= prepare;
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
                label = val_inst.find(".legendLabel").text();
                unit = val_inst.find(".legendUnit").text();
            }
        });
        if (options.yaxes[k-1] == null) {
            options.yaxes[k-1] = {};
        };
        if(k%2){pos="left";}else{pos="right";};
        tf = function (value, axis) {
            return value.toFixed(axis.tickDecimals) + axis.options.unit;
        };
        if (unit != "") {
            lb = label.replace(/\s/g, '') + "(" + unit + ")";
        }else{
            lb = label.replace(/\s/g, '');
        }
        options.yaxes[k-1].position = pos;
        options.yaxes[k-1].tickFormatter = tf;
        if (yaxisUniqueScale == false) {
            options.yaxes[k-1].axisLabel = lb;
            //options.yaxes[k-1].axisLabelUseCanvas = true;
            options.yaxes[k-1].axisLabelFontSizePixels = 12;
            options.yaxes[k-1].axisLabelFontFamily = 'Verdana, Arial';
            options.yaxes[k-1].axisLabelPadding = 3;
            options.yaxes[k-1].axisLabelColour = variables[variable_key]['color'];
        }
        options.yaxes[k-1].unit = unit;
        options.yaxes[k-1].labelWidth = null;
        options.yaxes[k-1].reserveSpace = true;
        k += 1;
    });


    function prepare(){
        // prepare legend table sorter
        $(legend_table_id).tablesorter({sortList: [[2,0]]});

        // add onchange function to every checkbox in legend
        $.each(variables,function(key,val){
            $(legend_checkbox_id+key).change(function() {
                plot.update();
                if ($(legend_checkbox_id+key).is(':checked')){
                    $(legend_checkbox_status_id+key).html(1);
                }else{
                    $(legend_checkbox_status_id+key).html(0);
                }
            });
        });
        //
        $(legend_checkbox_id+'make_all_none').change(function() {
                //console.log(legend_checkbox_id + 'changed');
                plot.update();
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
        update();

        //add info on mouse over a point and position of the mouse
        //add <span id="hoverdata"></span> to the html code to see the position of the mouse
        $("<div id='tooltip'></div>").css({
            position: "absolute",
            display: "none",
            border: "1px solid #fdd",
            padding: "2px",
            "background-color": "#fee",
            opacity: 0.80
	    }).appendTo("body");

        $(chart_container_id + ' .chart-placeholder').bind("plothover", function (event, pos, item) {
            if (pos.x) {
                    var str = "(" + pos.x.toFixed(0) + ", " + pos.y.toFixed(2) + ")";
                }
            $("#hoverdata").text(str);
            if (item) {
                var x = item.datapoint[0].toFixed(0),
                    y = item.datapoint[1].toFixed(2);
                $("#tooltip").html(item.series.label + "(" + x + ") = " + y)
                    .css({top: item.pageY+5, left: item.pageX+5})
                    .fadeIn(200);
            } else {
                $("#tooltip").hide();
            }
        });
        $(chart_container_id + ' .chart-placeholder').bind("plotclick", function (event, pos, item) {
			if (item) {
			    var x = item.datapoint[0].toFixed(0),
                    y = item.datapoint[1].toFixed(2);
				$("#clickdata").text(" - click point " + item.dataIndex + " in " + item.series.label +
				" - (x,y) = (" + x + ", " + y + ")");
				//TODO highlight the point and remove on nextclick
				//plot.highlight(item.series, item.datapoint);
			}
		});

        // bind
        $(chart_container_id + ' .chart-placeholder').bind("plotselected", function(event, ranges) {
            pOpt = flotPlot.getOptions();
            if ($(chart_container_id + " .activate_zoom_y").is(':checked')) {
                for (range in ranges) {
                    if (~range.indexOf('y')) {
                        if (range.match(/\d+/) != null) {
                            y_number = range.match(/\d+/)[0];
                            pOpt.yaxes[y_number-1].min = ranges[range].from;
                            pOpt.yaxes[y_number-1].max = ranges[range].to;
                        }else {
                            pOpt.yaxes[0].min = ranges[range].from;
                            pOpt.yaxes[0].max = ranges[range].to;
                        }
                    }
                }
                flotPlot.setupGrid();
                flotPlot.draw();
            }
            pOpt = flotPlot.getOptions();
            if ($(chart_container_id + " .activate_zoom_x").is(':checked') && ranges.xaxis != null) {
                pData = flotPlot.getData();
                tmin=0;
                tmax=0;
                for (x in pData[0].xdata) {
                    if (pData[0].xdata[x][1] >= ranges.xaxis.from && tmin == 0) {
                        tmin = pData[0].xdata[x][0] - 1000;
                    }
                    if (pData[0].xdata[x][1] >= ranges.xaxis.to && tmax == 0) {
                        tmax = pData[0].xdata[x][0] + 1000;
                    }
                }
                DATA_DISPLAY_TO_TIMESTAMP = tmax;
                DATA_DISPLAY_FROM_TIMESTAMP = tmin;
                DATA_DISPLAY_WINDOW = DATA_DISPLAY_TO_TIMESTAMP-DATA_DISPLAY_FROM_TIMESTAMP;
                pOpt.xaxes[0].min = ranges.xaxis.from;
                pOpt.xaxes[0].max = ranges.xaxis.to;
                flotPlot.setupGrid();
                flotPlot.draw();
            }
            flotPlot.clearSelection();
        });

        // Since CSS transforms use the top-left corner of the label as the transform origin,
        // we need to center the y-axis label by shifting it down by half its width.
        // Subtract 20 to factor the chart's bottom margin into the centering.
        var chartTitle = $(chart_container_id + ' .chartTitle');
        chartTitle.css("margin-left", -chartTitle.width() / 2);
        var yaxisLabel = $(chart_container_id + ' .axisLabel.yaxisLabel');
        yaxisLabel.css("margin-top", yaxisLabel.width() / 2 - 20);


        $(chart_container_id + " .btn.btn-default.chart-ResetSelection").click(function() {
            DATA_DISPLAY_FROM_TIMESTAMP = -1;
            DATA_DISPLAY_TO_TIMESTAMP = -1;
            DATA_DISPLAY_WINDOW = DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP
            set_x_axes();
            pOpt = flotPlot.getOptions();
            for (y in pOpt.yaxes){
                pOpt.yaxes[y].min = pOpt.yaxes[y].chart_data_min;
                pOpt.yaxes[y].max = pOpt.yaxes[y].chart_data_max;
            }
            pOpt.xaxes[0].min = pOpt.xaxes[0].x_data_min;
            pOpt.xaxes[0].max = pOpt.xaxes[0].x_data_max;
            flotPlot.setupGrid();
            flotPlot.draw();
        });

        $(chart_container_id + " .btn.btn-default.chart-ZoomYToFit").click(function() {
            pOpt = flotPlot.getOptions();
            for (y in pOpt.yaxes){
                pOpt.yaxes[y].min = pOpt.yaxes[y].chart_data_min;
                pOpt.yaxes[y].max = pOpt.yaxes[y].chart_data_max;
            }
            flotPlot.setupGrid();
            flotPlot.draw();
        });
        $(chart_container_id + " .btn.btn-default.chart-ZoomXToFit").click(function() {
            DATA_DISPLAY_FROM_TIMESTAMP = -1;
            DATA_DISPLAY_TO_TIMESTAMP = -1;
            DATA_DISPLAY_WINDOW = DATA_TO_TIMESTAMP - DATA_FROM_TIMESTAMP
            set_x_axes();
            pOpt = flotPlot.getOptions();
            pOpt.xaxes[0].min = pOpt.xaxes[0].x_data_min;
            pOpt.xaxes[0].max = pOpt.xaxes[0].x_data_max;
            flotPlot.setupGrid();
            flotPlot.draw();
        });
    }


    function update(){
        if(!prepared ){
            if($(chart_container_id).is(":visible")){
                prepared = true;
                prepare();
            }else{
                return;
            }
        }
        if($(chart_container_id).is(":visible")){
            // only update if plot is visible
            // add the selected data series to the "series" variable
            var series = [];
            start_id = 0;
            j=0;
            for (var key in keys){
                key = keys[key];
                xkey = xaxisVarId
                if($(legend_checkbox_id+key).is(':checked') && typeof(DATA[key]) === 'object'){
                    if (DATA_DISPLAY_TO_TIMESTAMP > 0 && DATA_DISPLAY_FROM_TIMESTAMP > 0){
                        start_id = find_index_sub_lte(DATA[key],DATA_DISPLAY_FROM_TIMESTAMP,0);
                        stop_id = find_index_sub_lte(DATA[key],DATA_DISPLAY_TO_TIMESTAMP,0);
                        chart_data = DATA[key].slice(start_id,stop_id+1);
                    }else if (DATA_DISPLAY_FROM_TIMESTAMP > 0 && DATA_DISPLAY_TO_TIMESTAMP < 0){
                        start_id = find_index_sub_lte(DATA[key],DATA_DISPLAY_FROM_TIMESTAMP,0);
                        chart_data = DATA[key].slice(start_id);
                    }else if (DATA_DISPLAY_FROM_TIMESTAMP < 0 && DATA_DISPLAY_TO_TIMESTAMP > 0){
                        if (DATA_DISPLAY_TO_TIMESTAMP < DATA[key][0][0]){continue;}
                        stop_id = find_index_sub_lte(DATA[key],DATA_DISPLAY_TO_TIMESTAMP,0);
                        chart_data = DATA[key].slice(0,stop_id+1);
                    }else {
                        chart_data = DATA[key].slice();
                    }
                    if (DATA_DISPLAY_TO_TIMESTAMP > 0 && DATA_DISPLAY_FROM_TIMESTAMP > 0){
                        start_fid = find_index_sub_lte(DATA[xkey],DATA_DISPLAY_FROM_TIMESTAMP,0);
                        stop_fid = find_index_sub_lte(DATA[xkey],DATA_DISPLAY_TO_TIMESTAMP,0);
                        chart_x_data = DATA[xkey].slice(start_fid,stop_fid+1);
                    }else if (DATA_DISPLAY_FROM_TIMESTAMP > 0 && DATA_DISPLAY_TO_TIMESTAMP < 0){
                        start_fid = find_index_sub_lte(DATA[xkey],DATA_DISPLAY_FROM_TIMESTAMP,0);
                        chart_x_data = DATA[xkey].slice(start_fid);
                    }else if (DATA_DISPLAY_FROM_TIMESTAMP < 0 && DATA_DISPLAY_TO_TIMESTAMP > 0){
                        if (DATA_DISPLAY_TO_TIMESTAMP < DATA[key][0][0]){continue;}
                        stop_fid = find_index_sub_lte(DATA[xkey],DATA_DISPLAY_TO_TIMESTAMP,0);
                        chart_x_data = DATA[xkey].slice(0,stop_fid+1);
                    }else {
                        chart_x_data = DATA[xkey].slice();
                    }
                    new_data=[];
                    if (chart_data.length > 0){
                        i = 0;
                        if (chart_x_data.length < chart_data.length){
                            console.log('X data smaller than Y data -> X : ' + chart_x_data + ' - Y : ' + chart_data);
                        }else {
                            chart_data_min = chart_data[0][1]
                            chart_data_max = chart_data[0][1]
                            x_data_min = chart_x_data[0][1]
                            x_data_max = chart_x_data[0][1]
                            while (i < chart_data.length) {
                                new_data.push([chart_x_data[i][1],chart_data[i][1]]);
                                chart_data_min = Math.min(chart_data_min, chart_data[i][1])
                                chart_data_max = Math.max(chart_data_max, chart_data[i][1])
                                x_data_min = Math.min(x_data_min, chart_x_data[i][1])
                                x_data_max = Math.max(x_data_max, chart_x_data[i][1])
                                i += 1;
                            }
                        }
                    }
                    $.each($(legend_table_id + ' .legendSeries'),function(kkey,val){
                        val_inst = $(val);
                        if (key == val_inst.find(".variable-config").data('key')){
                            label = val_inst.find(".legendLabel").text();
                            unit = val_inst.find(".legendUnit").text();
                        }
                    });
                    if (new_data.length > 0){
                        j += 1;
                        if (yaxisUniqueScale) {yj = 1} else {yj = j}
                        //plot Y with defferents axis
                        series.push({"data":new_data,"xdata":chart_x_data,"color":variables[key].color,"yaxis":yj,"label":label,"unit":unit,"chart_data_min":chart_data_min,"chart_data_max":chart_data_max,"x_data_min":x_data_min,"x_data_max":x_data_max});
                    }
                }
            }
            // update flot plot
            flotPlot.setData(series);

            //update y window
            pOpt = flotPlot.getOptions();
            if (j != 0){
                for (k = 1;k <= j;k++){
                    pOpt.yaxes[k-1].chart_data_min = series[k-1]['chart_data_min'];
                    pOpt.yaxes[k-1].chart_data_max = series[k-1]['chart_data_max'];
                }
            }

            // update x window
            //pOpt = flotPlot.getOptions();
            if (j != 0){
                var xticks=[];
                if (xaxisLinLog == "True"){
                    xticks=xticks.concat(chart_x_data[0][1]);
                    for (i=parseInt(Math.round(Math.log(chart_x_data[0][1])/Math.log(10)));i<=parseInt(Math.round(Math.log(chart_x_data[chart_x_data.length-1][1])/Math.log(10)));i++){
                        xticks=xticks.concat(Math.pow(10,i)/2);
                        xticks=xticks.concat(Math.pow(10,i));
                    xticks=xticks.concat(chart_x_data[chart_x_data.length-1][1]);
                    pOpt.xaxes[0].ticks = xticks;
                    pOpt.xaxes[0].transform = function (v) { return Math.log(v); };
                    pOpt.xaxes[0].inverseTransform = function (v) { return Math.exp(v); };
                    }
                }else {
                    pOpt.xaxes[0].ticks = Math.min(chart_x_data.length,11);
                }
                pOpt.xaxes[0].x_data_min = series[0]['x_data_min'];
                pOpt.xaxes[0].x_data_max = series[0]['x_data_max'];

                if (DATA_DISPLAY_TO_TIMESTAMP > 0 && DATA_DISPLAY_FROM_TIMESTAMP > 0){
                }else if (DATA_DISPLAY_FROM_TIMESTAMP > 0 && DATA_DISPLAY_TO_TIMESTAMP < 0){
                    pOpt.xaxes[0].max = series[0]['x_data_max'];
                }else if (DATA_DISPLAY_FROM_TIMESTAMP < 0 && DATA_DISPLAY_TO_TIMESTAMP > 0){
                    pOpt.xaxes[0].min = series[0]['x_data_min'];
                }else{
                    pOpt.xaxes[0].min = series[0]['x_data_min'];
                    pOpt.xaxes[0].max = series[0]['x_data_max'];
                }
            }
            flotPlot.setupGrid();
            flotPlot.draw();

            // Change the color of the axis
            if (j != 0 && yaxisUniqueScale == false){
                for (k = 1;k <= j;k++){
                    S = series[k-1]
                    if (S['unit'] != "") {
                        lb = S['label'].replace(/\s/g, '') + "(" + S['unit'] + ")";
                    }else{
                        lb = S['label'].replace(/\s/g, '');
                    }
                    if (k == 1){
                        $(chart_container_id + ' .axisLabels.yaxisLabel')[0].innerHTML = lb
                        $(chart_container_id + ' .axisLabels.yaxisLabel').css('color',S['color'])
                        $(chart_container_id + ' .flot-y' + k + '-axis').css('color',S['color'])
                    }else {
                        $(chart_container_id + ' .axisLabels.y' + k + 'axisLabel')[0].innerHTML = lb
                        $(chart_container_id + ' .axisLabels.y' + k + 'axisLabel').css('color',S['color'])
                        $(chart_container_id + ' .flot-y' + k + '-axis').css('color',S['color'])
                    }
                }
            }
        }
    }
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
    while(i++ < a.length){
        if (a[i][d]>=t){
            return i
        }
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


//form/write_task/

$('button.write-task-set').click(function(){
        key = $(this).data('key');
        id = $(this).attr('id');
        value = $("#"+id+"-value").val();
        item_type = $(this).data('type');
        if (value == "" ){
            add_notification('please provide a value',3);
            console.log('please provide a value');
        }else{
            $.ajax({
                type: 'post',
                url: ROOT_URL+'form/write_task/',
                data: {key:key, value:value, item_type:item_type},
                success: function (data) {
                    
                },
                error: function(data) {
                    add_notification('add new write task failed',3);
                    console.log("add new write task failed");
                }
            });
        };
});

$('button.write-task-form-set').click(function(){
        name_form = $(this.form).attr('name');
        tabinputs = document.forms[name_form].getElementsByTagName("input");
        DATA = {}; //reset the data after each button click
        DATA_DISPLAY_FROM_TIMESTAMP = -1;
        DATA_DISPLAY_TO_TIMESTAMP = -1;
        for (i=0;i<tabinputs.length;i++){ //test if there is an empty or non numeric value
            value = $(tabinputs[i]).val();
            if (value == "" || isNaN(value)){
                add_notification('please provide a value',3);
                alert("An input is empty or non numeric");
                return;
            };
        };

        for (i=0;i<tabinputs.length;i++){
            value = $(tabinputs[i]).val();
            var_name = $(tabinputs[i]).attr("name");
            $.each($('.variable-config'),function(kkey,val){
                name_var = $(val).data('name');
                if (name_var==var_name){
                    key = parseInt($(val).data('key'));
                    item_type = $(val).data('type');
                }
            });

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
                        add_notification('add new write task failed',3);
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
                        add_notification('add new write task failed',3);
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
                        add_notification('add new write task failed',3);
                        alert("Form Set NOK "+data+" - key "+key+" - value "+value+" - item_type "+item_type + " - name "+var_name)
                    }
                });
            };
        };
});

$('input.write-task-btn').click(function(){
        id = $(this).attr('id');
        $('#'+id).removeClass('update-able');
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
                    add_notification('add new write task failed',3);
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
                    add_notification('add new write task failed',3);
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
        // add a new Plot
        PyScadaPlots.push(new PyScadaPlot(id));
    });
    $.each($('.xy-chart-container'),function(key,val){
        // get identifier of the chart
        id = val.id.substring(19);
        label = $(val).data('axes0Yaxis').label;
        xaxisVarId = $(val).data('xaxis').id;
        xaxisLinLog = $(val).data('xaxis').linlog;
        if ($(val).data('yaxis').plotpoints == 'True') {plotPoints = true} else {plotPoints = false}
        if ($(val).data('yaxis').uniquescale == 'True') {yaxisUniqueScale = true} else {yaxisUniqueScale = false}
        CHART_VARIABLE_KEYS[xaxisVarId]=1;
        X_AXIS = xaxisVarId;
        // add a new Plot
        PyScadaPlots.push(new XYPlot(id, xaxisVarId, xaxisLinLog, plotPoints, yaxisUniqueScale));
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
            if ($("#" + window.location.hash.substr(1) + " .has_chart").length && $('#ShowTimelineButton').hasClass("btn-success")) {
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
        stop: function( event, ui ) {progressbar_resize_active = false;},
    });
    // auto update function
    $('#AutoUpdateButton').click(function(e) {
        if (AUTO_UPDATE_ACTIVE) {
            // deactivate auto update
            AUTO_UPDATE_ACTIVE = false;
            $("#AutoUpdateButton").addClass("btn-default");
            $("#AutoUpdateButton").removeClass("btn-success");
        } else {
            // activate auto update
            AUTO_UPDATE_ACTIVE = true;
            $("#AutoUpdateButton").addClass("btn-success");
            $("#AutoUpdateButton").removeClass("btn-default");
            JsonErrorCount = 0;
            data_handler();
        }
    });
    $('#PlusTwoHoursButton').click(function(e) {
	if (INIT_CHART_VARIABLES_DONE){
		$('#PlusTwoHoursButton').addClass("disabled");
		DATA_INIT_STATUS++;
		DATA_BUFFER_SIZE = DATA_BUFFER_SIZE + 120*60*1000;
		INIT_CHART_VARIABLES_DONE = false;
	}
    });
    // show timeline init
    if (window.location.hash.substr(1) !== '') {
        if ($("#" + window.location.hash.substr(1) + " .has_chart").length && $('#ShowTimelineButton').hasClass("btn-success")) {
            $("#show_timeline").removeClass("hidden");
        } else {
            $("#show_timeline").addClass("hidden");
        };
    }
    $('#ShowTimelineButton').click(function(e) {
        if ($('#ShowTimelineButton').hasClass("btn-default")) {
            // deactivate timeline
            if (window.location.hash.substr(1) !== '') {
                if ($("#" + window.location.hash.substr(1) + " .has_chart").length) {
                    $("#show_timeline").removeClass("hidden");
                }
            }
            $("#ShowTimelineButton").addClass("btn-success");
            $("#ShowTimelineButton").removeClass("btn-default");
        } else if ($('#ShowTimelineButton').hasClass("btn-success")) {
            // activate timeline
            $("#show_timeline").addClass("hidden");
            $("#ShowTimelineButton").addClass("btn-default");
            $("#ShowTimelineButton").removeClass("btn-success");
        }
    });
});
