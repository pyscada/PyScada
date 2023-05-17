// modified from https://github.com/scientifichackers/django-hideshow

(function () {
    Set.prototype.diff = function (other) {
        let ret = new Set(this);
        for (let elem of other) {
            ret.delete(elem);
        }
        return ret;
    };

    document.addEventListener("DOMContentLoaded", function () {
        let nodes = document.querySelectorAll("[--hideshow-fields]");

        for (let node of nodes) {
            let onChange;

            let hideFields = new Set(csvParse(node.getAttribute("--hideshow-fields")));

            switch (node.type) {
                case "select-one":
                    onChange = function () {
                        let value = node.value;

                        let showOnSelected;
                        if (value) {
                            showOnSelected = csvParse(
                                node.getAttribute(`--show-on-${value}`)
                            );
                        }

                        let toShow = showOnSelected || [];
                        let toHide = hideFields.diff(toShow);

                        getFormRows(toShow, node).map(show);
                        getFormRows(toHide, node).map(hide);
                    };

                    break;

                case "checkbox":
                    let showOnChecked = csvParse(node.getAttribute("--show-on-checked"));

                    let toShow = showOnChecked || [];
                    let toHide = hideFields.diff(toShow);

                    let showRows = getFormRows(toShow, node);
                    let hideRows = getFormRows(toHide, node);

                    onChange = function () {
                        let checked = node.checked;
                        hideRows.map(checked ? hide : show);
                        showRows.map(checked ? show : hide);
                    };

                    break;
            }

            if (onChange) {
                onChange();
                node.addEventListener("change", onChange);
            }
        }
    });

    function csvParse(str) {
        if (!str) {
            return [];
        }
        let arr = str.split(",");
        for (let i = 0; i < arr.length; i++) {
            arr[i] = arr[i].trim();
        }
        return arr;
    }

    function getFormRows(fields, node) {
        return Array.from(_getFormRows(fields, node));
    }

    function* _getFormRows(fields, node) {
        if (!fields) {
            return;
        }
        for (let name of fields) {
            let formRow = fieldNameToFormRow(name, node);
            if (!formRow) continue;
            yield formRow;
        }
    }

    function fieldNameToFormRow(fieldName, node) {
        let cls = "field-" + fieldName;
        let formRow = node.parentNode.parentNode.parentNode.parentNode.getElementsByClassName(cls)[0];
        return formRow;
    }

    function hide(node) {
        node.style.display = "none";
    }

    function show(node) {
        node.style.display = "";
    }
})();