/* Javascript library for the PyScada web client based on jquery and flot, version 0.3.0-alpha.

Copyright (c) 2013-2014 Martin Schröder
Licensed under the GPL.




*/


// the code
function main(){


	if (auto_update_active) {
		$("#AutoUpdateStatus").show();
		if (fetchData(PyScadaConfig.DataFile,PyScadaConfig.RefreshRate)){
			setTimeout('$( "#AutoUpdateStatus" ).hide();', 250);
			flotPlotUpdateEachData(now);
			setTimeout('fetchJsonData("' + ChartConfig.DataFile + '")', ChartConfig.RefreshRate);
			$("#AutoUpdateButton").removeClass("btn-warning");
			$("#AutoUpdateButton").addClass("btn-success");
			if (JsonErrorCount > 0) {
				JsonErrorCount = JsonErrorCount - 1;
			}
		}else{
			JsonErrorCount = JsonErrorCount + 1;
			if (JsonErrorCount > 60) {
				auto_update_active = false;
				addNotification("error limit reached", 3);
				ChartDataAppendNull();
			} else {
				setTimeout('$( "#AutoUpdateStatus" ).hide();', 250);
				if (auto_update_active) {
					setTimeout('fetchJsonData("' + ChartConfig.DataFile + '")', 500);
				}
				ChartDataAppendNull();
			}
			$("#AutoUpdateButton").removeClass("btn-success");
			$("#AutoUpdateButton").addClass("btn-warning");
			$("#AutoUpdateStatus").hide();
		}
	}else{
		ChartDataAppendNull();
	}
}

function fetchConfig(){
	$.ajax({
        url: "config.json",
        dataType: "json",
        timeout: 1000,
        success: function(data) {
			return data;
        },
        error: function(x, t, m) {
            addNotification(t, 3);
        }
    });
}

