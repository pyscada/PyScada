/* Javascript library for the PyScada web client based on jquery and flot, version 0.3.0-alpha.

Copyright (c) 2013-2014 Martin Schröder
Licensed under the GPL.




*/

var NotificationCount = 0
var PyScadaConfig;
var PyScadaPlots = [];
var JsonErrorCount = 0;
var auto_update_active = true;
var log_last_timestamp = 0;
var log_frm = $('#page-log-form');
var log_frm_mesg = $('#page-log-form-message')
var csrftoken = $.cookie('csrftoken');
// the code
var tic = new Date().getTime()/1000;
var debug = 0; 
function fetchConfig(){
	
	$.ajax({
		url: "json/config/",
		dataType: "json",
		timeout: 5000,
		success: function(data) {
			PyScadaConfig = data;
			$.each(PyScadaConfig.config,function(key,val){
				PyScadaPlots.push(new PyScadaPlot(val));
			});
			fetchInitData()
		},
		error: function(x, t, m) {
			addNotification(t, 3);
		}
	});
}

function fetchInitData(){
	// plot data
	$.ajax({
		url: PyScadaConfig.InitialDataFile,
		dataType: "json",
		timeout: 30000,
		success: function(data) {
			$.each(PyScadaPlots,function(plot_id){
				$.each(data,function(key,val){
					PyScadaPlots[plot_id].add(key,val);
				});
			});
			fetchData();
		},
		error: function(x, t, m) {
			addNotification(t, 3);
			fetchData();
		}
	});
	// log
	$.ajax({
		url: PyScadaConfig.LogDataFile,
		dataType: "json",
		timeout: 30000,
		success: function(data) {
			
			$.each(data,function(key,val){
				if (log_last_timestamp<data[key].fields.timestamp){
					log_last_timestamp = data[key].fields.timestamp;
				}
				log_row = '<tr>';
				log_row += '<td><span class="hidden" >'+data[key].fields.timestamp.toFixed(3)+'</span>' + new Date(data[key].fields.timestamp*1000).toLocaleString(); + '</td><!-- Date -->';
				log_row += '<td>' + data[key].fields.level + '</td><!-- Level -->';
				log_row += '<td>' + data[key].fields.message + '</td><!-- Message -->';
				log_row += '</tr>';
				$('#log-table tbody').append(log_row);
			});
			$('#log-table').tablesorter({sortList: [[0,-1]]});
		},
		error: function(x, t, m) {
			addNotification(t, 3);
		}
	});
}

function fetchData() {
	tic = new Date().getTime()/1000;
	if(debug>0){
		$('#page-log').append('<p>0.00: start</p>')
	}
	if (auto_update_active) {
		$("#AutoUpdateStatus").show();
		
		$.ajax({
			url: PyScadaConfig.DataFile,
			dataType: "json",
			timeout: PyScadaConfig.RefreshRate,
			success: function(data) {
				if(debug>1){
					$('#page-log').append('<p>' + (new Date().getTime()/1000-tic).toFixed(2) + ': data feched</p>')
				}
				if (data["timestamp"] > 0){
					time = data["timestamp"];
				}else{
					time = new Date().getTime();
				}
				$.each(data, function(key, val) {
				//append data to data array
					$.each(PyScadaPlots,function(plot_id){
						PyScadaPlots[plot_id].addData(key,time,val);
					});
					updateDataValues(key,val);
				});
				if(debug>1){
					$('#page-log').append('<p>' + (new Date().getTime()/1000-tic).toFixed(2) + ': plot data cache updated, and fields updated</p>')
				}
				$.each(PyScadaPlots,function(plot_id){
					var self = this, doBind = function() {
						PyScadaPlots[plot_id].update();
					};
					$.browserQueue.add(doBind, this);
				});
				
				if(debug>1){
					$('#page-log').append('<p>' + (new Date().getTime()/1000-tic).toFixed(2) + ': plots updated</p>')
				}
				setTimeout('$( "#AutoUpdateStatus" ).hide();', 100);
				setTimeout('fetchData()', PyScadaConfig.RefreshRate);
				$("#AutoUpdateButton").removeClass("btn-warning");
				$("#AutoUpdateButton").addClass("btn-success");
				if (JsonErrorCount > 0) {
					JsonErrorCount = JsonErrorCount - 1;
				}
				if(debug>0){
					$('#page-log').append('<p>' + (new Date().getTime()/1000-tic).toFixed(2) + ': ready</p>')
				}
			},
			error: function(x, t, m) {
				addNotification(t, 3);
				JsonErrorCount = JsonErrorCount + 1;
				if (JsonErrorCount > 60) {
					auto_update_active = false;
					addNotification("error limit reached", 3);
				} else {
					setTimeout('$( "#AutoUpdateStatus" ).hide();', 100);
					if (auto_update_active) {
						setTimeout('fetchData()', 500);
					}
				}
				$("#AutoUpdateButton").removeClass("btn-success");
				$("#AutoUpdateButton").addClass("btn-warning");
				$("#AutoUpdateStatus").hide();
				}
		});
		updateLog();
	}
}

