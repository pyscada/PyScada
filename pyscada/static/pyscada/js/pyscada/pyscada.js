/* Javascript library for the PyScada web client based on jquery and flot, version 0.3.0-alpha.

Copyright (c) 2013-2014 Martin Schröder
Licensed under the GPL.




*/

var NotificationCount = 0
var PyScadaConfig;
var PyScadaPlots = [];
var JsonErrorCount = 0;
var auto_update_active = true;
// the code


function fetchConfig(){
	
	$.ajax({
		url: "json/config/",
		dataType: "json",
		timeout: 1000,
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
	
	$.ajax({
		url: PyScadaConfig.InitialDataFile,
		dataType: "json",
		timeout: 10000,
		success: function(data) {
			$.each(PyScadaPlots,function(plot_id){
				$.each(data,function(key,val){
					PyScadaPlots[plot_id].add(key,val);
				});
			});
			fetchData()
		},
		error: function(x, t, m) {
			addNotification(t, 3);
		}
	});
}

function fetchData() {
	if (auto_update_active) {
		$("#AutoUpdateStatus").show();
		$.ajax({
			url: PyScadaConfig.DataFile,
			dataType: "json",
			timeout: PyScadaConfig.RefreshRate,
			success: function(data) {
				if (data["timestamp"] > 0){
					time = data["timestamp"];
				}else{
					time = new Date().getTime();
				}
				$.each(data, function(key, val) {
				//append data to data array
					$.each(PyScadaPlots,function(plot_id){
						// PyScadaPlots[plot_id].add(key,val)
						PyScadaPlots[plot_id].addData(key,time,val);
						updateDataValues(key,val);
					});
				});
				$.each(PyScadaPlots,function(plot_id){
					PyScadaPlots[plot_id].update();
				});
				setTimeout('$( "#AutoUpdateStatus" ).hide();', 250);
				setTimeout('fetchData()', PyScadaConfig.RefreshRate);
				$("#AutoUpdateButton").removeClass("btn-warning");
				$("#AutoUpdateButton").addClass("btn-success");
				if (JsonErrorCount > 0) {
					JsonErrorCount = JsonErrorCount - 1;
				}
			},
			error: function(x, t, m) {
				addNotification(t, 3);
				JsonErrorCount = JsonErrorCount + 1;
				if (JsonErrorCount > 60) {
					auto_update_active = false;
					addNotification("error limit reached", 3);
				} else {
					setTimeout('$( "#AutoUpdateStatus" ).hide();', 250);
					if (auto_update_active) {
						setTimeout('fetchData()', 500);
					}
				}
				$("#AutoUpdateButton").removeClass("btn-success");
				$("#AutoUpdateButton").addClass("btn-warning");
				$("#AutoUpdateStatus").hide();
				}
		});
	}
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

function updateDataValues(key,val){
		// set value fields
		$(".type-numeric.var-" + key).html(Number(val).toPrecision(4));
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
		var LegendString = '<div class="legend"><table style="font-size:smaller;color:#545454"><tbody>';
		$.each(config.variables,function(key,val){
			if (typeof(config.variables[key])==="object"){
				LegendString +='<tr class="legendSeries"><td><input type="checkbox" checked="checked" id="'+config.placeholder.substring(1)+'-'+key+'-checkbox"></td><td class="legendColorBox"><div style="border:1px solid #ccc;padding:1px"><div style="width:4px;height:0;border:5px solid '+ LineColors[config.variables[key].color].toString() +';overflow:hidden"></div></div></td><td class="legendLabel">'+key+'</td><td class="legendValue type-numeric var-'+key+'"></td><td class="legendUnit">'+ config.variables[key].unit +'</td></tr>';
			}
		});
	
		LegendString +='</tbody></table></div><div class="btn-toolbar" role="toolbar"><div class="btn-group">';
		LegendString +='<button type="button" class="btn btn-default" id="'+config.placeholder.substring(1)+'-ResetSelection"><span class="glyphicon glyphicon-fullscreen"></span></button>';
		LegendString +='<button type="button" class="btn btn-default" id="'+config.placeholder.substring(1)+'-ZoomYToFit"><span class="glyphicon glyphicon-resize-vertical"></span></button>';
		LegendString +='</div></div>';

		$(config.legendplaceholder).append('<div id="'+config.placeholder.substring(1)+'-show" style="display:none;"><button type="button" class="btn btn-default" id="'+config.placeholder.substring(1)+'-btn-show" ><span class="glyphicon glyphicon-plus"></span></button></div><div id="'+config.legendplaceholder.substring(1)+'-legend" style="padding: 0px; position: relative;"><div class="legendTitle">'+ config.label +'</div>'+LegendString+'</div>');
		
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
	}
	
	function add(key,value){
		if (typeof(data[key])==="object"){
			data[key] = data[key].concat(value);
        	if (data[key].length > BufferSize){
        		// if buffer is full drop the first element
       			data[key] = data[key].splice(data[key].length-BufferSize,data[key].length);
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
		// add the selected data series to the "series" variable
		series = [];
		$.each(data,function(key){
			if($(config.placeholder+'-'+key+'-checkbox').is(':checked')){
				series.push({"data":data[key],"color":config.variables[key].color,"yaxis":config.variables[key].yaxis});		
			};
		});
		// update flot plot
		flotPlot.setData(series);
		// update x window
		pOpt = flotPlot.getOptions();
		now = new Date().getTime();
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

// init
fetchConfig()
