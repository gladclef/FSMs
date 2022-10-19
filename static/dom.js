function dom_set_value(jval, val) {
    if (jval.is("input")) {
        jval.val(val);
    } else {
        jval.html(val);
    }
}

function dom_get_jquery(jquery_or_elem_or_handle) {
    if (is_str(jquery_or_elem_or_handle)) {
        // id or class or name
        ret = $("#"+jquery_or_elem_or_handle);
        if (is_dom(ret)) { return ret; }
        ret = $("."+jquery_or_elem_or_handle);
        if (is_dom(ret)) { return ret; }
        return $("[name="+jquery_or_elem_or_handle+"]");
    } else if (is_jquery(jquery_or_elem_or_handle)) {
        return jquery_or_elem_or_handle;
    } else {
        return $(jquery_or_elem_or_handle);
    }
}