var plot; // main plot object
var overview; // overview plot object
var mainPlotId;
var overviewPlotId;
var plotOptions; // main plot options
var overviewOptions; // overview plot options
var data = []; // plot data
var alreadyFetched = {};	 // 
var yAxisVariables = [];
var initDone = false;
var updateChart = 0;
var csrftoken = $.cookie('csrftoken');
var varIds = [];
function initPlot(mainPlotIdIn,overviewPlotIdIn){
	mainPlotId = mainPlotIdIn;
	overviewPlotId = overviewPlotIdIn;
	// set plot properties
	plotOptions = {
        		xaxis: { 
        			mode: "time", tickLength: 5, 
        			timeformat: "%d.%m %H:%M"
        				},
				series: {
        			lines: { show: true },
        			points: { show: true }
    					},
    			crosshair: { mode: "x" },
            	grid: { hoverable: true, autoHighlight: false },
    			yaxis: {tickFormatter: function (val, axis) {if(val.toFixed(axis.tickDecimals) > axis.max){return yAxisVariables[axis.n-1] + "\n" + val.toFixed(axis.tickDecimals)}{return val.toFixed(axis.tickDecimals)}}},
        		selection: { mode: "x" }
        		//grid: { markings: weekendAreas }
    				};
    overviewOptions = {
        		series: {
            		lines: { show: true, lineWidth: 1 },
            		shadowSize: 0
        				},
        		xaxis: { ticks: [], mode: "time" },
        		yaxis: { ticks: [], min: 0, autoscaleMargin: 0.1 },
        		selection: { mode: "x" },
        		legend: { show: false }	
        				};
    // expand plot div to screensize
}

function initPlotWindow(){
	$('#'+mainPlotId).css('display','');
	$('#'+overviewPlotId).css('display','');
	$(window).resize(function(){
		$('#'+mainPlotId).width($('#'+mainPlotId).parent().width()-5);
		$('#'+mainPlotId).height($('#'+mainPlotId).parent().height()-$('#fullPlotOverview').height()-$('#fullPlotMenu').height()-20);
		resizePlot();
	});
	$('#'+mainPlotId).width($('#'+mainPlotId).parent().width()-5);
	$('#'+mainPlotId).height($('#'+mainPlotId).parent().height()-$('#fullPlotOverview').height()-$('#fullPlotMenu').height()-20);
// now draw the plotwindows
    plot = $.plot($('#'+mainPlotId), data, plotOptions);
   	overview = $.plot($('#'+overviewPlotId), data, overviewOptions);
	connectPlotOverview();
	addDataPointer();
	
	$('#autoUpdate').click(toggleAutoUpdate);
	initDone = true;
}

function toggleAutoUpdate(){
	if(updateChart){
		$('#autoUpdate').attr('value',"start autoupdate");
		updateChart = 0;
	}else{
		updateChart = 1;
		$('#autoUpdate').attr('value',"stop autoupdate");
		setTimeout('processAjaxJsonQuery()', 10000);
	}

}

function connectPlotOverview(){
	// now connect the two
    $('#'+mainPlotId).bind("plotselected", function (event, ranges) {
    // do the zooming
    	plot = $.plot($('#'+mainPlotId), data,
    	$.extend(true, {}, plotOptions, 
    		{
            	xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to }
            }));

    	// don't fire event on the overview to prevent eternal loop
    	overview.setSelection(ranges, true);
    });
    $('#'+overviewPlotId).bind("plotselected", function (event, ranges) {
        plot.setSelection(ranges);
    });
}

function addQueryVarPlotDataJson(dataid) {
    //fetch the data with jQuery
    if (!alreadyFetched[dataid])
		alreadyFetched[dataid] = false;
    processAjaxJsonQuery(true);
}

