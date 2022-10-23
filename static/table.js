function get_table_text_boxes(jtable) {
    if (arguments.length === 0 || jtable === undefined || jtable == null) {
        jtable = $("div.table");
    }
    let jinputs = form_get_inputs(jtable);
    jinputs = jinputs.filter(jinput => jinput.attr("type") === "text")
    return jinputs;
}

function get_table_buttons(jtable) {
    if (arguments.length === 0 || jtable === undefined || jtable == null) {
        jtable = $("div.table");
    }
    let jinputs = form_get_inputs(jtable);
    jinputs = jinputs.filter(jinput => jinput.attr("type") === "button")
    return jinputs;
}

function get_table_vals() {
    console.log('get_table_vals');
    let jtexts = get_table_text_boxes();
    ret = [];

    $.each(jtexts, (i, jtext) => {
        parts = jtext.attr("name").split("_");
        row_idx = parseInt(parts[0]);
        col_idx = parseInt(parts[1]);

        // make sure the return value is long enough
        for (var r = 0; r <= row_idx; r++) {
            if (ret.length < r+1) {
                ret.push([]);
            }
            for (var c = ret[r].length-1; c <= col_idx; c++) {
                if (ret[r].length < c+1) {
                    ret[r].push("");
                }
            }
        }

        // add this value to the return table values
        ret[row_idx][col_idx] = jtext.val();
    });

    return ret;
}

dont_update_on_saveme_changed = false;
function saveme_changed() {
    if (dont_update_on_saveme_changed) {
        return;
    }

    get_table_vals(); // do this so that latest_failure_instance is set
    _update( eval($('[name=saveme_tvals]').val()), false );
}

function table_key_up(jinput, key) {
    console.log('table_key_up');
    let jnext = null;
    parts = jinput.attr("name").split("_");
    row_idx = parseInt(parts[0]);
    col_idx = parseInt(parts[1]);

    if (key === "ArrowUp") {
        jnext = $("input[name="+(row_idx-1)+"_"+col_idx+"]");
    } else if (key === "ArrowDown") {
        jnext = $("input[name="+(row_idx+1)+"_"+col_idx+"]");
        if (jnext.length === 0) {
            row_plus(row_idx);
            setTimeout(() => {
                jnext = $("input[name="+(row_idx+1)+"_"+col_idx+"]");
                jnext.focus();
                jnext.select();
            }, 200);
        }
    } else if (key === "Enter") {
        update();
        setTimeout(() => {
            jinput = $("input[name="+row_idx+"_"+col_idx+"]");
            jinput.focus();
            jinput.select();
        }, 200);
    }

    if (jnext != null && jnext.length > 0) {
        jnext.focus();
        jnext.select();
    }
}

function attach_table_handles(jtable, results) {
    console.log('attach_table_handles');
    let jtexts = get_table_text_boxes(jtable);
    let jbuttons = get_table_buttons(jtable);
    $.each(jtexts, (i, jtext) => {
        jtext.keyup((e) => { table_key_up(jtext, e.key); } );
    });
    $.each(jbuttons, (i, jbutton) => {
        if (jbutton.attr("name").indexOf("clear") >= 0) {
            jbutton.click(update_with_clear_empty);
        } else {
            jbutton.click(update);
        }
    });
}

function update() {
    _update(get_table_vals(), false);
}

function update_with_clear_empty() {
    _update(get_table_vals(), true)
}

function _update(table_vals, clear_empty) {
    console.log("_update");
    post("/update_table", {"table_vals": table_vals, "clear_emtpy": clear_empty}, null, form_set('table', true, attach_table_handles));
    post("/update_graph", {"table_vals": table_vals}, null, form_set('fsm_container', true));
    post("/update_code", {"table_vals": table_vals}, null, form_set('code', true));

    dont_update_on_saveme_changed = true;
    $('[name=saveme_tvals]').val(JSON.stringify(table_vals));
    dont_update_on_saveme_changed = false;
}

function row_up(idx) {
    if (idx === 0) { return; }
    table_vals = get_table_vals();
    prev_row = table_vals[idx];
    table_vals.splice(idx+2, 0, prev_row);
    table_vals.splice(idx, 1);
    _update(table_vals, false);
}

function row_down(idx) {
    table_vals = get_table_vals();
    if (idx === table_vals.length-2) { return; }
    next_row = table_vals[idx+2];
    table_vals.splice(idx+2, 1);
    table_vals.splice(idx+1, 0, next_row);
    _update(table_vals, false);
}

function row_plus(idx) {
    table_vals = get_table_vals();
    row = [];
    for (var c = 0; c < table_vals[0].length; c++) {
        row.push("");
    }
    table_vals.splice(idx+2, 0, row);
    _update(table_vals, false);
}

function col_plus() {
    table_vals = get_table_vals();
    for (var r = 0; r < table_vals.length; r++) {
        table_vals[r].push("");
    }
    _update(table_vals, false);
}