function updateLog() {
	
	$.ajax({
		url: PyScadaConfig.LogDataFile,
		type: 'post',
		dataType: "json",
		timeout: 3000,
		data: {timestamp: log_last_timestamp},
		methode: 'post',
		success: function(data) {
			$.each(data,function(key,val){
				if (log_last_timestamp<data[key].fields.timestamp){
					log_last_timestamp = data[key].fields.timestamp;
				}
				log_row = '<tr>';
				log_row += '<td><span class="hidden" >'+data[key].fields.timestamp.toFixed(3)+'</span>' + new Date(data[key].fields.timestamp*1000).toLocaleString(); + '</td><!-- Date -->';
				log_row += '<td>' + data[key].fields.level + '</td><!-- Level -->';
				log_row += '<td>' + data[key].fields.message + '</td><!-- Message -->';
				log_row += '</tr>';
				$('#log-table tbody').append(log_row);
				if (!$('#log-table').is(":visible")){
					addNotification(data[key].fields.message,+data[key].fields.level);
				}
			});
			$('#log-table').trigger("updateAll",["",function(table){}]);
		},
		error: function(x, t, m) {
			addNotification(t, 3);
		}
	});
}

function addNotification(message, level) {
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
    
    $('#notification_area').append('<div id="notification_Nb' + NotificationCount + '" class="notification alert alert-' + level + ' alert-dismissable" style="position: fixed; top: ' + top + 'px; right: ' + right + 'px; "><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>'+message_pre+ new Date().toLocaleTimeString() + ': ' + message + '</div>');
    setTimeout('$("#notification_Nb' + NotificationCount + '").alert("close");', 7000);
    NotificationCount = NotificationCount + 1;
}

function updateDataValues(key,val){
		// set value fields
		$(".type-numeric.var-" + key).html(Number(val).toPrecision(4));
		$('input.var-'+ key).attr("placeholder",Number(val).toPrecision(4));
		// set button colors
		if (val === 0) {
			$(".type-bool.var-" + key).addClass("label-default");
			$(".type-bool.var-" + key).removeClass("label-primary");
			$(".type-bool.var-" + key).removeClass("label-info");
			$(".type-bool.var-" + key).removeClass("label-success");
			$(".type-bool.var-" + key).removeClass("label-warning");
			$(".type-bool.var-" + key).removeClass("label-danger");
			$('button.btn-default.write-task-btn.var-' + key).addClass("updateable");
			$('button.updateable.write-task-btn.var-' + key).addClass("btn-default");
			$('button.updateable.write-task-btn.var-' + key).removeClass("btn-success");
		} else {
			$(".type-bool.var-" + key).removeClass("label-default");
			$(".type-bool.status-blue.var-" + key).addClass("label-primary");
			$(".type-bool.status-info.var-" + key).addClass("label-info");
			$(".type-bool.status-green.var-" + key).addClass("label-success");
			$(".type-bool.status-yello.var-" + key).addClass("label-warning");
			$(".type-bool.status-red.var-" + key).addClass("label-danger");
			$('button.btn-success.write-task-btn.var-' + key).addClass("updateable");
			$('button.updateable.write-task-btn.var-' + key).removeClass("btn-default");
			$('button.updateable.write-task-btn.var-' + key).addClass("btn-success");
		}
}

