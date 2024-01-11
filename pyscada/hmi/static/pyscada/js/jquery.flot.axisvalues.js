/* Flot plugin for showing axis values when the mouse hovers over the plot.
Copyright (c) 2019 Camille Lavayssière.
Licensed under the MIT license.
The plugin supports these options:
	axisvalues: {
		mode: null or "x" or "y" or "xy"
		color: color
        backgroundColor: "#fee",
        opacity: 0.80
	}
Set the mode to one of "x", "y" or "xy". The "x" mode enables a vertical
axisvalues that lets you trace the values on the x axis, "y" enables a
horizontal axisvalues and "xy" enables them both. "color" is the color of the
axisvalues (default is "rgba(170, 0, 0, 0.80)").
The plugin also adds four public methods:
  - setAxisValues( pos )
    Set the position of the axisvalues. Note that this is cleared if the user
    moves the mouse. "pos" is in coordinates of the plot and should be on the
    form { x: xpos, y: ypos } (you can use x2/x3/... if you're using multiple
    axes), which is coincidentally the same format as what you get from a
    "plothover" event. If "pos" is null, the axisvalues is cleared.
  - clearAxisValues()
    Clear the axisvalues.
  - lockAxisValues(pos)
    Cause the axisvalues to lock to the current location, no longer updating if
    the user moves the mouse. Optionally supply a position (passed on to
    setAxisValues()) to move it to.
    Example usage:
	var myFlot = $.plot( $("#graph"), ..., { axisvalues: { mode: "x" } } };
	$("#graph").bind( "plothover", function ( evt, position, item ) {
		if ( item ) {
			// Lock the axisvalues to the data point being hovered
			myFlot.lockAxisValues({
				x: item.datapoint[ 0 ],
				y: item.datapoint[ 1 ]
			});
		} else {
			// Return normal axisvalues operation
			myFlot.unlockAxisValues();
		}
	});
  - unlockAxisValues()
    Free the axisvalues to move again after locking it.
*/

