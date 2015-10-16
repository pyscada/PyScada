/* Javascript library for the PyScada web client based on jquery and flot,

version 0.6.19

Copyright (c) 2013-2015 Martin Schröder
Licensed under the GPL.

*/
var version = "0.6.19"
var NotificationCount = 0
var UpdateStatusCount = 0;
var PyScadaPlots = [];
var DataOutOfDate = false; 
var DataOutOfDateAlertId = '';
var JsonErrorCount = 0;
var auto_update_active = true;
var log_last_timestamp = 0;
var log_init = false;
var data_last_timestamp = 0;
var data_first_timestamp = 0;
var server_time = 0;
var log_frm = $('#page-log-form');
var log_frm_mesg = $('#page-log-form-message')
var csrftoken = $.cookie('csrftoken');
var fetch_data_timeout = 5000;
var init_chart_data_fetch_pending_count = 0;
var log_fetch_pending_count = false;
var refresh_rate = 2000;
var cache_timeout = 15000; // in milliseconds
var RootUrl = window.location.protocol+"//"+window.location.host + "/";
var VariableKeys = [];

// the code
var debug = 0;
var DataFetchingProcessCount = 0;

function showUpdateStatus(){
    $("#AutoUpdateStatus").show();
    UpdateStatusCount = UpdateStatusCount + 1;
}
function hideUpdateStatus(){
    UpdateStatusCount = UpdateStatusCount -1;
    if (UpdateStatusCount <= 0){
        $("#AutoUpdateStatus").hide();
    }
}
function raiseDataOutOfDateError(){
    if (!DataOutOfDate){
        DataOutOfDate = true;
        DataOutOfDateAlertId = addNotification('displayed data is out of date!',4,false,false);
    }
}
function clearDataOutOfDateError(){
    if (DataOutOfDate){
        DataOutOfDate = false;
        $('#'+DataOutOfDateAlertId).alert("close");
    }
}

function fetchData(variable_keys,first_timestamp,init,plot_instance) {
    variable_keys = typeof variable_keys !== 'undefined' ? variable_keys : VariableKeys;
    first_timestamp = typeof first_timestamp !== 'undefined' ? first_timestamp : data_first_timestamp;
    init = typeof variable_keys !== 'undefined' ? init : 0; // ((first_timestamp == 0) ? 1:0)
	
    if (auto_update_active) {
        showUpdateStatus();		
        $.ajax({
            url: RootUrl+'json/cache_data/',
            dataType: "json",
            timeout: ((first_timestamp == 0) ? fetch_data_timeout*10 : fetch_data_timeout),
            type: "POST",
            data:{ timestamp: data_last_timestamp, variables: variable_keys, first_timestamp:first_timestamp, init: init},
            success: function(data) {
                if (init){
                    $.each(data, function(key, val) {
                    //append data to data array
                        if (typeof(val)==="object" && typeof plot_instance !== 'undefined'){
							//alert(plot_id);
                            plot_instance.PreppendData(key,val);
                        }
                    });
					init_chart_data_fetch_pending_count--;
                }else{
                    timestamp = data['timestamp'];
                    delete data['timestamp'];
                    server_time = data['server_time'];
                    delete data['server_time'];
                    
                    if (data_last_timestamp < timestamp){
                        data_last_timestamp = timestamp;
                    }
                    if (data_first_timestamp == 0){
                        data_first_timestamp = data_last_timestamp;
                    }
                
                    DataOutOfDate = (server_time - timestamp  > cache_timeout);
                    if (DataOutOfDate){
                        raiseDataOutOfDateError();
                        $.each(PyScadaPlots,function(plot_id){
                            var variable_names = PyScadaPlots[plot_id].getVariableNames();
                            $.each(variable_names, function(key, val) {
                                PyScadaPlots[plot_id].addData(server_time,data_last_timestamp,Number.NaN);
                                updateDataValues(val,Number.NaN);
                            });
                        });
                    }else{
                        clearDataOutOfDateError();
                        $.each(data, function(key, val) {
                        //append data to data array
                            if (typeof(val)==="object"){
                                $.each(PyScadaPlots,function(plot_id){
                                    PyScadaPlots[plot_id].AppendData(key,val);
                                });
                                val = val.pop();
                                if (typeof(val[1])==="number"){
                                    updateDataValues(key,val[1]);
                                }else{
                                    updateDataValues(key,Number.NaN);
                                }
                            }
                        });
                    }
                    $.each(PyScadaPlots,function(plot_id){
                        var self = this, doBind = function() {
                            PyScadaPlots[plot_id].update();
                        };
                        $.browserQueue.add(doBind, this);
                    });
                }
                UpdateStatusCount = UpdateStatusCount -1;
                hideUpdateStatus();
                setTimeout('fetchData()', refresh_rate);
                $("#AutoUpdateButton").removeClass("btn-warning");
                $("#AutoUpdateButton").addClass("btn-success");
                if (JsonErrorCount > 0) {
                    JsonErrorCount = JsonErrorCount - 1;
                }
            },
            error: function(x, t, m) {
                if(JsonErrorCount % 5 == 0)
                    addNotification(t, 3);

                JsonErrorCount = JsonErrorCount + 1;
                if (JsonErrorCount > 60) {
                    auto_update_active = false;
                    addNotification("error limit reached", 3);
                } else {
                    UpdateStatusCount = UpdateStatusCount -1;
                    hideUpdateStatus();
                    if (auto_update_active) {
                        setTimeout('fetchData()', 500);
                    }
                    $.each(PyScadaPlots,function(plot_id){
                        var keys = PyScadaPlots[plot_id].getKeys();
                        $.each(keys, function(key, val) {
                            PyScadaPlots[plot_id].addData(val,data_last_timestamp,Number.NaN);
                        });
                    });
                }
				if (init){
					init_chart_data_fetch_pending_count--;
				}
                $("#AutoUpdateButton").removeClass("btn-success");
                $("#AutoUpdateButton").addClass("btn-warning");
                $("#AutoUpdateStatus").hide();
                }
        });
        updateLog();
    }else{
        $.each(PyScadaPlots,function(plot_id){
            var keys = PyScadaPlots[plot_id].getKeys();
            $.each(keys, function(key, val) {
                PyScadaPlots[plot_id].addData(val,data_last_timestamp,Number.NaN);
            });
        });
    }
}