function fetchData(url,timeout) {
	
		$.ajax({
			url: url,
			dataType: "json",
			timeout: timeout,
			success: function(data) {
				var now = new Date().getTime();
				var time = now
				$.each(data, function(key, val) {
					//append data to data array
					if (typeof(PyScadaConfig.variables[key])==="object"){
						PyScadaConfig.variables[key].data.push([time, val]);
						if (PyScadaConfig.variables[key].data.length > PyScadaConfig.ChartBufferSize){
							PyScadaConfig.variables[key].data =PyScadaConfig.variables[key].data.splice(1,PyScadaConfig.variables[key].data.length);
						}
    				}
				});
				return true
				
			},
			error: function(x, t, m) {
				addNotification(t, 3);
				return false
				
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
    if (level === 1) {
        level = 'success';
    } else if (level === 2) {
        level = 'info';
    } else if (level === 3) {
        level = 'warning';
    } else if (level === 4) {
        level = 'danger';
    }
    $('#notification_area').append('<div id="notification_Nb' + NotificationCount + '" class="notification alert alert-' + level + ' alert-dismissable" style="position: fixed; top: ' + top + 'px; right: ' + right + 'px; "><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button><strong>Warning!</strong> ' + new Date().toLocaleTimeString() + ': ' + message + '</div>');
    setTimeout('$("#notification_Nb' + NotificationCount + '").alert("close");', 10000);
    NotificationCount = NotificationCount + 1;
}

function updateDataValues(data){
	$.each(data, function(key, val) {
		// set value fields
		$(".type-numeric.var-" + key).html(val);
		// set button colors
		if (val === 0) {
			$(".type-bool.var-" + key).addClass("label-default");
			$(".type-bool.var-" + key).removeClass("label-success");
			$(".type-bool.var-" + key).removeClass("label-warning");
			$(".type-bool.var-" + key).removeClass("label-danger");
		} else {
			$(".type-bool.var-" + key).removeClass("label-default");
			$(".type-bool.status-green.var-" + key).addClass("label-success");
			$(".type-bool.status-yello.var-" + key).addClass("label-warning");
			$(".type-bool.status-red.var-" + key).addClass("label-danger");
		}
	});
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
        }
	},
	series,				// just the active data series
	data,				// all the data
	flotPlot,			// handle to plot
	BufferSize = 5760, 	// buffered points
	WindowSize = 20, 	// displayed data window in minutes
	plot = this;
	
	// public functions
	plot.addData 			= addData;
	plot.update 			= update;
	plot.updateSelection 	= updateSelection;
	plot.expandToMaxWidth 	= expandToMaxWidth;
	plot.getBufferSize		= function () { return BufferSize};
	plot.setBufferSize		= setBufferSize;
	
	function prepare(){
		// prepare legend
		var LegendString = '<div class="legend"><table style="font-size:smaller;color:#545454"><tbody>';
		$.each(config.variables,function(key,val){
			if (typeof(config.variables[key])==="object"){
				LegendString +='<tr class="legendSeries"><td><input type="checkbox" checked="checked" id="'+config.placeholder+'-'+key+'-checkbox"></td><td class="legendColorBox"><div style="border:1px solid #ccc;padding:1px"><div style="width:4px;height:0;border:5px solid '+ LineColors[config.variables[key].color].toString() +';overflow:hidden"></div></div></td><td class="legendLabel">'+key+'</td><td class="legendValue type-numeric var-'+key+'"></td><td class="legendUnit">'+ config.variables[key].unit +'</td></tr>';
			}
		});
	
		LegendString +='</tbody></table></div><div class="btn-toolbar" role="toolbar"><div class="btn-group">';
		LegendString +='<button type="button" class="btn btn-default" id="'+config.placeholder+'-ResetSelection"><span class="glyphicon glyphicon-fullscreen"></span></button>';
		LegendString +='<button type="button" class="btn btn-default" id="'+config.placeholder+'-ZoomYToFit"><span class="glyphicon glyphicon-resize-vertical"></span></button>';
		LegendString +='</div></div>';

		$(config.legendplaceholder).append('<div id="'+config.placeholder+'-show" style="display:none;"><button type="button" class="btn btn-default" id="'+config.placeholder+'-btn-show" ><span class="glyphicon glyphicon-plus"></span></button></div><div id="'+config.legendplaceholder+'-legend">'+LegendString+'</div>');
		$.each(config.variables,function(key,val){
			$(config.placeholder+'-'+key+'-checkbox').change(function() {
				plot.update()
			});
		});
		
		expandToMaxWidth();
		
		contentAreaHeight = $(config.placeholder).closest('.main-chart-area').parent().height();
		mainChartAreaHeight = $(config.placeholder).closest('.main-chart-area').height();
		if (contentAreaHeight>mainChartAreaHeight){
			$(config.placeholder).closest('.main-chart-area').height(contentAreaHeight);
		}
		
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
		
		
		//
		
		flotPlot = $.plot($(config.placeholder + ' .chart-placeholder'), series,options)
		// bind 
		$(config.placeholder + ' .chart-placeholder').bind("plotselected", function(event, ranges) {
			pOpt = flotPlot.getOptions();
			pOpt.yaxes[0].min = ranges.yaxis.from;
			pOpt.yaxes[0].max = ranges.yaxis.to;
			flotPlot.setupGrid();
			flotPlot.draw();
			flotPlot.clearSelection();
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
       			data[key] = data[key].splice(data[key].length-BufferSize,data[key].length);
        	}
    	}
    	plot.update;
	}
	
	
	function update(){
		// add the selected data series to the "series" variable
		series = [];
		if($(config.placeholder).is(":visible")){
			$.each(data,function(key){
				if($(config.placeholder+'-'+key+'-checkbox').is(':checked')){
					series.push(data[key]);
				};
			});
		}
		// update flot plot
		flotPlot.setData(series);
		// update x window
		pOpt = flotPlot.getOptions();
		pOpt.xaxes[0].min = now - (WindowSize * 1000 * 60);
		flotPlot.setupGrid();
		flotPlot.draw();
	}
	
	
	function expandToMaxWidth(){
		contentAreaWidth = $(config.placeholder).closest('.main-chart-area').parent().width()
		sidebarAreaWidth = $(config.legendplaceholder).closest('.legend-sidebar').width();
		mainChartAreaWidth = contentAreaWidth - sidebarAreaWidth - 70;
		$(config.placeholder).closest('.main-chart-area').width(mainChartAreaWidth);
	}
}