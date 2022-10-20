function get_table_vals() {
    let jinputs = form_get_inputs($("div.table"));
    ret = [];

    $.each(jinputs, (i, jinput) => {
        parts = jinput.attr("name").split("_");
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
        ret[row_idx][col_idx] = jinput.val();
    });

    return ret;
}

dont_update_on_saveme_changed = false;
function saveme_changed() {
    if (dont_update_on_saveme_changed) {
        return;
    }

    get_table_vals(); // do this so that latest_failure_instance is set
    update( eval($('[name=saveme_tvals]').val()) );
}

function update(table_vals) {
    post("/update_table", {"table_vals": table_vals}, null, form_set('table', true));
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
    update(table_vals);
}

function row_down(idx) {
    table_vals = get_table_vals();
    if (idx === table_vals.length-2) { return; }
    next_row = table_vals[idx+2];
    table_vals.splice(idx+2, 1);
    table_vals.splice(idx+1, 0, next_row);
    update(table_vals);
}

function row_plus(idx) {
    table_vals = get_table_vals();
    row = [];
    for (var c = 0; c < table_vals[0].length; c++) {
        row.push("");
    }
    table_vals.splice(idx+2, 0, row);
    update(table_vals);
}

function col_plus() {
    table_vals = get_table_vals();
    for (var r = 0; r < table_vals.length; r++) {
        table_vals[r].push("");
    }
    update(table_vals);
}