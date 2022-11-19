import math
from flask import Flask, redirect, url_for, request, render_template, jsonify

from lib.css import *
import lib.geometry as geo

app = Flask(__name__)

def parse_table(table_vals:list[list[str]] = None, clear_empty:bool = False) -> tuple[list[list[str]], list[str], list[str], dict[str,dict[str,str]]]:
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

    # filter out empty rows and columns
    if clear_empty:
        new_table_vals = []
        for row in table_vals:
            if any(filter(lambda s: s != "", row)):
                new_table_vals.append(row)
        if len(new_table_vals) == 0:
            return [], [], [], {}
        for col_idx in range(len(new_table_vals[0])):
            found = False
            col_vals = [row[col_idx] for row in new_table_vals]
            if not any(filter(lambda s: s != "", col_vals)):
                for row in new_table_vals:
                    del row[col_idx]
        table_vals = new_table_vals

    # extract the states and transitions
    states, transitions = [], []
    if len(table_vals) > 0:
        states = [l[0] for l in table_vals[1:]]
        if len(table_vals[0]) > 1:
            transitions = table_vals[0][1:]
    transition_map = {state:{} for state in states}

    # extract the state transition mapping
    if len(table_vals) > 0:
        for state_row in table_vals[1:]:
            state = state_row[0] if (len(state_row) > 0) else ""
            for trans_idx in range(len(transitions)):
                transition = transitions[trans_idx]
                next_state = state_row[trans_idx+1]
                if next_state != "":
                    transition_map[state][transition] = next_state

    return table_vals, states, transitions, transition_map

def populate_table(table_vals:list[list[str]] = None, clear_empty:bool = False) -> str:
    table_vals, states, transitions, transition_map = parse_table(table_vals, clear_empty)

    # get dimensions
    width, height = css_get_size("div.table")
    symw, symh = css_get_size("div.table .sym")
    cwidth = max(120, min(200, math.floor((width-3*symw-20) / (len(transitions)+1) )))
    rheight = max(20, min(40, height / (len(states)+2) ))
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
    # ... footer
    ret += "<div><input type='button' name='update' value='Update' /><input type='button' name='update_and_clear' value='Clear Empty'></div>"

    return ret