function processAjaxJsonQuery(queryNewVar){
	function onDataReceived(series) {
    	// data is now an ordinary Javascript object
        // let's add it to our current data
        for (key in series){
        	if (alreadyFetched[series[key].id]) {
        		for (listEntry in data){
    				if(data[listEntry].id==series[key].id)
    					if(series[key].data.length != 0){
    						for (valuePair in series[key].data)
    							data[listEntry].data.push(series[key].data[valuePair]);
    					}
    			}
        	}else{
        		alreadyFetched[series[key].id] = true;
        		series[key].yaxis = determineYAxis(series[key].unit);
        		data.push(series[key]);
        	}
        }
        // ubdate the plot
        ubdatePlot();
    }
    var varIds = [];
	var tstamp = new Date().getTime()-(3600)*1000;
	if($('#datepicker').datetimepicker('getDate') && $('#useActualDate').is(':checked'))
		tstamp = $('#datepicker').datetimepicker('getDate').getTime();
    for (dataid in alreadyFetched){
   		if (alreadyFetched[dataid]) {
    		// var is fetched query update 
    		for (listEntry in data){
    			if(data[listEntry].id==dataid && data[listEntry].data.length != 0)
    				var tstamp = data[listEntry].data[data[listEntry].data.length-1][0]
    		}
    	}else{
    		// var is not fetched jet
    		var tstamp = new Date().getTime()-(3600)*1000;
    	}
    	varIds.push(dataid);
    }
    var dataurl = '/json/data/';
    $.ajax({
        url: dataurl,
        type: 'POST',
        data: {timestamp:tstamp,varIds:varIds},
        dataType: 'json'
        }).done(onDataReceived);
        
    if (updateChart && !queryNewVar){
        setTimeout('processAjaxJsonQuery()', 10000);
        return true;
    }
    return false;
}

function RemoveValueFromPlot(id){

}

function ubdatePlot(){
	if(!initDone){
		initPlotWindow();
	}
	overview.setData(data);
    overview.setupGrid()
    overview.draw();
    
    plot.setData(data);
    plot.setupGrid()
    plot.draw()
}

function resizePlot(){
	plot.resize();
	plot.setupGrid()
    plot.draw();
}

function addDataPointer(){
		var legends = $('#'+mainPlotId+" .legendLabel");
    		legends.each(function () {
        		// fix the widths so they don't jump around
        		$(this).css('width', $(this).width());
    		});		
			var updateLegendTimeout = null;
    		var latestPosition = null;
    
    		function updateLegend() {
        		updateLegendTimeout = null;
        
        		var pos = latestPosition;
        
        		var axes = plot.getAxes();
        		if (pos.x < axes.xaxis.min || pos.x > axes.xaxis.max ||
            		pos.y < axes.yaxis.min || pos.y > axes.yaxis.max)
            		return;

        		var i, j, dataset = plot.getData();
        		for (i = 0; i < dataset.length; ++i) {
            		var series = dataset[i];

            		// find the nearest points, x-wise
            		for (j = 0; j < series.data.length; ++j)
                		if (series.data[j][0] > pos.x)
                    	break;
            
            		// now interpolate
            		var y, p1 = series.data[j - 1], p2 = series.data[j];
            		if (p1 == null)
                		y = p2[1];
            		else if (p2 == null)
                		y = p1[1];
            		else
                		y = p1[1] + (p2[1] - p1[1]) * (pos.x - p1[0]) / (p2[0] - p1[0]);
            		legends.eq(i).text(series.label.replace(/= [0-9-\.]*/, "= " + y.toFixed(2)));
        		}
    		}
    		
    		$('#'+mainPlotId).bind("plothover",  function (event, pos, item) {
        		latestPosition = pos;
        		if (!updateLegendTimeout)
            		updateLegendTimeout = setTimeout(updateLegend, 50);
    		});
}

function determineYAxis(unit){
	if (!(yAxisVariables.lastIndexOf(unit)>=0)) {
		yAxisVariables[yAxisVariables.length] = unit;
	}
	return yAxisVariables.length;
}

// utility functions
function getMaxFromList(listVar){
	var listEntryOld = 0;
	for (listEntry in listVar){
		if (listVar[listEntry] >	listEntryOld)
			listEntryOld = listVar[listEntry];
	}
	return listEntryOld;
}
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});