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
			var PyScadaConfig = data;
			$.each(PyScadaConfig.config,function(key){
				PyScadaConfig.config[key]["init"] = true;
			})
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

function PyScadaPlot(){
	var 

	plot = this;
	
	// public functions
	plot.updateData = updateData;
	
	
	

}