def populate_graph(table_vals:list[list[str]] = None) -> str:
    table_vals, states, transitions, transition_map = parse_table(table_vals)
    states = list(filter(lambda s: s != "", states))

    # get some dimensions
    r1, r2, rself = 40, 200, 25
    size = r2*2 + r1*2 + rself*4 + 20*2
    center = size / 2
    angle = 2*math.pi / len(states)
    _, text_height = css_get_size("div.diagram text")
    pcenter = geo.Pxy(center, center)

    # prep
    ret = f"<svg width='{size}' height='{size}'>"

    # draw some circles!
    state_pos = {}
    state_intersections = {}
    for state_idx in range(len(states)):
        state = states[state_idx]
        p = geo.rad_to_cart(angle * state_idx, r2, center)
        state_pos[state] = p
        ret += f"<circle cx='{p.x}' cy='{p.y}' r='{r1}' />"
        i1, i2 = geo.circle_intersections([center, center, r2], [p.x, p.y, r1])
        i3, i4 = geo.circle_vector_intersections([center, center, r2], angle*state_idx, r2-r1, r2+r1)
        i5, i6 = geo.circle_intersections([center, center, r2+25], [p.x, p.y, r1])
        state_intersections[state] = { "left": i1, "right": i2, "inside": i3, "outside": i4, "outer_left": i5, "outer_right": i6}

    # helper functions
    transition_texts : dict[geo.Pxy,list[str]] = {}
    def add_transition_text(p1: geo.Pxy, sval: str):
        for p2, svals in transition_texts.items():
            if p1.dist(p2) < 10:
                svals.append(sval)
                return
        transition_texts[p1] = [sval]
    def draw_arc(xy1:geo.Pxy, xy2:geo.Pxy, circ:geo.Pxy, sval:str, ret:str, clockwise:bool=True, is_line=False) -> str:
        """ Draws an arc, some text, and an arrow

        Parameters
        ----------
            xy1: must be to the counter-clockwise location of xy2
            xy2: must be to the clockwise location of xy1
            circ: The location of the ending circle
        """
        # draw the arc
        if is_line:
            ret += f"<path d='M {xy1.x} {xy1.y} L {xy2.x} {xy2.y}' />"
        elif xy1 != xy2:
            radius = r2 if clockwise else r2+25
            ret += f"<path d='M {xy1.x} {xy1.y} A {radius} {radius} 0 0 1 {xy2.x} {xy2.y}' />"
        else:
            self_rad = geo.cart_to_rad(pcenter, xy1)
            pself = geo.rad_to_cart(geo.Rad(self_rad.radians, r2+r1+rself), centerx=center, centery=center)
            ret += f"<circle class='arc' cx='{pself.x}' cy='{pself.y}' r='{rself}' />"

        # add the text
        if is_line:
            xdist, ydist = xy1.xdist(xy2), xy1.ydist(xy2)
            mid = geo.Pxy(xy1.x + xdist*3/4, xy1.y + ydist*3/4)
            add_transition_text(mid, sval)
        elif xy1 != xy2: # self-referencing circle
            sval_rad = geo.Rad(3/4, -25) if clockwise else geo.Rad(1/4, 50)
            rad1 = geo.cart_to_rad(pcenter, xy1)
            rad2 = geo.cart_to_rad(pcenter, xy2)
            rad_mid = geo.Rad(rad1.radians + (rad2.radians - rad1.radians) * sval_rad.radians, r2 + sval_rad.dist)
            mid = geo.rad_to_cart(rad_mid, centerx=center, centery=center)
            add_transition_text(mid, sval)
        else:
            add_transition_text(pself, sval)

        # draw an arrow
        arr_width = math.pi / 4
        arr_length = 10
        arr_pnts = [None, None, None]
        arr_pnts[1] = xy2 if clockwise else xy1
        arr_rad = geo.cart_to_rad(circ, arr_pnts[1])
        if xy1 == xy2:
            arr_rad = geo.Rad(arr_rad.radians + math.pi*5/11, arr_rad.dist) # for self-referencing circles
        elif is_line:
            arr_rad = geo.cart_to_rad(xy2, xy1)
        elif clockwise:
            arr_rad = geo.Rad(arr_rad.radians - math.pi/25, arr_rad.dist) # who knows why this is needed
        else:
            arr_rad = geo.Rad(arr_rad.radians + math.pi*9/13, arr_rad.dist) # who knows why this is needed
        arr_start_rad = geo.Rad(arr_rad.radians + arr_width/2, arr_length)
        arr_stop_rad = geo.Rad(arr_rad.radians - arr_width/2, arr_length)
        arr_pnts[0] = geo.rad_to_cart(arr_start_rad, centerx=arr_pnts[1].x, centery=arr_pnts[1].y)
        arr_pnts[2] = geo.rad_to_cart(arr_stop_rad, centerx=arr_pnts[1].x, centery=arr_pnts[1].y)
        ret += f"<path d='M {arr_pnts[0].x} {arr_pnts[0].y} L {arr_pnts[1].x} {arr_pnts[1].y} L {arr_pnts[2].x} {arr_pnts[2].y}' />"

        return ret

    # draw some transitions!
    for state1 in states:
        try:
            state1_idx = states.index(state1)
        except ValueError:
            continue
        for transition, state2 in transition_map[state1].items():
            try:
                state2_idx = states.index(state2)
            except ValueError:
                continue

            if (state1_idx == state2_idx):
                # self-transition
                xy1 = state_intersections[state1]["outside"]
                circ = state_pos[state1]
                ret += draw_arc(xy1, xy1, circ, sval=transition, ret=ret)
            elif (transition != "reset") and ((state2_idx == state1_idx+1) or (state2_idx == 0 and state1_idx == len(states)-1)):
                # draw a clockwise arc
                xy1 = state_intersections[state1]["right"]
                xy2 = state_intersections[state2]["left"]
                circ = state_pos[state2]
                ret += draw_arc(xy1, xy2, circ, sval=transition, ret=ret)
            elif (transition != "reset") and ((state1_idx == state2_idx+1) or (state1_idx == 0 and state2_idx == len(states)-1)):
                # draw a counter-clockwise arc
                xy1 = state_intersections[state2]["outer_right"]
                xy2 = state_intersections[state1]["outer_left"]
                circ = state_pos[state1]
                ret += draw_arc(xy1, xy2, circ, sval=transition, ret=ret, clockwise=False)
            else:
                # draw an inside arc
                xy1 = state_intersections[state1]["inside"]
                xy2 = state_intersections[state2]["inside"]
                circ = state_pos[state2]
                ret += draw_arc(xy1, xy2, circ, sval=transition, ret=ret, is_line=True)

    # add some text!
    for state_idx, state in enumerate(states):
        p = state_pos[state]
        ret += f"<text x='{p.x}' y='{p.y+5}'>{state}</text>"
    for p1, svals in transition_texts.items():
        y_start = text_height * (len(svals)-1) / 2
        for idx, sval in enumerate(svals):
            p2 = geo.Pxy(p1.x, p1.y - y_start + text_height*idx)
            ret += f"<text x='{p2.x}' y='{p2.y+5}'>{sval}</text>"

    ret += "</svg>"
    return ret

