/*!
 * jquery.flot.gauge v1.1.0 *
 *
 * Flot plugin for rendering gauge charts.
 *
 * Copyright (c) 2015 @toyoty99.
 * Licensed under the MIT license.
 */

/**
 * @module flot.gauge
 */
(function($) {
    /**
     * Logger class
     *
     * @class Logger
     */
    var Logger = (function() {
        /**
         * constructor
         *
         * @class Logger
         * @constructor
         * @param {Object} debugOptions debug options
         */
        var Logger = function(debugOptions) {
            var log;
            // create log function
            if (debugOptions.log) {
                if (window.console && console.log) {
                    if (console.log.bind) {
                        log = console.log.bind(console);
                    } else {
                        log = function() {
                            var text = Array.prototype.join.apply(arguments, [""]);
                            console.log(text);
                        }
                    }
                } else if (debugOptions.alert) {
                    log = function() {
                        var text = Array.prototype.join.apply(arguments, [""]);
                        alert(text);
                    }
                } else {
                    log = function(){};
                }
            } else {
                log = function(){};
            }
            /**
             * log
             *
             * @method log
             * @param {Object} ...obj
             */
            Logger.prototype.log = log;
        }

        /**
         * debug the layout
         *
         * @method debugLayout
         * @param  {Object} context the context of canvas
         * @param  {Number} seriesLength the length of series
         * @param  {Object} layout the layout properties
         */
        Logger.prototype.debugLayout = function(context, seriesLength, layout) {
            context.save();
            context.strokeStyle = "gray";
            context.lineWidth = 1;
            context.strokeRect(0, 0, layout.canvasWidth, layout.canvasHeight);
            for (var i = 0; i < seriesLength; i++) {
                var c = col(layout.columns, i);
                var r = row(layout.columns, i);
                context.strokeRect(
                    layout.margin + layout.cellWidth * c + layout.hMargin * c,
                    layout.margin + layout.cellHeight * r + layout.vMargin * r,
                    layout.cellWidth,
                    layout.cellHeight);
            }
            context.restore();
        }

        /**
         * debug the cell layout
         *
         * @method debugCellLayout
         * @param  {Object} context the context of canvas
         * @param  {Object} gaugeOptions the option of the gauge
         * @param  {Object} layout the layout properties
         * @param  {Object} cellLayout the cell layout properties
         */
        Logger.prototype.debugCellLayout = function(context, gaugeOptions, layout, cellLayout) {
            context.save();
            context.strokeStyle = "gray";
            context.lineWidth = 1;
            // debug label layout
            if (gaugeOptions.label.show) {
                var labelMarginWidth = (cellLayout.cellWidth / 3) + (layout.labelMargin * 2);
                var labelMarginHeight = layout.labelFontSize + (layout.labelMargin * 2);
                var labelWidth = (cellLayout.cellWidth / 3);
                var labelHeight = layout.labelFontSize;
                context.strokeRect(
                    cellLayout.cx - (labelMarginWidth / 2),
                    cellLayout.y + cellLayout.cellMargin + cellLayout.offsetY,
                    labelMarginWidth,
                    labelMarginHeight);
                context.strokeRect(
                    cellLayout.cx - (labelWidth / 2),
                    cellLayout.y + cellLayout.cellMargin + layout.labelMargin + cellLayout.offsetY,
                    labelWidth,
                    labelHeight);
            }
            // debug value layout
            if (gaugeOptions.value.show) {
                var valueMarginWidth = (cellLayout.cellWidth / 3) + (layout.valueMargin * 2);
                var valueMarginHeight = layout.valueFontSize + (layout.valueMargin * 2);
                var valueWidth = (cellLayout.cellWidth / 3);
                var valueHeight = layout.valueFontSize;
                context.strokeRect(
                    cellLayout.cx - (valueMarginWidth / 2),
                    cellLayout.cy - (valueMarginHeight / 2),
                    valueMarginWidth,
                    valueMarginHeight);
                context.strokeRect(
                    cellLayout.cx - (valueWidth / 2),
                    cellLayout.cy - (valueHeight / 2),
                    valueWidth,
                    valueHeight);
            }
            // debug gauge center
            context.strokeRect(cellLayout.cx, cellLayout.cy, 1, 1);
            // debug gauge outer height
            context.strokeRect(
                cellLayout.x + cellLayout.cellMargin,
                cellLayout.y + cellLayout.cellMargin + labelMarginHeight + cellLayout.offsetY,
                cellLayout.cellWidth - (cellLayout.cellMargin * 2),
                layout.gaugeOuterHeight);
            // debug gauge layout
            drawArc(
                context,
                cellLayout.cx,
                cellLayout.cy,
                layout.radius,
                layout.width,
                toRad(gaugeOptions.gauge.startAngle),
                toRad(gaugeOptions.gauge.endAngle),
                context.strokeStyle);
            // debug threshold layout
            if (gaugeOptions.threshold.show) {
                drawArc(
                    context,
                    cellLayout.cx, cellLayout.cy,
                    layout.radius + layout.thresholdWidth,
                    layout.thresholdWidth,
                    toRad(gaugeOptions.gauge.startAngle),
                    toRad(gaugeOptions.gauge.endAngle),
                    context.strokeStyle);
            }
            // debug threshold label layout
            if (gaugeOptions.threshold.label.show) {
                drawArc(
                    context,
                    cellLayout.cx,
                    cellLayout.cy,
                    layout.radius + layout.thresholdWidth + layout.thresholdLabelFontSize + (layout.thresholdLabelMargin * 2),
                    layout.thresholdLabelFontSize + (layout.thresholdLabelMargin * 2),
                    toRad(gaugeOptions.gauge.startAngle),
                    toRad(gaugeOptions.gauge.endAngle),
                    context.strokeStyle);
            }
            context.restore();
        }

        return Logger;
    })();

    /**
     * Gauge class
     *
     * @class Gauge
     */
    var Gauge = (function() {
        /**
         * context of canvas
         *
         * @property context
         * @type Object
         */
        var context;
        /**
         * placeholder of canvas
         *
         * @property placeholder
         * @type Object
         */
        var placeholder;
        /**
         * options of plot
         *
         * @property options
         * @type Object
         */
        var options;
        /**
         * options of gauge
         *
         * @property gaugeOptions
         * @type Object
         */
        var gaugeOptions;
        /**
         * data series
         *
         * @property series
         * @type Array
         */
        var series;
        /**
         * logger
         *
         * @property logger
         * @type Object
         */
        var logger;

        /**
         * constructor
         *
         * @class Gauge
         * @constructor
         * @param  {Object} gaugeOptions gauge options
         */
        var Gauge = function(plot, ctx) {
            context = ctx;
            placeholder = plot.getPlaceholder();
            options = plot.getOptions();
            gaugeOptions = options.series.gauges;
            series = plot.getData();
            logger = getLogger(gaugeOptions.debug);
        }

        /**
         * calculate layout
         *
         * @method calculateLayout
         * @return the calculated layout properties
         */
        Gauge.prototype.calculateLayout = function() {
            logger.log("flot.gauge.calculateLayout");
            var canvasWidth = placeholder.width();
            var canvasHeight = placeholder.height();
            logger.log("canvasWidth=", canvasWidth);
            logger.log("canvasHeight=", canvasHeight);

            // calculate cell size
            var columns = Math.min(series.length, gaugeOptions.layout.columns);
            var rows = Math.ceil(series.length / columns);
            logger.log("columns=", columns);
            logger.log("rows=", rows);

            var margin = gaugeOptions.layout.margin;
            var hMargin = gaugeOptions.layout.hMargin;
            var vMargin = gaugeOptions.layout.vMargin;
            var cellWidth = (canvasWidth - (margin * 2) - (hMargin * (columns - 1))) / columns;
            var cellHeight = (canvasHeight - (margin * 2) - (vMargin * (rows - 1))) / rows;
            if (gaugeOptions.layout.square) {
                var cell = Math.min(cellWidth, cellHeight);
                cellWidth = cell;
                cellHeight = cell;
            }
            logger.log("cellWidth=", cellWidth);
            logger.log("cellHeight=", cellHeight);

            // calculate 'auto' values
            calculateAutoValues(gaugeOptions, cellWidth);

            // calculate maximum radius
            var cellMargin = gaugeOptions.cell.margin;
            var labelMargin = 0;
            var labelFontSize = 0;
            if (gaugeOptions.label.show) {
                labelMargin = gaugeOptions.label.margin;
                labelFontSize = gaugeOptions.label.font.size;
            }
            var valueMargin = 0;
            var valueFontSize = 0;
            if (gaugeOptions.value.show) {
                valueMargin = gaugeOptions.value.margin;
                valueFontSize = gaugeOptions.value.font.size;
            }
            var thresholdWidth = 0;
            if (gaugeOptions.threshold.show) {
                thresholdWidth = gaugeOptions.threshold.width;
            }
            var thresholdLabelMargin = 0;
            var thresholdLabelFontSize = 0;
            if (gaugeOptions.threshold.label.show) {
                thresholdLabelMargin = gaugeOptions.threshold.label.margin;
                thresholdLabelFontSize = gaugeOptions.threshold.label.font.size;
            }

            var maxRadiusH = (cellWidth / 2) - cellMargin - thresholdWidth - (thresholdLabelMargin * 2) - thresholdLabelFontSize;

            var startAngle = gaugeOptions.gauge.startAngle;
            var endAngle = gaugeOptions.gauge.endAngle;
            var dAngle = (endAngle - startAngle) / 100;
            var heightRatioV = -1;
            for (var a = startAngle; a < endAngle; a += dAngle) {
                heightRatioV = Math.max(heightRatioV, Math.sin(toRad(a)));
            }
            heightRatioV = Math.max(heightRatioV, Math.sin(toRad(endAngle)));
            var outerRadiusV = (cellHeight - (cellMargin * 2) - (labelMargin * 2) - labelFontSize) / (1 + heightRatioV);
            if (outerRadiusV * heightRatioV < valueMargin + (valueFontSize / 2)) {
                outerRadiusV = cellHeight - (cellMargin * 2) - (labelMargin * 2) - labelFontSize - valueMargin - (valueFontSize / 2);
            }
            var maxRadiusV = outerRadiusV - (thresholdLabelMargin * 2) - thresholdLabelFontSize - thresholdWidth;

            var radius = Math.min(maxRadiusH, maxRadiusV);
            logger.log("radius=", radius);

            var width = gaugeOptions.gauge.width;
            if (width >= radius) {
                width = Math.max(3, radius / 3);
            }
            logger.log("width=", width);

            var outerRadius = (thresholdLabelMargin * 2) + thresholdLabelFontSize + thresholdWidth + radius;
            var gaugeOuterHeight = Math.max(outerRadius * (1 + heightRatioV), outerRadius + valueMargin + (valueFontSize / 2));

            return {
                canvasWidth: canvasWidth,
                canvasHeight: canvasHeight,
                margin: margin,
                hMargin: hMargin,
                vMargin: vMargin,
                columns: columns,
                rows: rows,
                cellWidth: cellWidth,
                cellHeight: cellHeight,
                cellMargin: cellMargin,
                labelMargin: labelMargin,
                labelFontSize: labelFontSize,
                valueMargin: valueMargin,
                valueFontSize: valueFontSize,
                width: width,
                radius: radius,
                thresholdWidth: thresholdWidth,
                thresholdLabelMargin: thresholdLabelMargin,
                thresholdLabelFontSize: thresholdLabelFontSize,
                gaugeOuterHeight: gaugeOuterHeight
            };
        }

        /**
         * calculate the values which are set as 'auto'
         *
         * @method calculateAutoValues
         * @param  {Object} gaugeOptionsi the options of the gauge
         * @param  {Number} cellWidth the width of cell
         */
        function calculateAutoValues(gaugeOptionsi, cellWidth) {
            logger.log("flot.gauge.calculateAutoValues");
            if (gaugeOptionsi.gauge.width === "auto") {
                gaugeOptionsi.gauge.width = Math.max(5, cellWidth / 8);
            }
            if (gaugeOptionsi.label.margin === "auto") {
                gaugeOptionsi.label.margin = Math.max(1, cellWidth / 20);
            }
            if (gaugeOptionsi.label.font.size === "auto") {
                gaugeOptionsi.label.font.size = Math.max(5, cellWidth / 8);
            }
            if (gaugeOptionsi.value.margin === "auto") {
                gaugeOptionsi.value.margin = Math.max(1, cellWidth / 30);
            }
            if (gaugeOptionsi.value.font.size === "auto") {
                gaugeOptionsi.value.font.size = Math.max(5, cellWidth / 9);
            }
            if (gaugeOptionsi.threshold.width === "auto") {
                gaugeOptionsi.threshold.width = Math.max(3, cellWidth / 100);
            }
            if (gaugeOptionsi.threshold.label.margin === "auto") {
                gaugeOptionsi.threshold.label.margin = Math.max(3, cellWidth / 40);
            }
            if (gaugeOptionsi.threshold.label.font.size === "auto") {
                gaugeOptionsi.threshold.label.font.size = Math.max(5, cellWidth / 15);
            }
            logger.log("gaugeOptions=", gaugeOptionsi);
        }
        Gauge.prototype.calculateAutoValues = calculateAutoValues;

        /**
         * calculate the layout of the cell inside
         *
         * @method calculateCellLayout
         * @param  {Object} gaugeOptionsi the options of the gauge
         * @param  {Number} cellWidth the width of cell
         * @param  {Number} i the index of the series
         * @return the calculated cell layout properties
         */
        Gauge.prototype.calculateCellLayout = function(gaugeOptionsi, layout, i) {
            logger.log("flot.gauge.calculateCellLayout");
            // calculate top, left and center
            var c = col(layout.columns, i);
            var r = row(layout.columns, i);
            var x = layout.margin + (layout.cellWidth + layout.hMargin) * c;
            var y = layout.margin + (layout.cellHeight + layout.vMargin) * r;
            var cx = x + (layout.cellWidth / 2);
            var cy = y + layout.cellMargin + (layout.labelMargin * 2) + layout.labelFontSize + layout.thresholdWidth
                        + layout.thresholdLabelFontSize + (layout.thresholdLabelMargin * 2) + layout.radius;
            var blank = layout.cellHeight - (layout.cellMargin * 2) - (layout.labelMargin * 2) - layout.labelFontSize - layout.gaugeOuterHeight;
            var offsetY = 0;
            if (gaugeOptionsi.cell.vAlign === "middle") {
                offsetY = (blank / 2);
            } else if (gaugeOptionsi.cell.vAlign === "bottom") {
                offsetY = blank;
            }
            cy += offsetY;

            return {
                col: c,
                row: r,
                x: x,
                y: y,
                offsetY: offsetY,
                cellWidth: layout.cellWidth,
                cellHeight: layout.cellHeight,
                cellMargin: layout.cellMargin,
                cx: cx,
                cy: cy
            }
        }

        /**
         * draw the background of chart
         *
         * @method drawBackground
         * @param  {Object} layout the layout properties
         */
        Gauge.prototype.drawBackground = function(layout) {
            logger.log("flot.gauge.drawBackground");
            if (!gaugeOptions.frame.show) {
                return;
            }
            context.save();
            context.strokeStyle = options.grid.borderColor;
            context.lineWidth = options.grid.borderWidth;
            context.strokeRect(0, 0, layout.canvasWidth, layout.canvasHeight);
            if (options.grid.backgroundColor) {
                context.fillStyle = options.grid.backgroundColor;
                context.fillRect(0, 0, layout.canvasWidth, layout.canvasHeight);
            }
            context.restore();
        }

        /**
         * draw the background of cell
         *
         * @method drawCellBackground
         * @param  {Object} gaugeOptionsi the options of the gauge
         * @param  {Object} cellLayout the cell layout properties
         */
        Gauge.prototype.drawCellBackground = function(gaugeOptionsi, cellLayout) {
            logger.log("flot.gauge.drawCellBackground");
            context.save();
            if (gaugeOptionsi.cell.border && gaugeOptionsi.cell.border.show && gaugeOptionsi.cell.border.color && gaugeOptionsi.cell.border.width) {
                context.strokeStyle = gaugeOptionsi.cell.border.color;
                context.lineWidth = gaugeOptionsi.cell.border.width;
                context.strokeRect(cellLayout.x, cellLayout.y, cellLayout.cellWidth, cellLayout.cellHeight);
            }
            if (gaugeOptionsi.cell.background && gaugeOptionsi.cell.background.color) {
                context.fillStyle = gaugeOptionsi.cell.background.color;
                context.fillRect(cellLayout.x, cellLayout.y, cellLayout.cellWidth, cellLayout.cellHeight);
            }
            context.restore();
        }

        /**
         * draw the gauge
         *
         * @method drawGauge
         * @param  {Object} gaugeOptionsi the options of the gauge
         * @param  {Object} layout the layout properties
         * @param  {Object} cellLayout the cell layout properties
         * @param  {String} label the label of data
         * @param  {Number} data the value of the gauge
         */
        Gauge.prototype.drawGauge = function(gaugeOptionsi, layout, cellLayout, label, data) {
            logger.log("flot.gauge.drawGauge");

            var blur = gaugeOptionsi.gauge.shadow.show ? gaugeOptionsi.gauge.shadow.blur : 0;
            logger.log("blur=", blur);

            // draw gauge frame
            drawArcWithShadow(
                cellLayout.cx, // center x
                cellLayout.cy, // center y
                layout.radius,
                layout.width,
                toRad(gaugeOptionsi.gauge.startAngle),
                toRad(gaugeOptionsi.gauge.endAngle),
                gaugeOptionsi.gauge.border.color,      // line color
                gaugeOptionsi.gauge.border.width,      // line width
                gaugeOptionsi.gauge.background.color,  // fill color
                blur);

            // draw gauge
            var c1 = getColor(gaugeOptionsi, data);
            var a2 = calculateAngle(gaugeOptionsi, layout, data);
            drawArcWithShadow(
                cellLayout.cx, // center x
                cellLayout.cy, // center y
                layout.radius - 1,
                layout.width - 2,
                toRad(gaugeOptionsi.gauge.startAngle),
                toRad(a2),
                c1,           // line color
                1,            // line width
                c1,           // fill color
                blur);
        }

        /**
         * decide the color of the data from the threshold options
         *
         * @method getColor
         * @private
         * @param  {Object} gaugeOptionsi the options of the gauge
         * @param  {Number} data the value of the gauge
         */
        function getColor(gaugeOptionsi, data) {
            var color;
            for (var i = 0; i < gaugeOptionsi.threshold.values.length; i++) {
                var threshold = gaugeOptionsi.threshold.values[i];
                color = threshold.color;
                if (data <= threshold.value) {
                    break;
                }
            }
            return color;
        }

        /**
         * calculate the angle of the data
         *
         * @method calculateAngle
         * @private
         * @param  {Object} gaugeOptionsi the options of the gauge
         * @param  {Object} layout the layout properties
         * @param  {Number} data the value of the gauge
         */
        function calculateAngle(gaugeOptionsi, layout, data) {
            var a =
                gaugeOptionsi.gauge.startAngle
                    + (gaugeOptionsi.gauge.endAngle - gaugeOptionsi.gauge.startAngle)
                        * ((data - gaugeOptionsi.gauge.min) / (gaugeOptionsi.gauge.max - gaugeOptionsi.gauge.min));

            if (a < gaugeOptionsi.gauge.startAngle) {
                a = gaugeOptionsi.gauge.startAngle;
            } else if (a > gaugeOptionsi.gauge.endAngle) {
                a = gaugeOptionsi.gauge.endAngle;
            }
            return a;
        }

        /**
         * draw the arc of the threshold
         *
         * @method drawThreshold
         * @param  {Object} gaugeOptionsi the options of the gauge
         * @param  {Object} layout the layout properties
         * @param  {Object} cellLayout the cell layout properties
         */
        Gauge.prototype.drawThreshold = function(gaugeOptionsi, layout, cellLayout) {
            logger.log("flot.gauge.drawThreshold");
            var a1 = gaugeOptionsi.gauge.startAngle;
            for (var i = 0; i < gaugeOptionsi.threshold.values.length; i++) {
                var threshold = gaugeOptionsi.threshold.values[i];
                c1 = threshold.color;
                a2 = calculateAngle(gaugeOptionsi, layout, threshold.value);
                drawArc(
                    context,
                    cellLayout.cx, // center x
                    cellLayout.cy, // center y
                    layout.radius + layout.thresholdWidth,
                    layout.thresholdWidth - 2,
                    toRad(a1),
                    toRad(a2),
                    c1,           // line color
                    1,            // line width
                    c1);          // fill color
                a1 = a2;
            }
        }

        /**
         * draw an arc with a shadow
         *
         * @method drawArcWithShadow
         * @private
         * @param  {Number} cx the x position of the center
         * @param  {Number} cy the y position of the center
         * @param  {Number} r the radius of an arc
         * @param  {Number} w the width of an arc
         * @param  {Number} rd1 the start angle of an arc in radians
         * @param  {Number} rd2 the end angle of an arc in radians
         * @param  {String} lc the color of a line
         * @param  {Number} lw the widht of a line
         * @param  {String} fc the fill color  of an arc
         * @param  {Number} blur the shdow blur
         */
        function drawArcWithShadow(cx, cy, r, w, rd1, rd2, lc, lw, fc, blur) {
            if (rd1 === rd2) {
                return;
            }
            context.save();

            drawArc(context, cx, cy, r, w, rd1, rd2, lc, lw, fc);

            if (blur) {
                drawArc(context, cx, cy, r, w, rd1, rd2);
                context.clip();
                context.shadowOffsetX = 0;
                context.shadowOffsetY = 0;
                context.shadowBlur = 10;
                context.shadowColor = "gray";
                drawArc(context, cx, cy, r + 1, w + 2, rd1, rd2, lc, 1);
            }
            context.restore();
        }

        /**
         * draw the label of the gauge
         *
         * @method drawLable
         * @param  {Object} gaugeOptionsi the options of the gauge
         * @param  {Object} layout the layout properties
         * @param  {Object} cellLayout the cell layout properties
         * @param  {Number} i the index of the series
         * @param  {Object} item the item of the series
         */
        Gauge.prototype.drawLable = function(gaugeOptionsi, layout, cellLayout, i, item) {
            logger.log("flot.gauge.drawLable");
            drawText(
                cellLayout.cx,
                cellLayout.y + cellLayout.cellMargin + layout.labelMargin + cellLayout.offsetY,
                "flotGagueLabel" + i,
                gaugeOptionsi.label.formatter ? gaugeOptionsi.label.formatter(item.label, item.data[0][1]) : text,
                gaugeOptionsi.label);
        }

        /**
         * draw the value of the gauge
         *
         * @method drawValue
         * @param  {Object} gaugeOptionsi the options of the gauge
         * @param  {Object} layout the layout properties
         * @param  {Object} cellLayout the cell layout properties
         * @param  {Number} i the index of the series
         * @param  {Object} item the item of the series
         */
        Gauge.prototype.drawValue = function(gaugeOptionsi, layout, cellLayout, i, item) {
            logger.log("flot.gauge.drawValue");
            drawText(
                cellLayout.cx,
                cellLayout.cy - (gaugeOptionsi.value.font.size / 2),
                "flotGagueValue" + i,
                gaugeOptionsi.value.formatter ? gaugeOptionsi.value.formatter(item.label, item.data[0][1]) : text,
                gaugeOptionsi.value);
        }

        /**
         * draw the values of the threshold
         *
         * @method drawThresholdValues
         * @param  {Object} gaugeOptionsi the options of the gauge
         * @param  {Object} layout the layout properties
         * @param  {Object} cellLayout the cell layout properties
         * @param  {Number} i the index of the series
         */
        Gauge.prototype.drawThresholdValues = function(gaugeOptionsi, layout, cellLayout, i) {
            logger.log("flot.gauge.drawThresholdValues");
            // min, max
            drawThresholdValue(gaugeOptionsi, layout, cellLayout, "Min" + i, gaugeOptionsi.gauge.min, gaugeOptionsi.gauge.startAngle);
            drawThresholdValue(gaugeOptionsi, layout, cellLayout, "Max" + i, gaugeOptionsi.gauge.max, gaugeOptionsi.gauge.endAngle);
            // threshold values
            for (var j = 0; j < gaugeOptionsi.threshold.values.length; j++) {
                var threshold = gaugeOptionsi.threshold.values[j];
                if (threshold.value > gaugeOptionsi.gauge.min && threshold.value < gaugeOptionsi.gauge.max) {
                    var a = calculateAngle(gaugeOptionsi, layout, threshold.value);
                    drawThresholdValue(gaugeOptionsi, layout, cellLayout, i + "_" + j, threshold.value, a);
                }
            }
        }

        /**
         * draw the value of the threshold
         *
         * @method drawThresholdValue
         * @param  {Object} gaugeOptionsi the options of the gauge
         * @param  {Object} layout the layout properties
         * @param  {Object} cellLayout the cell layout properties
         * @param  {Number} i the index of the series
         * @param  {Number} value the value of the threshold
         * @param  {Number} a the angle of the value drawn
         */
        function drawThresholdValue(gaugeOptionsi, layout, cellLayout, i, value, a) {
            drawText(
                cellLayout.cx
                    + ((layout.thresholdLabelMargin + (layout.thresholdLabelFontSize / 2) + layout.radius)
                        * Math.cos(toRad(a))),
                cellLayout.cy
                    + ((layout.thresholdLabelMargin + (layout.thresholdLabelFontSize / 2) + layout.radius)
                        * Math.sin(toRad(a))),
                "flotGagueThresholdValue" + i,
                gaugeOptionsi.threshold.label.formatter ? gaugeOptionsi.threshold.label.formatter(value) : value,
                gaugeOptionsi.threshold.label,
                a);
        }

        /**
         * draw a text
         *
         * the textOptions is assumed as follows:
         *
         *   textOptions: {
         *       background: {
         *           color: null,
         *           opacity: 0
         *       },
         *       font: {
         *           size: "auto"
         *           family: "\"ＭＳ ゴシック\",sans-serif"
         *       },
         *       color: null
         *   }
         *
         * @method drawText
         * @private
         * @param  {Number} x the x position of the text drawn (left top)
         * @param  {Number} y the y position of the text drawn (left top)
         * @param  {String} id the id of the dom element
         * @param  {String} text the text drawn
         * @param  {Object} textOptions the option of the text
         * @param  {Number} [a] the angle of the value drawn
         */
        function drawText(x, y, id, text, textOptions, a) {
            var span = $(placeholder).find("#" + id);
            var exists = span.length;
            if (!exists) {
                span = $("<span></span>")
                span.attr("id", id);
                span.css("position", "absolute");
                span.css("top", y + "px");
                if (textOptions.font.size) {
                    span.css("font-size", textOptions.font.size + "px");
                }
                if (textOptions.font.family) {
                    span.css("font-family", textOptions.font.family);
                }
                if (textOptions.color) {
                    span.css("color", textOptions.color);
                }
                if (textOptions.background.color) {
                    span.css("background-color", textOptions.background.color);
                }
                if (textOptions.background.opacity) {
                    span.css("opacity", textOptions.background.opacity);
                }
                placeholder.append(span);
            }
            span.text(text);
            // after append, readjust the left position
            span.css("left", x + "px"); // for redraw, resetting the left position is needed here
            span.css("left", (parseInt(span.css("left")) - (span.width()/ 2)) + "px");

            // at last, set angle
            if (!exists && a) {
                span.css("top", (parseInt(span.css("top")) - (span.height()/ 2)) + "px");
                span.css("transform", "rotate(" + ((180 * a) + 90) + "deg)"); // not supported for ie8
            }
        }

        return Gauge;
    })();
    /**
     * get a instance of Logger
     *
     * @method  getLogger
     * @for flot.gauge
     * @private
     * @param  {Object} debugOptions the options of debug
     */
    function getLogger(debugOptions) {
        return typeof Logger !== "undefined" ? new Logger(debugOptions) : null;
    }

    /**
     * calculate the index of columns for the specified data
     *
     * @method col
     * @for flot.gauge
     * @param  {Number} columns the number of columns
     * @param  {Number} i       the index of the series
     * @return the index of columns
     */
    function col(columns, i) {
        return i % columns;
    }

    /**
     * calculate the index of rows for the specified data
     *
     * @method row
     * @for flot.gauge
     * @param  {Number} columns the number of rows
     * @param  {Number} i       the index of the series
     * @return the index of rows
     */
    function row(columns, i) {
        return Math.floor(i / columns);
    }

    /**
     * calculate the angle in radians
     *
     * internally, use a number without PI (0 - 2).
     * so, in this function, multiply PI
     *
     * @method toRad
     * @for flot.gauge
     * @param  {Number} a the number of angle without PI
     * @return the angle in radians
     */
    function toRad(a) {
        return a * Math.PI;
    }

    /**
     * draw an arc
     *
     * @method drawArc
     * @for flot.gauge
     * @param  {Object} context the context of canvas
     * @param  {Number} cx the x position of the center
     * @param  {Number} cy the y position of the center
     * @param  {Number} r the radius of an arc
     * @param  {Number} w the width of an arc
     * @param  {Number} rd1 the start angle of an arc in radians
     * @param  {Number} rd2 the end angle of an arc in radians
     * @param  {String} lc the color of a line
     * @param  {Number} lw the widht of a line
     * @param  {String} fc the fill color  of an arc
     */
    function drawArc(context, cx, cy, r, w, rd1, rd2, lc, lw, fc) {
        if (rd1 === rd2) {
            return;
        }
        var counterClockwise = false;
        context.save();
        context.beginPath();
        context.arc(cx, cy, r, rd1, rd2, counterClockwise);
        context.lineTo(cx + (r - w) * Math.cos(rd2),
                       cy + (r - w) * Math.sin(rd2));
        context.arc(cx, cy, r - w, rd2, rd1, !counterClockwise);
        context.closePath();
        if (lw) {
            context.lineWidth = lw;
        }
        if (lc) {
            context.strokeStyle = lc;
            context.stroke();
        }
        if (fc) {
            context.fillStyle = fc;
            context.fill();
        }
        context.restore();
    }

    /**
     * initialize plugin
     *
     * @method init
     * @for flot.gauge
     * @private
     * @param  {Object} plot a instance of plot
     */
    function init (plot) {
        // add processOptions hook
        plot.hooks.processOptions.push(function(plot, options) {
            var logger = getLogger(options.series.gauges.debug);

            logger.log("flot.gauge.processOptions");
            logger.log("options=", options);

            // turn 'grid' and 'legend' off
            if (options.series.gauges.show) {
                options.grid.show = false;
                options.legend.show = false;
            }

            // sort threshold
            var thresholds = options.series.gauges.threshold.values;
            logger.log("thresholds=", thresholds);
            thresholds.sort(function(a, b) {
                if (a.value < b.value) {
                    return -1;
                } else if (a.value > b.value) {
                    return 1;
                } else {
                    return 0;
                }
            });
            logger.log("thresholds(sorted)=", thresholds);

            logger.log("options=", options);
        });

        // add draw hook
        plot.hooks.draw.push(function(plot, context) {
            var options = plot.getOptions();
            var gaugeOptions = options.series.gauges;

            var logger = getLogger(gaugeOptions.debug);
            logger.log("flot.gauge.draw");

            if (!gaugeOptions.show) {
                return;
            }

            var series = plot.getData();
            logger.log("series=", series);
            if (!series || !series.length) {
                return; // if no series were passed
            }

            var gauge = new Gauge(plot, context);

            // calculate layout
            var layout = gauge.calculateLayout();
            logger.log("layout=", layout);
            // debug layout
            if (gaugeOptions.debug.layout) {
                logger.debugLayout(context, series.length, layout);
            }

            // draw background
            gauge.drawBackground(layout)

            // draw cells (label, gauge, value, threshold)
            for (var i = 0; i < series.length; i++) {
                var item = series[i];
                logger.log("item[" + i + "]=", item);
                var gaugeOptionsi = $.extend({}, gaugeOptions, item.gauges);
                if (item.gauges) {
                    // re-calculate 'auto' values
                    gauge.calculateAutoValues(gaugeOptionsi, layout.cellWidth);
                }
                logger.log("gaugeOptions[" + i + "]=", gaugeOptionsi);
                // calculate cell layout
                var cellLayout = gauge.calculateCellLayout(gaugeOptionsi, layout, i);
                logger.log("cellLayout=", cellLayout);
                // draw cell background
                gauge.drawCellBackground(gaugeOptionsi, cellLayout)
                // debug layout
                if (gaugeOptionsi.debug.layout) {
                    logger.debugCellLayout(context, gaugeOptionsi, layout, cellLayout);
                }
                // draw label
                if (gaugeOptionsi.label.show) {
                    gauge.drawLable(gaugeOptionsi, layout, cellLayout, i, item);
                }
                // draw gauge
                gauge.drawGauge(gaugeOptionsi, layout, cellLayout, item.label, item.data[0][1]);
                // draw threshold
                if (gaugeOptionsi.threshold.show) {
                    gauge.drawThreshold(gaugeOptionsi, layout, cellLayout);
                }
                if (gaugeOptionsi.threshold.label.show) {
                    gauge.drawThresholdValues(gaugeOptionsi, layout, cellLayout, i)
                }
                // draw value
                if (gaugeOptionsi.value.show) {
                    gauge.drawValue(gaugeOptionsi, layout, cellLayout, i, item);
                }
            }
        });
    }

    /**
     * [defaults description]
     *
     * @property defaults
     * @type {Object}
     */
    var defaults = {
        series: {
            gauges: {
                debug: {
                    log: false,
                    layout: false,
                    alert: false
                },
                show: false,
                layout: {
                    margin: 5,
                    columns: 3,
                    hMargin: 5,
                    vMargin: 5,
                    square: false
                },
                frame: {
                    show: true
                },
                cell: {
                    background: {
                        color: null
                    },
                    border: {
                        show: true,
                        color: "black",
                        width: 1
                    },
                    margin: 5,
                    vAlign: "middle" // 'top' or 'middle' or 'bottom'
                },
                gauge: {
                    width: "auto", // a specified number, or 'auto'
                    startAngle: 0.9, // 0 - 2 factor of the radians
                    endAngle: 2.1, // 0 - 2 factor of the radians
                    min: 0,
                    max: 100,
                    background: {
                        color: "white"
                    },
                    border: {
                        color: "lightgray",
                        width: 2
                    },
                    shadow: {
                        show: true,
                        blur: 5
                    }
                },
                label: {
                    show: true,
                    margin: "auto", // a specified number, or 'auto'
                    background: {
                        color: null,
                        opacity: 0
                    },
                    font: {
                        size: "auto", // a specified number, or 'auto'
                        family: "sans-serif"
                    },
                    color: null,
                    formatter: function(label, value) {
                        return label;
                    }
                },
                value: {
                    show: true,
                    margin: "auto", // a specified number, or 'auto'
                    background: {
                        color: null,
                        opacity: 0
                    },
                    font: {
                        size: "auto", // a specified number, or 'auto'
                        family: "sans-serif"
                    },
                    color: null,
                    formatter: function(label, value) {
                        return parseInt(value);
                    }
                },
                threshold: {
                    show: true,
                    width: "auto", // a specified number, or 'auto'
                    label: {
                        show: true,
                        margin: "auto", // a specified number, or 'auto'
                        background: {
                            color: null,
                            opacity: 0
                        },
                        font: {
                            size: "auto", // a specified number, or 'auto'
                            family: ",sans-serif"
                        },
                        color: null,
                        formatter: function(value) {
                            return value;
                        }
                    },
                    values: [
                        {
                            value: 50,
                            color: "lightgreen"
                        }, {
                            value: 80,
                            color: "yellow"
                        }, {
                            value: 100,
                            color: "red"
                        }
                    ]
                }
            }
        }
    };

    // register the gauge plugin
    $.plot.plugins.push({
        init: init,
        options: defaults,
        name: "gauge",
        version: "1.1.0"
    });

})(jQuery);
