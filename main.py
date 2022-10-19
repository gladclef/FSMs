import math

from flask import Flask, redirect, url_for, request, render_template, jsonify
from lib.css import *

app = Flask(__name__)

def parse_table(table_vals:list[list[str]] = None) -> tuple[list[list[str]], list[str], list[str], dict[str,dict[str,str]]]:
    if table_vals is None:
        table_vals = [["",     "reset", "start", "is_done"],
                      ["IDLE", "IDLE",  "WORK",  ""],
                      ["WORK", "IDLE",  "",      "IDLE"]]

    # filter the input to only valid characters
    def filter_varname(sval):
        sval = list(re.findall(r'[a-zA-Z_][a-zA-Z0-9_]+', sval))
        if len(sval) == 0:
            return ""
        return sval[0]

    # rebuild the table values with filtered strings
    new_table_vals = []
    for row in table_vals:
        new_table_vals.append(list(map(filter_varname, row)))
    table_vals = new_table_vals

    # extract the states and transitions
    states, transitions = [], []
    if len(table_vals) > 0:
        states = [l[0] for l in table_vals[1:]]
        if len(table_vals[0]) > 1:
            transitions = table_vals[0][1:]
    transition_map = {state:{} for state in states}

    # extract the state transition mapping
    for state_row in table_vals[1:]:
        state = state_row[0] if (len(state_row) > 0) else ""
        for trans_idx in range(len(transitions)):
            transition = transitions[trans_idx]
            next_state = state_row[trans_idx+1]
            if next_state != "":
                transition_map[state][transition] = next_state

    return table_vals, states, transitions, transition_map

def populate_table(table_vals:list[list[str]] = None) -> str:
    table_vals, states, transitions, transition_map = parse_table(table_vals)

    # get dimensions
    width, height = css_get_size("div.table")
    symw, symh = css_get_size("div.table .sym")
    cwidth = max(120, min(200, math.floor((width-3*symw-20) / (len(transitions)+1) )))
    rheight = max(20, min(40, height / (len(states)+1) ))
    style = f"style='width: {cwidth}px; height: {rheight}px'"
    row_style = f"style='width: {cwidth*(len(transitions)+1) + symw*3}px'"

    # build the table
    def cell(txt, row_idx, col_idx, *classes):
        sclasses = " ".join(classes)
        return f"<input type='text' class='tcell {sclasses}' {style} name='{row_idx}_{col_idx}' value='{txt}' />"
    def syms(row_index):
        return f"<div class='sym up' onclick='row_up({row_index})'>▲</div>" + \
               f"<div class='sym down' onclick='row_down({row_index})'>▼</div>" + \
               f"<div class='sym plus' onclick='row_plus({row_index})'>➕</div>"
    # ... header
    ret = f"<div class='row' {row_style}><div class='tcell header' {style}></div>"
    for col_idx in range(len(transitions)):
        transition = transitions[col_idx]
        ret += cell(transition, 0, col_idx+1, 'header')
    ret += "<div class='sym plus' onclick='col_plus()'>➕</div></div>"
    # ... body
    for row_idx in range(len(states)):
        state = states[row_idx]
        row = f"<div class='row' {row_style}>" + cell(state, row_idx+1, 0)
        state_transitions = transition_map[state]
        for col_idx in range(len(transitions)):
            transition = transitions[col_idx]
            next_state = "" if (transition not in state_transitions) else state_transitions[transition]
            row += cell(next_state, row_idx+1, col_idx+1)
        ret += row + syms(row_idx) + "</div>"

    return ret

@app.route('/update_table', methods=['POST'])
def update_table():
    if request.method == 'POST':
        table_vals = request.json['table_vals']
        table_str = populate_table(table_vals)
        return jsonify(table_str)

@app.route('/', methods=['GET'])
def login():
    if request.method == 'GET':
        return render_template('main.html', populate_table=populate_table)

if __name__ == '__main__':
    app.run(debug=True)