def populate_code(table_vals:list[list[str]] = None) -> str:
    table_vals_str = str(table_vals)
    table_vals, states, transitions, transition_map = parse_table(table_vals)

    ret = "-----------------------------------------------------------\n" \
          "-- FSM created with https://github.com/gladclef/FSMs\n" \
          f"-- {table_vals_str}\n" \
          "-----------------------------------------------------------\n" \
          "\n" \
          "library IEEE;\n" \
          "use IEEE.STD_LOGIC_1164.ALL;\n" \
          "use IEEE.NUMERIC_STD.ALL;\n" \
          "\n" \
          "entity fsm is\n" \
          "   Port (\n" \
          "      reset : in std_logic;\n" \
          "      clk : in std_logic\n" \
          "   );\n" \
          "end fsm;\n" \
          "\n" \
          "architecture rtl of fsm is\n"
    ret += f"   type state_type is ({', '.join(states)});\n" \
           f"   signal state_reg, state_next: state_type;\n"
    for transition in transitions:
        if transition != "reset":
            ret += f"   signal {transition}: std_logic;\n"
    ret += "begin\n" \
           "\n" \
           "   -- state and data register\n" \
           "   process(clk, reset)\n" \
           "   begin\n" \
           "      if (reset = '1') then\n" \
           f"         state_reg <= {states[0]};\n" \
           "      elsif (rising_edge(clk)) then\n" \
           "         state_reg <= state_next;\n" \
           "      end if;\n" \
           "   end process;\n" \
           "\n" \
           "   -- combinational circuit\n" \
           f"   process(state_reg, {', '.join(transitions)})\n" \
           "   begin\n" \
           "      state_next <= state_reg;\n" \
           "\n" \
           "      case state_reg is\n"
    for state in states:
        ret += f"         when {state} =>\n"
        first_transition = True
        for transition, state_next in transition_map[state].items():
            ifstr = "if" if first_transition else "elsif"
            ret += f"            {ifstr} ({transition} = '1') then\n" \
                   f"               state_next <= {state_next};\n"
            first_transition = False
        ret += "            end if;\n" \
               "\n"
    ret += "      end case;\n" \
           "   end process;\n" \
           "end rtl;\n"

    linecnt = len(ret.split('\n'))
    return f"<textarea rows='{linecnt}' cols='80'>{ret}</textarea>"

@app.route('/update_table', methods=['POST'])
def update_table():
    if request.method == 'POST':
        table_vals = request.json['table_vals']
        clear_emtpy = request.json['clear_emtpy']
        table_str = populate_table(table_vals, clear_emtpy)
        return jsonify(table_str)

@app.route('/update_graph', methods=['POST'])
def update_graph():
    if request.method == 'POST':
        table_vals = request.json['table_vals']
        graph_str = populate_graph(table_vals)
        return jsonify(graph_str)

@app.route('/update_code', methods=['POST'])
def update_code():
    if request.method == 'POST':
        table_vals = request.json['table_vals']
        graph_str = populate_code(table_vals)
        return jsonify(graph_str)

@app.route('/', methods=['GET'])
def login():
    if request.method == 'GET':
        return render_template('main.html', populate_table=populate_table, populate_diagram=populate_graph, populate_code=populate_code)

if __name__ == '__main__':
    app.run(debug=True)