function PyScadaPlot(config){
	
	var options = {
		xaxis: {
            mode: "time",
            ticks: config.xaxis.ticks,
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
	data = {},			// all the data
	flotPlot,			// handle to plot
	BufferSize = 5760, 	// buffered points
	WindowSize = 20, 	// displayed data window in minutes
	prepared = false,	// 
	plot = this;
	
	// public functions
	plot.add				= add;
	plot.addData 			= addData;
	plot.update 			= update;
	plot.prepare 			= prepare;
	plot.expandToMaxWidth 	= expandToMaxWidth;
	plot.getBufferSize		= function () { return BufferSize};
	plot.setBufferSize		= setBufferSize;
	plot.getData			= function () { return data };
	plot.getSeries 			= function () { return series };
	plot.getFlotObject		= function () { return flotPlot};
	plot.setWindowSize		= function (size){ WindowSize = size; update(); };
	// init data
	$.each(config.variables,function(key){
			data[key] = [];
		});
	
	
	function prepare(){
		var LineColors = []
		colorPool = ["#edc240", "#afd8f8", "#cb4b4b", "#4da74d", "#9440ed"];
		colorPoolSize = colorPool.length;
		neededColors = 50
		variation = 0;
		for (i = 0; i < neededColors; i++) {
			c = $.color.parse(colorPool[i % colorPoolSize] || "#666");

			// Each time we exhaust the colors in the pool we adjust
			// a scaling factor used to produce more variations on
			// those colors. The factor alternates negative/positive
			// to produce lighter/darker colors.

			// Reset the variation after every few cycles, or else
			// it will end up producing only white or black colors.

			if (i % colorPoolSize == 0 && i) {
				if (variation >= 0) {
					if (variation < 0.5) {
						variation = -variation - 0.2;
					} else variation = 0;
				} else variation = -variation;
			}

			//colors.push(c.scale('rgb', 1 + variation));
			LineColors.push(c.scale('rgb', 1 + variation));
		}
		
		// prepare legend
		var LegendString = '<div class="legend"><table id="'+config.placeholder.substring(1)+'-table" class="tablesorter" style="font-size:smaller;color:#545454"><thead><tr><th>&nbsp;</th><th class="sorter-false">&nbsp;</th><th class="sorter-text">&nbsp;</th><th class="sorter-float">&nbsp;</th><th class="sorter-text">&nbsp;</th></tr></thead><tbody>';
		$.each(config.variables,function(key,val){
			if (typeof(config.variables[key])==="object"){
				if (typeof(config.variables[key].color)== "string"){
					var line_color = config.variables[key].color;
				}else{
					var line_color = LineColors[config.variables[key].color].toString();
					}
				LegendString +='<tr class="legendSeries"><td><span class="hidden" id="'+config.placeholder.substring(1)+'-'+key+'-checkbox-status" >1</span><input type="checkbox" checked="checked" id="'+config.placeholder.substring(1)+'-'+key+'-checkbox"></td><td class="legendColorBox"><div style="border:1px solid #ccc;padding:1px"><div style="width:4px;height:0;border:5px solid '+ line_color +';overflow:hidden"></div></div></td><td class="legendLabel">'+config.variables[key].label+'</td><td class="legendValue type-numeric var-'+key+'"></td><td class="legendUnit">'+ config.variables[key].unit +'</td></tr>';
			}
		});
	
		LegendString +='</tbody></table></div>';
		//<div class="btn-toolbar" role="toolbar"><div class="btn-group">';
		//LegendString +='<button type="button" class="btn btn-default" id="'+config.placeholder.substring(1)+'-ResetSelection"><span class="glyphicon glyphicon-fullscreen"></span></button>';
		//LegendString +='<button type="button" class="btn btn-default" id="'+config.placeholder.substring(1)+'-ZoomYToFit"><span class="glyphicon glyphicon-resize-vertical"></span></button>';
		//LegendString +='</div></div>';

		$(config.legendplaceholder).append('<div id="'+config.placeholder.substring(1)+'-show" style="display:none;"><button type="button" class="btn btn-default" id="'+config.placeholder.substring(1)+'-btn-show" ><span class="glyphicon glyphicon-plus"></span></button></div><div id="'+config.legendplaceholder.substring(1)+'-legend" style="padding: 0px; position: relative;"><div class="legendTitle">'+ config.label +'</div>'+LegendString+'</div>');
		
		$(config.placeholder+'-table').tablesorter({sortList: [[2,0]]});
		
		$.each(config.variables,function(key,val){
			$(config.placeholder+'-'+key+'-checkbox').change(function() {
				plot.update();
				if ($(config.placeholder+'-'+key+'-checkbox').is(':checked')){
					$(config.placeholder+'-'+key+'-checkbox-status').html(1);
				}else{
					$(config.placeholder+'-'+key+'-checkbox-status').html(0);
				}
			});
		});
		

		expandToMaxWidth();
		contentAreaHeight = $(config.placeholder).closest('.main-chart-area').parent().height();
		mainChartAreaHeight = $(config.placeholder).closest('.main-chart-area').height();
		if (contentAreaHeight>mainChartAreaHeight){
			$(config.placeholder).closest('.main-chart-area').height(contentAreaHeight);
		}

			
	
		//
		$(config.placeholder).addClass('chart-container');
		$(config.placeholder).append('<div class="chart-placeholder"></div>')
		flotPlot = $.plot($(config.placeholder + ' .chart-placeholder'), series,options)
		// update the plot
		update()
		// bind 
		$(config.placeholder + ' .chart-placeholder').bind("plotselected", function(event, ranges) {
			pOpt = flotPlot.getOptions();
			pOpt.yaxes[0].min = ranges.yaxis.from;
			pOpt.yaxes[0].max = ranges.yaxis.to;
			flotPlot.setupGrid();
			flotPlot.draw();
			flotPlot.clearSelection();
		});
		
		
		var chartTitle = $("<div class='chartTitle'></div>")
		.text(config.label)
		.appendTo(config.placeholder + ' .chart-placeholder');

		// Since CSS transforms use the top-left corner of the label as the transform origin,
		// we need to center the y-axis label by shifting it down by half its width.
		// Subtract 20 to factor the chart's bottom margin into the centering.
	
		chartTitle.css("margin-left", -chartTitle.width() / 2);
		
		
		var yaxisLabel = $("<div class='axisLabel yaxisLabel'></div>")
		.text(config.axes[0].yaxis.label)
		.appendTo(config.placeholder + ' .chart-placeholder');
		
		
		// Since CSS transforms use the top-left corner of the label as the transform origin,
		// we need to center the y-axis label by shifting it down by half its width.
		// Subtract 20 to factor the chart's bottom margin into the centering.
	
		yaxisLabel.css("margin-top", yaxisLabel.width() / 2 - 20);
	
	
		$(config.placeholder + ' .chart-placeholder').append('<div class="chart-btn-bar" ><div class="btn-group"><button type="button" class="btn btn-default" id="'+config.placeholder.substring(1)+'-ResetSelection"><span class="glyphicon glyphicon-fullscreen"></span></button><button type="button" class="btn btn-default" id="'+config.placeholder.substring(1)+'-ZoomYToFit"><span class="glyphicon glyphicon-resize-vertical"></span></button></div></div>');

		$(config.placeholder + "-ResetSelection").click(function() {
			pOpt = flotPlot.getOptions();
			pOpt.yaxes[0].min = config.axes[0].yaxis.min;
			pOpt.yaxes[0].max = config.axes[0].yaxis.max;
			flotPlot.setupGrid();
			flotPlot.draw();
		});
		
		$(config.placeholder + "-ZoomYToFit").click(function() {
			pOpt = flotPlot.getOptions();
			aOpt = flotPlot.getYAxes();
			pOpt.yaxes[0].min = aOpt.datamin;
			pOpt.yaxes[0].max = aOpt.datamax;
			flotPlot.setupGrid();
			flotPlot.draw();
		});
		
		$(config.placeholder + "-minimize").click(function() {
			$(config.legendplaceholder).hide();
			$(config.placeholder).hide();
			$(config.placeholder + "-show").show();
		});
		
		$(config.placeholder + "-btn-show").click(function() {
			$(config.legendplaceholder).show();
			$(config.placeholder).show();
			$(config.placeholder + "-show").hide();
		});
	
	
	
	}
	
	function setBufferSize(size){
		if (size <= BufferSize){
			BufferSize = size;
			$.each(data,function(key){
				if (data[key].length > BufferSize){
        			// if buffer is full drop the first element
       				data[key] = data[key].splice(data[key].length-BufferSize,data[key].length);
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
        		// if buffer is full drop the first element
       			data[key].splice(data[key].length-BufferSize);
        	}
    	}
	}
	
	function add(key,value){
		if (typeof(data[key])==="object"){
			data[key] = data[key].concat(value);
        	if (data[key].length > BufferSize){
        		// if buffer is full drop the first element
       			data[key].splice(data[key].length-BufferSize);
        	}
    	}
	}
	
	function update(){
		if(!prepared ){
			if($(config.placeholder).is(":visible")){
				prepared = true;
				prepare();
			}else{
				return;
			}
		}
		if($(config.placeholder).is(":visible")){
			// only update if plot is visible
			// add the selected data series to the "series" variable
			series = [];
			start_id = 0;
			now = new Date().getTime();
			$.each(data,function(key){
				if($(config.placeholder+'-'+key+'-checkbox').is(':checked')){
					//if(start_id===-1){
						start_id = findIndexSub(data[key],now - (WindowSize * 1000 * 60),0);
					//}
					series.push({"data":data[key].slice(start_id),"color":config.variables[key].color,"yaxis":config.variables[key].yaxis});
					//series.push({"data":data[key],"color":config.variables[key].color,"yaxis":config.variables[key].yaxis});		
				};
			});
			// update flot plot
			flotPlot.setData(series);
			// update x window
			pOpt = flotPlot.getOptions();
			pOpt.xaxes[0].min = now - (WindowSize * 1000 * 60);
			flotPlot.setupGrid();
			flotPlot.draw();
			$('.legend table').trigger("updateAll",["",function(table){}]);
		}
	}
	
	function expandToMaxWidth(){
		contentAreaWidth = $(config.placeholder).closest('.main-chart-area').parent().width()
		sidebarAreaWidth = $(config.legendplaceholder).closest('.legend-sidebar').width();
		mainChartAreaWidth = contentAreaWidth - sidebarAreaWidth - 15;
		$(config.placeholder).closest('.main-chart-area').width(mainChartAreaWidth);
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


//$('li').each(function() {
        //var self = this, doBind = function() {
            //$(self).bind('click', function() {
                //alert('Yeah you clicked me');
            //});
        //};
        //$.queue.add(doBind, this);
    //});
    
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
// init
fetchConfig();


log_frm.submit(function () {
	if (log_frm_mesg.val()== ""){
		addNotification("can't add empty log entry",5);
	}else{
		$.ajax({
			type: log_frm.attr('method'),
			url: log_frm.attr('action'),
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
			url: 'form/write_task/',
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
				url: 'form/write_task/',
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
				url: 'form/write_task/',
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
				url: 'form/write_task/',
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
$(function() {
  // Setup drop down menu
  $('.dropdown-toggle').dropdown();
 
  // Fix input element click problem
  $('.dropdown input, .dropdown label, .dropdown button').click(function(e) {
    e.stopPropagation();
  });
});