function updateLog() {
    if (log_fetch_pending_count){return false;}
    showUpdateStatus();
    log_fetch_pending_count = true;
if(log_last_timestamp === 0){
        if(server_time > 0){
                log_last_timestamp = server_time; 
        }else{
            return false;	
        }
    }
    $.ajax({
        url: RootUrl+'json/log_data/',
        type: 'post',
        dataType: "json",
        timeout: 29000,
        data: {timestamp: log_last_timestamp},
        methode: 'post',
        success: function(data) {
            $.each(data,function(key,val){
                    if("timestamp" in data[key]){
                        if (log_last_timestamp<data[key].timestamp){
                            log_last_timestamp = data[key].timestamp;
                        }
                        addNotification(data[key].message,+data[key].level);
                    }
                });
            hideUpdateStatus();
        },
        error: function(x, t, m) {
            hideUpdateStatus();
        }
    });
}

function addNotification(message, level,timeout,clearable) {
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
        $('#notification_area').append('<div id="notification_Nb' + NotificationCount + '" class="notification alert alert-' + level + ' alert-dismissable" style="position: fixed; top: ' + top + 'px; right: ' + right + 'px; "><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>'+message_pre+ new Date().toLocaleTimeString() + ': ' + message + '</div>');
    }else{
        $('#notification_area_2').append('<div id="notification_Nb' + NotificationCount + '" class="notification alert alert-' + level + '" >'+message_pre+ new Date().toLocaleTimeString() + ': ' + message + '</div>');
    }
    if (timeout){
        setTimeout('$("#notification_Nb' + NotificationCount + '").alert("close");', 7000);
    }else{
        id = 'notification_Nb' + NotificationCount;
        NotificationCount = NotificationCount + 1;
        return id;
    }
    NotificationCount = NotificationCount + 1;
}

function updateDataValues(key,val){
        
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
        // set value fields
        $(".type-numeric.var-" + key).html(r_val);
        $('input.var-'+ key).attr("placeholder",r_val);
        // set button colors
        if (val === 0) {
            $(".label.type-bool.var-" + key).addClass("label-default");
            $(".label.type-bool.var-" + key).removeClass("label-primary");
            $(".label.type-bool.var-" + key).removeClass("label-info");
            $(".label.type-bool.var-" + key).removeClass("label-success");
            $(".label.type-bool.var-" + key).removeClass("label-warning");
            $(".label.type-bool.var-" + key).removeClass("label-danger");
            // inverted
            $(".label.type-bool.status-red-inv.var-" + key).addClass("label-danger");
            
            $('button.btn-default.write-task-btn.var-' + key).addClass("updateable");
            $('button.updateable.write-task-btn.var-' + key).addClass("btn-default");
            $('button.updateable.write-task-btn.var-' + key).removeClass("btn-success");
        } else {
            $(".label.type-bool.var-" + key).removeClass("label-default");
            $(".label.type-bool.var-" + key).removeClass("label-danger");
            $(".label.type-bool.status-blue.var-" + key).addClass("label-primary");
            $(".label.type-bool.status-info.var-" + key).addClass("label-info");
            $(".label.type-bool.status-green.var-" + key).addClass("label-success");
            $(".label.type-bool.status-yello.var-" + key).addClass("label-warning");
            $(".label.type-bool.status-red.var-" + key).addClass("label-danger");
            $(".label.type-bool.status-red-inv.var-" + key).addClass("label-default");
            $('button.btn-success.write-task-btn.var-' + key).addClass("updateable");
            $('button.updateable.write-task-btn.var-' + key).removeClass("btn-default");
            $('button.updateable.write-task-btn.var-' + key).addClass("btn-success");
        }
}

