function post(url, vals, on_failure, on_success)
{
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(vals),
        contentType: "application/json",
        dataType: 'json',
        success: on_success, //(result)
        error: on_failure, //(jqXHR, textStatus, errorThrown)
    });
}

function form_get_inputs(container_handle) {
    jcontainer = dom_get_jquery(container_handle);
    inputs = jcontainer.find("input");
    latest_form_container = jcontainer;

    // find all the named inputs
    ret = [];
    $.each(inputs, (i, input) => {
        jinput = $(input);
        name = jinput.attr("name");
        if (name != null && name !== "" && name != "undefined") {
            ret.push(jinput);
        }
    });

    return ret;
}



latest_form_container = null;
function form_get_input_vals(container_handle) {
    /** Returns a dictionary of name to value. */
    jcontainer = dom_get_jquery(container_handle);
    inputs = form_get_inputs(jcontainer);

    ret = {}
    for (var i = 0; i < inputs.length; i++) {
        jinput = inputs[i];
        ret[jinput.attr("name")] = jinput.val();
    }

    return ret;
}

/**
 * Must be called after form_get_inputs or form_get_input_vals.
 */
latest_failure_instance = null;
function form_set(elem_handle, success, callback) {
    let jcontainer = latest_form_container;

    // find the jval instance by name, id, or class
    jval = jcontainer.find("[name="+elem_handle+"]");
    if (!is_dom(jval)) {
        if (elem_handle === "submit") {
            jval = jcontainer.find("input[type=submit]")
        }
        if (!is_dom(jval)) {
            jval = dom_get_jquery(elem_handle);
            if (!is_dom(jval)) {
                return null;
            }
        }
    }
    if (!success) {
        latest_failure_instance = jval;
    }

    function gen(jval, latest_failure_instance) {
        if (success) {
            return (results) => {
                jval.removeClass("success");
                jval.removeClass("failure");
                jval.addClass("success");
                if (is_jquery(latest_failure_instance)) {
                    latest_failure_instance.removeClass("failure");
                }
                dom_set_value(jval, results);
                if (callback != null) {
                    callback(jval, results);
                }
            };
        } else {
            return () => {
                jval.removeClass("success");
                jval.removeClass("failure");
                jval.addClass("failure");
                if (!jval.is("input") || jval.attr("type") !== "submit") {
                    dom_set_value(jval, "error");
                }
                if (callback != null) {
                    callback(jval, results);
                }
            };
        }
    }
    return gen(jval, latest_failure_instance);
}