(function ($) {
    var options = {
        axisvalues: {
            mode: null, // one of null, "x", "y" or "xy",
            color: "rgba(170, 0, 0, 0.80)",
            backgroundColor: "#fee",
            opacity: 0.80
        }
    };

    function init(plot) {
        // position of axisvalues in pixels
        var axisvalues = { x: -1, y: -1, locked: false };

        plot.setAxisValues = function setAxisValues(pos) {
            if (!pos) {
                axisvalues.x = -1;
            }else {
                var o = plot.p2c(pos);
                axisvalues.x = Math.max(0, Math.min(o.left, plot.width()));
                axisvalues.y = Math.max(0, Math.min(o.top, plot.height()));
            }

            plot.triggerRedrawOverlay();
        };

        plot.clearAxisValues = plot.setAxisValues; // passes null for pos

        plot.lockAxisValues = function lockAxisValues(pos) {
            if (pos)
                plot.setAxisValues(pos);
            axisvalues.locked = true;
        };

        plot.unlockAxisValues = function unlockAxisValues() {
            axisvalues.locked = false;
        };

        function onMouseOut(e) {
            if (axisvalues.locked)
                return;

            $(".axes-tooltips").hide();

            if (axisvalues.x !== -1) {
                axisvalues.x = -1;
                plot.triggerRedrawOverlay();
            }
        }

        function onMouseMove(e) {
            if (axisvalues.locked)
                return;

            if (plot.getSelection && plot.getSelection()) {
                axisvalues.x = -1; // hide the axisvalues while selecting
                return;
            }

            var offset = plot.offset();
            if (0 <= e.pageX - offset.left && e.pageX - offset.left <= plot.width() && 0 <= e.pageY - offset.top && e.pageY - offset.top <= plot.height()) {
                axisvalues.x = Math.max(0, Math.min(e.pageX - offset.left, plot.width()));
                axisvalues.y = Math.max(0, Math.min(e.pageY - offset.top, plot.height()));
                plot.triggerRedrawOverlay();
            }else {
                axisvalues.x = -1;
            }
        }

        plot.hooks.bindEvents.push(function (plot, eventHolder) {
            if (!plot.getOptions().axisvalues.mode)
                return;

            eventHolder.mouseout(onMouseOut);
            eventHolder.mousemove(onMouseMove);
        });

        plot.hooks.drawOverlay.push(function (plot, ctx) {
            var c = plot.getOptions().axisvalues;
            if (!c.mode)
                return;

            var plotOffset = plot.getPlotOffset();
            var xaxes = plot.getXAxes()
            var yaxes = plot.getYAxes()
            var offset = plot.offset();
            tf = function (value, axis) {
                return value.toFixed(axis.tickDecimals) + ((typeof axis.options.unit != "undefined") ? axis.options.unit : '');
            };

            if (axisvalues.x !== -1) {

                if (c.mode.indexOf("x") !== -1) {
                    for (xaxis in xaxes) {
                        var xaxisplusone = Number(xaxis) + 1;
                        var fontSize = $("#y" + xaxisplusone + "-tooltip").css("font-size")
                        fontSize = fontSize ? +fontSize.replace("px", "") : 13;
                        if (xaxes[xaxis].used && typeof xaxes[xaxis].box !== 'undefined' && typeof xaxes[xaxis].box.padding !== 'undefined' && typeof xaxes[xaxis].box.top !== 'undefined' && typeof xaxes[xaxis].box.height !== 'undefined') {
                            var drawX = Math.floor(axisvalues.x);
                            if (xaxes[xaxis].options.mode == "time") {
                                dG = $.plot.dateGenerator(Number(xaxes[xaxis].c2p(drawX).toFixed(0)), xaxes[xaxis].options)
                                dF = $.plot.formatDate(dG, xaxes[xaxis].options.timeformat, xaxes[xaxis].options.monthNames, xaxes[xaxis].options.dayNames);
                                x_value = dF;
                            }else {
                                x_value = tf(xaxes[xaxis].c2p(drawX), xaxes[xaxis]);
                            }
                            x_length = x_value.includes(":") ? x_value.replace(":", "").length - 1 : x_value.length;
                            if (xaxes[xaxis].position == "top") {
                                $("#x" + xaxisplusone + "-tooltip").html(x_value)
                                    .css({top: offset.top - xaxes[xaxis].box.top - xaxes[xaxis].box.padding, left: offset.left + drawX - fontSize * x_length * 0.8 / 2})
                                    .show();
                            }else if (xaxes[xaxis].position == "bottom") {
                                $("#x" + xaxisplusone + "-tooltip").html(x_value)
                                    .css({top: offset.top + xaxes[xaxis].box.top + xaxes[xaxis].box.padding - xaxes[xaxis].box.height + 2, left: offset.left + drawX - fontSize * x_length * 0.8 / 2})
//                                    .css({top: offset.top + xaxes[xaxis].box.top - xaxes[xaxis].box.height, left: offset.left + drawX})
                                    .show();
                            }
                        }
                    }
                }
                if (c.mode.indexOf("y") !== -1) {
                    for (yaxis in yaxes) {
                        var drawY = Math.floor(axisvalues.y),
                        y_value = tf(yaxes[yaxis].c2p(drawY), yaxes[yaxis]),
                        yaxisplusone = Number(yaxis) + 1;
                        if (yaxes[yaxis].used && typeof yaxes[yaxis].box !== 'undefined' && typeof yaxes[yaxis].box.padding !== 'undefined' && typeof yaxes[yaxis].box.left !== 'undefined' && typeof yaxes[yaxis].box.width !== 'undefined' && $("#y" + yaxisplusone + "-tooltip").length) {
                            if (yaxes[yaxis].position == "left") {
                                $("#y" + yaxisplusone + "-tooltip").html(y_value)
//                                    .css({top: offset.top + drawY - yaxes[yaxis].box.padding, left: offset.left - yaxes[yaxis].box.padding - window.getComputedStyle($("#y" + yaxisplusone + "-tooltip")[0]).width.replace("px", "")})
                                    .css({top: offset.top + drawY - yaxes[yaxis].box.padding + yaxes[yaxis].labelHeight/2, left: offset.left + yaxes[yaxis].box.left - plotOffset.left + ((typeof yaxes[yaxis].options.axisLabel != "undefined") ? yaxes[yaxis].labelHeight : 0)})
                                    .show();
                            }else if (yaxes[yaxis].position == "right") {
                                $("#y" + yaxisplusone + "-tooltip").html(y_value)
//                                    .css({top: offset.top + drawY - yaxes[yaxis].box.padding, left: offset.left + yaxes[yaxis].box.left + yaxes[yaxis].box.padding - yaxes[yaxis].box.width})
                                    .css({top: offset.top + drawY - yaxes[yaxis].box.padding + yaxes[yaxis].labelHeight/2, left: offset.left + yaxes[yaxis].box.left + yaxes[yaxis].box.padding - plotOffset.left})
                                    .show();
                            }
                        }
                    }
                }
            }else {
                //$(".axes-tooltips").hide();
            }
        });

        plot.hooks.shutdown.push(function (plot, eventHolder) {
            eventHolder.unbind("mouseout", onMouseOut);
            eventHolder.unbind("mousemove", onMouseMove);
        });
    }

    $.plot.plugins.push({
        init: init,
        options: options,
        name: 'axisvalues',
        version: '1.0'
    });
})(jQuery);