function PyScadaPlot(id){
    
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
        }
    },
    series = [],		// just the active data series
    keys   = [],		// list of variable keys (ids)
    variable_names = [], // list of all variable names 
    data = {},			// all the data
    flotPlot,			// handle to plot
    BufferSize = 5760, 	// buffered points
    WindowSize = 20, 	// displayed data window in minutes
    prepared = false,	// 
    InitDone = false,	// initial Data has loaded
    InitRetry	= 0,	// number of retries to load initial data
    legend_id = '#chart-legend-' + id,
    legend_table_id = '#chart-legend-table-' + id,
    chart_container_id = '#chart-container-'+id,
    legend_checkbox_id = '#chart-legend-checkbox-' + id + '-',
    legend_checkbox_status_id = '#chart-legend-checkbox-status-' + id + '-',
    variables = {},
    plot = this;
    
    
    // public functions
    plot.AppendData			= AppendData;
    plot.PreppendData       = PreppendData;
    plot.addData 			= addData;
    plot.update 			= update;
    plot.prepare 			= prepare;
    plot.getBufferSize		= function () { return BufferSize};
    plot.setBufferSize		= setBufferSize;
    plot.getData			= function () { return data };
    plot.getSeries 			= function () { return series };
    plot.getFlotObject		= function () { return flotPlot};
    plot.setWindowSize		= function (size){ WindowSize = size; update(); };
    plot.getKeys			= function (){ return keys};
    plot.getVariableNames	= function (){ return variable_names};

    plot.getInitStatus		= function () { if(InitDone){return InitRetry}else{return false}};
    plot.getId				= function () {return id};
    // init data
    $.each($(legend_table_id + ' .variable-config'),function(key,val){
        val_inst = $(val);
        variable_name = val_inst.data('name');
        variable_key = val_inst.data('key');
        data[variable_name] = [];
        variables[variable_name] = {'color':val_inst.data('color'),'yaxis':1}
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
        
        // expand the chart to the maximum width
        main_chart_area  = $(chart_container_id).closest('.main-chart-area');
        
        
        contentAreaHeight = main_chart_area.parent().height();
        mainChartAreaHeight = main_chart_area.height();
        
        if (contentAreaHeight>mainChartAreaHeight){
            main_chart_area.height(contentAreaHeight);
        }

        //
        flotPlot = $.plot($(chart_container_id + ' .chart-placeholder'), series,options);
        // update the plot
        update();
        // bind 
        $(chart_container_id + ' .chart-placeholder').bind("plotselected", function(event, ranges) {
            pOpt = flotPlot.getOptions();
            pOpt.yaxes[0].min = ranges.yaxis.from;
            pOpt.yaxes[0].max = ranges.yaxis.to;
            flotPlot.setupGrid();
            flotPlot.draw();
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
            pOpt = flotPlot.getOptions();
            pOpt.yaxes[0].min = $(chart_container_id).data('axes0Yaxis').min;
            pOpt.yaxes[0].max = $(chart_container_id).data('axes0Yaxis').max;
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
    }
    
    function setBufferSize(size){
        if (size <= BufferSize){
            BufferSize = size;
            $.each(data,function(key){
                if (data[key].length > BufferSize){
                    // if buffer is full drop the oldest elements
                    data[key].splice(-data[key].length,data[key].length-BufferSize);
                }
            });
        }else{
            BufferSize = size;	
        }
        
    }
    
    function addData(key,time,val){
        if (typeof(data[key])==="object"){
            data[key].push([time, val]);
            if (data[key].length > BufferSize){
                // if buffer is full drop the oldest elements
                data[key].splice(-data[key].length,data[key].length-BufferSize);
            }
        }
    }
    
    function AppendData(key,value){
        if (typeof(data[key])==="object"){
            data[key] = data[key].concat(value);
            if (data[key].length > BufferSize){
                // if buffer is full drop the first element
                data[key].splice(-data[key].length,data[key].length-BufferSize);
            }
        }
    }
    
    function PreppendData(key,value){
        if (typeof(data[key])==="object"){
            data[key] = value.concat(data[key]);
        }
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
            if(!InitDone){
            // try to load initial data
                if (init_chart_data_fetch_pending_count < 1){
                    init_chart_data_fetch_pending_count++;
                    fetchData(keys,0,1,plot); // keys, from_time,init, id 
					InitDone = true;
                }
            }
            // only update if plot is visible
            // add the selected data series to the "series" variable
            series = [];
            start_id = 0;
            $.each(data,function(key){
                if($(legend_checkbox_id+key).is(':checked')){
                    //if(start_id===-1){
                        start_id = findIndexSub(data[key],data_last_timestamp - (WindowSize * 1000 * 60),0);
                    //}
                    series.push({"data":data[key].slice(start_id),"color":variables[key].color,"yaxis":variables[key].yaxis});
                };
            });
            // update flot plot
            flotPlot.setData(series);
            // update x window
            pOpt = flotPlot.getOptions();
            pOpt.xaxes[0].min = data_last_timestamp - (WindowSize * 1000 * 60);
            pOpt.xaxes[0].max = data_last_timestamp;
            flotPlot.setupGrid();
            flotPlot.draw();
            $('.legend table').trigger("updateAll",["",function(table){}]);
        }
    }
}

function setWindowSize(size){
    $.each(PyScadaPlots,function(plot_id){
        PyScadaPlots[plot_id].setWindowSize(size);
    });
}

function findIndex(a,t){
    var i = a.length; //or 10
    while(i--){
        if (a[i]<=t){
            return i
        }
    }
}
function findIndexSub(a,t,d){
    var i = a.length; //or 10
    while(i--){
        if (a[i][d]<=t){
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
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


log_frm.submit(function () {
    if (log_frm_mesg.val()== ""){
        addNotification("can't add empty log entry",5);
    }else{
        $.ajax({
            type: log_frm.attr('method'),
            url: RootUrl+log_frm.attr('action'),
            data: log_frm.serialize(),
            success: function (data) {
                log_frm_mesg.val("");
                addNotification('new log entry successfuly added',9);
                updateLog();
            },
            error: function(data) {
                addNotification('new log entry adding failed',3);
            }
        });
    }
    return false;
})


//form/write_task/

function addWriteTask(var_id,value){
    $.ajax({
            type: 'post',
            url: RootUrl+'form/write_task/',
            data: {var_id:var_id,value:value},
            success: function (data) {
                
            },
            error: function(data) {
                addNotification('add new write task failed',3);
            }
        });
    
};

$('button.write-task-set').click(function(){
        var_id = $(this).attr('var_id');
        id = $(this).attr('id');
        value = $("#"+id+"-value").val();
        if (value == "" ){
            addNotification('please provide a value',3);
        }else{
            $.ajax({
                type: 'post',
                url: RootUrl+'form/write_task/',
                data: {var_id:var_id,value:value},
                success: function (data) {
                    
                },
                error: function(data) {
                    addNotification('add new write task failed',3);
                }
            });
        };
});

$('button.write-task-btn').click(function(){
        var_id = $(this).attr('var_id');
        id = $(this).attr('id');
        $('#'+id).removeClass('updateable');
        if($(this).hasClass('btn-default')){
            $.ajax({
                type: 'post',
                url: RootUrl+'form/write_task/',
                data: {var_id:var_id,value:1},
                success: function (data) {
                    $('#'+id).removeClass('btn-default')
                    $('#'+id).addClass('btn-success');
                },
                error: function(data) {
                    addNotification('add new write task failed',3);
                }
            });
        }else if ($(this).hasClass('btn-success')){
            $.ajax({
                type: 'post',
                url: RootUrl+'form/write_task/',
                data: {var_id:var_id,value:0},
                success: function (data) {
                    $('#'+id).addClass('btn-default')
                    $('#'+id).removeClass('btn-success');
                },
                error: function(data) {
                    addNotification('add new write task failed',3);
                }
            });
        }
});


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
    
    $.each($('.variable-config'),function(key,val){
        val = parseInt($(val).data('key'));
        if (VariableKeys.indexOf(val)==-1){
            VariableKeys.push(val)
        }
    });
    fetchData();
});
