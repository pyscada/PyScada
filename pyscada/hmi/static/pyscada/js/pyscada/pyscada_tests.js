/*
run it it using :
var js = document.createElement("script");

js.type = "text/javascript";
js.src = "/static/pyscada/js/pyscada/pyscada_tests.js";

document.body.appendChild(js);
for (test in PYSCADA_TESTS) {PYSCADA_TESTS[test]();}
*/

function pyscada_test_add_data() {

    // Warn if overriding existing method
    if(Array.prototype.equals)
        console.warn("Overriding existing Array.prototype.equals. Possible causes: New API defines the method, there's a framework conflict or you've got double inclusions in your code.");
    // attach the .equals method to Array's prototype to call it on any array
    Array.prototype.equals = function (array) {
        // if the other array is a falsy value, return
        if (!array)
            return false;
        // if the argument is the same array, we can be sure the contents are same as well
        if(array === this)
            return true;
        // compare lengths - can save a lot of time
        if (this.length != array.length)
            return false;

        for (var i = 0, l=this.length; i < l; i++) {
            // Check if we have nested arrays
            if (this[i] instanceof Array && array[i] instanceof Array) {
                // recurse into the nested arrays
                if (!this[i].equals(array[i]))
                    return false;
            }
            else if (this[i] != array[i]) {
                // Warning - two different object instances will never be equal: {x:20} != {x:20}
                return false;
            }
        }
        return true;
    }
    // Hide method from for-in loops
    Object.defineProperty(Array.prototype, "equals", {enumerable: false});



    key="test_add_data";
    CHART_VARIABLE_KEYS[key]=1;
    DATA[key]=[[1,7], [2,8], [4,9], [11,15]];
    console.log(DATA[key]);
    ok=0;
    fail=0;

    function test_add_fetched_data(value, wanted) {
        key=666;
        CHART_VARIABLE_KEYS[key]=1;
        DATA[key]=[[1,7], [2,8], [4,9], [11,15]];
        add_fetched_data(key,value);
        result = DATA[key].equals(wanted)
        console.log(result);
        if (!result) {console.log(DATA[key], value, wanted);};
        return result;
    }

    value=[[0,1]];
    wanted=[[0, 1], [1, 7], [2, 8], [4, 9], [11, 15]];
    test_add_fetched_data(value, wanted) ? ok +=1 : fail += 1;

    value=[[0,1],[1,1]];
    wanted=[[0, 1], [1, 7], [2, 8], [4, 9], [11, 15]];
    test_add_fetched_data(value, wanted) ? ok +=1 : fail += 1;

    value=[[1,1]];
    wanted=[[1, 7], [2, 8], [4, 9], [11, 15]];
    test_add_fetched_data(value, wanted) ? ok +=1 : fail += 1;

    value=[[0,1],[2,1]];
    wanted=[[0, 1], [1, 7], [2, 8], [4, 9], [11, 15]];
    test_add_fetched_data(value, wanted) ? ok +=1 : fail += 1;

    value=[[1,1],[2,1]];
    wanted=[[1, 7], [2, 8], [4, 9], [11, 15]];
    test_add_fetched_data(value, wanted) ? ok +=1 : fail += 1;

    value=[[2,1]];
    wanted=[[1, 7], [2, 8], [4, 9], [11, 15]];
    test_add_fetched_data(value, wanted) ? ok +=1 : fail += 1;

    value=[[2,1], [3,2]];
    wanted=[[1, 7], [2, 8], [4, 9], [11, 15]];
    test_add_fetched_data(value, wanted) ? ok +=1 : fail += 1;

    value=[[3,2]];
    wanted=[[1, 7], [2, 8], [3, 2], [4, 9], [11, 15]];
    test_add_fetched_data(value, wanted) ? ok +=1 : fail += 1;

    value=[[5,2], [6,4]];
    wanted=[[1, 7], [2, 8], [4, 9], [5, 2], [6, 4], [11, 15]];
    test_add_fetched_data(value, wanted) ? ok +=1 : fail += 1;

    value=[[3,2], [4,10]];
    wanted=[[1, 7], [2, 8], [4, 9], [11, 15]];
    test_add_fetched_data(value, wanted) ? ok +=1 : fail += 1;

    value=[[2,2], [4,10]];
    wanted=[[1, 7], [2, 8], [4, 9], [11, 15]];
    test_add_fetched_data(value, wanted) ? ok +=1 : fail += 1;

    value=[[2,2], [3, 2], [4,10]];
    wanted=[[1, 7], [2, 8], [4, 9], [11, 15]];
    test_add_fetched_data(value, wanted) ? ok +=1 : fail += 1;

    value=[[3,2], [6,10]];
    wanted=[[1, 7], [2, 8], [4, 9], [11, 15]];
    test_add_fetched_data(value, wanted) ? ok +=1 : fail += 1;

    value=[[11,2]];
    wanted=[[1, 7], [2, 8], [4, 9], [11, 15]];
    test_add_fetched_data(value, wanted) ? ok +=1 : fail += 1;

    delete DATA["test_add_data"]
    console.log("pyscada_test_add_data : ok", ok, ", fail", fail);
}

PYSCADA_TESTS.push(pyscada_test_add_data)
