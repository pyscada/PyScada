function PyScadaControlItemDisplayValueTransformDataMin(key, val, control_item_id, display_value_option_id, transform_data_id) {
  var variable_id = get_config_from_hidden_config('controlitem', 'display-value-options', displayvalueoption_id, 'variable');
  if (DATA[variable_id] == undefined) {
    console.log("PyScada HMI : PyScadaControlItemDisplayValueTransformDataMin : " + variable_id + " not in DATA. ")
    return val;
  }
  var result = null;
  var data = sliceDATAusingTimestamps(variable_id);
  for (d in data) {
    if (result == null) {result = data[d][1]}
    else{result = Math.min(result, data[d][1])}
  }
  return result;
}

function PyScadaControlItemDisplayValueTransformDataMax(key, val, control_item_id, display_value_option_id, transform_data_id) {
  var variable_id = get_config_from_hidden_config('controlitem', 'display-value-options', displayvalueoption_id, 'variable');
  if (DATA[variable_id] == undefined) {
    console.log("PyScada HMI : PyScadaControlItemDisplayValueTransformDataMax : " + variable_id + " not in DATA. ")
    return val;
  }
  var result = null;
  var data = sliceDATAusingTimestamps(variable_id);
  for (d in data) {
    if (result == null) {result = data[d][1]}
    else{result = Math.max(result, data[d][1])}
  }
  return result;
}

function PyScadaControlItemDisplayValueTransformDataTotal(key, val, control_item_id, display_value_option_id, transform_data_id) {
  var variable_id = get_config_from_hidden_config('controlitem', 'display-value-options', displayvalueoption_id, 'variable');
  if (DATA[variable_id] == undefined) {
    console.log("PyScada HMI : PyScadaControlItemDisplayValueTransformDataTotal : " + variable_id + " not in DATA. ")
    return val;
  }
  var result = 0;
  var data = sliceDATAusingTimestamps(variable_id);
  for (d in data) {
    result += data[d][1]
  }
  return result;
}

function PyScadaControlItemDisplayValueTransformDataDifference(key, val, control_item_id, display_value_option_id, transform_data_id) {
  var variable_id = get_config_from_hidden_config('controlitem', 'display-value-options', displayvalueoption_id, 'variable');
  if (DATA[variable_id] == undefined) {
    console.log("PyScada HMI : PyScadaControlItemDisplayValueTransformDataDifference : " + variable_id + " not in DATA. ")
    return val;
  }
  var result = null;
  var data = sliceDATAusingTimestamps(variable_id);
  if (data.length > 0) {
    result = data[data.length - 1][1] - data[0][1]
  }
  return result;
}

function PyScadaControlItemDisplayValueTransformDataDifferencePercent(key, val, control_item_id, display_value_option_id, transform_data_id) {
  var variable_id = get_config_from_hidden_config('controlitem', 'display-value-options', displayvalueoption_id, 'variable');
  if (DATA[variable_id] == undefined) {
    console.log("PyScada HMI : PyScadaControlItemDisplayValueTransformDataDifferencePercent : " + variable_id + " not in DATA. ")
    return val;
  }
  var result = null;
  var data = sliceDATAusingTimestamps(variable_id);
  if (data.length > 0) {
    result = data[data.length - 1][1] - data[0][1]
    result = result / Math.abs(data[0][1] * 100)
  }
  return result;
}

function PyScadaControlItemDisplayValueTransformDataDelta(key, val, control_item_id, display_value_option_id, transform_data_id) {
  var variable_id = get_config_from_hidden_config('controlitem', 'display-value-options', displayvalueoption_id, 'variable');
  if (DATA[variable_id] == undefined) {
    console.log("PyScada HMI : PyScadaControlItemDisplayValueTransformDataDelta : " + variable_id + " not in DATA. ")
    return val;
  }
  var result = 0;
  var prev = null;
  var data = sliceDATAusingTimestamps(variable_id);
  for (d in data) {
    if (prev != null && data[d][1] - prev > 0) {
      result += data[d][1] - prev;
    }
    prev = data[d][1];
  }
  return result;
}

function PyScadaControlItemDisplayValueTransformDataMean(key, val, control_item_id, display_value_option_id, transform_data_id) {
  var variable_id = get_config_from_hidden_config('controlitem', 'display-value-options', displayvalueoption_id, 'variable');
  if (DATA[variable_id] == undefined) {
    console.log("PyScada HMI : PyScadaControlItemDisplayValueTransformDataMean : " + variable_id + " not in DATA. ")
    return val;
  }
  var data = sliceDATAusingTimestamps(variable_id);
  if (data.length == 0) {return null;}
  var result = 0;
  for (d in data) {
    result += data[d][1]
  }
  return result / data.length;
}

