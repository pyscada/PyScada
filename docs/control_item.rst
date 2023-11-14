Control item
============

Control items are elements of crontol panels which have two functions by default:

- display the last value of a variable,
- control the value of a variable.

To create one in the administration interface, you need at least to:

- enter a label,
- select a variable OR a variable property.
- chose a type : display the value or control the value of the variable/variable property,

You can also:

- select the order in the control panel using the position attribute : lower is at the top of the control panel,
- add options using display value options or control element options.

Display value options
---------------------

It allows adding options to a control item configured to display value.

To create one in the administration interface, you need at least to:

- enter a title,
- choose a template to change the graphic rendering,
- choose if you want to replace a timestamp value by a human readable format,
- transform the data before show it in the user interface: see section below,
- apply color levels: see section below.

### Transform data

#### Usage (configuration)

You can use a data transformation to pass the data through a function before displaying it (for example, display the minimum of the variable in the selected time range).

You may need to specify additional information at the bottom depending on the tranformation needs (as for the Count Value transformation).

#### Creation (developer)

A plugin can add a new transform data to the list.

To do so you can create them automatically in the *ready* function of the *AppConfig* class in *apps.py*.
Have a look at the [*hmi.apps.py*](https://github.com/pyscada/PyScada/blob/main/pyscada/hmi/apps.py).

The fields of a transform data are :
- inline_model_name : the model name to add an inline to the admin page which can add additional fields needed by the transform data function (as TransformDataCountValue for the Count Value function),
- short_name : the name displayed in the admin interface,
- js_function_name : the name of the JavaScript function which will be called to transform the data,
- js_files : a coma separated list of the JavaScript files to add,
- css_files : a coma separated list of the CSS files to add,
- need_historical_data : set to True if the transform data function needs the variable data for the whole period selected by the date time range picker, set to False if it only needs the last value.

### Template

You can choose a specific template to display you control item.

#### Creation (developer)

A plugin can add a new control item template.

To do so you can create them automatically in the *ready* function of the *AppConfig* class in *apps.py*.
Have a look at the [*hmi.apps.py*](https://github.com/pyscada/PyScada/blob/main/pyscada/hmi/apps.py).

The fields of a template are :
- label the template name to display,
- template_name : the file name to use,
- js_files : a coma separated list of the JavaScript files to add,
- css_files : a coma separated list of the CSS files to add.