function PyScadaControlItemDisplayValueTransformDataFirst(key, val, control_item_id, display_value_option_id, transform_data_id) {
  var variable_id = get_config_from_hidden_config('controlitem', 'display-value-options', displayvalueoption_id, 'variable');
  if (DATA[variable_id] == undefined) {
    console.log("PyScada HMI : PyScadaControlItemDisplayValueTransformDataFirst : " + variable_id + " not in DATA. ")
    return val;
  }
  var data = sliceDATAusingTimestamps(variable_id);
  if (data.length == 0) {return null;}
  return data[0][1];
}

function PyScadaControlItemDisplayValueTransformDataCount(key, val, control_item_id, display_value_option_id, transform_data_id) {
  var variable_id = get_config_from_hidden_config('controlitem', 'display-value-options', displayvalueoption_id, 'variable');
  if (DATA[variable_id] == undefined) {
    console.log("PyScada HMI : PyScadaControlItemDisplayValueTransformDataCount : " + variable_id + " not in DATA. ")
    return val;
  }
  var result = 0;
  var data = sliceDATAusingTimestamps(variable_id);
  for (d in data) {
    result += 1;
  }
  return result;
}

function PyScadaControlItemDisplayValueTransformDataCountValue(key, val, control_item_id, display_value_option_id, transform_data_id) {
  var variable_id = get_config_from_hidden_config('controlitem', 'display-value-options', displayvalueoption_id, 'variable');
  if (DATA[variable_id] == undefined) {
    console.log("PyScada HMI : PyScadaControlItemDisplayValueTransformDataCountValue : " + variable_id + " not in DATA. ")
    return val;
  }
  var value = get_config_from_hidden_config('transformdatacountvalue', 'display-value-option', displayvalueoption_id, 'value');
  var result = 0;
  var data = sliceDATAusingTimestamps(variable_id);
  for (d in data) {
    if (data[d][1] == value) {
      result += 1;
    }
  }
  return result;
}

function PyScadaControlItemDisplayValueTransformDataRange(key, val, control_item_id, display_value_option_id, transform_data_id) {
  var variable_id = get_config_from_hidden_config('controlitem', 'display-value-options', displayvalueoption_id, 'variable');
  if (DATA[variable_id] == undefined) {
    console.log("PyScada HMI : PyScadaControlItemDisplayValueTransformDataRange : " + variable_id + " not in DATA. ")
    return val;
  }
  var min = null;
  var max = null;
  var data = sliceDATAusingTimestamps(variable_id);
  for (d in data) {
    if (min == null) {
      min = data[d][1];
      max = data[d][1];
    }
    else{
      min = Math.min(min, data[d][1]);
      max = Math.max(max, data[d][1]);
    }
  }
  return max - min;
}

function PyScadaControlItemDisplayValueTransformDataStep(key, val, control_item_id, display_value_option_id, transform_data_id) {
  var variable_id = get_config_from_hidden_config('controlitem', 'display-value-options', displayvalueoption_id, 'variable');
  if (DATA[variable_id] == undefined) {
    console.log("PyScada HMI : PyScadaControlItemDisplayValueTransformDataStep : " + variable_id + " not in DATA. ")
    return val;
  }
  var data = sliceDATAusingTimestamps(variable_id);
  if (data.length == 0) {return null;}
  var result = null;
  var prev = null;
  for (d in data) {
    if (prev != null) {
      if (result == null) {
        result = Math.abs(data[d][1] - prev);
      }else {
        result = Math.min(result, Math.abs(data[d][1] - prev));
      }
    }
    prev = data[d][1];
  }
  return result;
}

function PyScadaControlItemDisplayValueTransformDataChangeCount(key, val, control_item_id, display_value_option_id, transform_data_id) {
  var variable_id = get_config_from_hidden_config('controlitem', 'display-value-options', displayvalueoption_id, 'variable');
  if (DATA[variable_id] == undefined) {
    console.log("PyScada HMI : PyScadaControlItemDisplayValueTransformDataChangeCount : " + variable_id + " not in DATA. ")
    return val;
  }
  var data = sliceDATAusingTimestamps(variable_id);
  if (data.length == 0) {return null;}
  var result = 0;
  var prev = null;
  for (d in data) {
    if (prev != null && prev != data[d][1]) {
      result += 1;
    }
    prev = data[d][1];
  }
  return result;
}

function PyScadaControlItemDisplayValueTransformDataDistinctCount(key, val, control_item_id, display_value_option_id, transform_data_id) {
  var variable_id = get_config_from_hidden_config('controlitem', 'display-value-options', displayvalueoption_id, 'variable');
  if (DATA[variable_id] == undefined) {
    console.log("PyScada HMI : PyScadaControlItemDisplayValueTransformDataDistinctCount : " + variable_id + " not in DATA. ")
    return val;
  }
  var data = sliceDATAusingTimestamps(variable_id);
  if (data.length == 0) {return null;}
  var result = 0;
  var list = [];
  for (d in data) {
    if (!(data[d][1] in list)) {
      result += 1;
      list.push(data[d][1])
    }
  }
  return result;
}
