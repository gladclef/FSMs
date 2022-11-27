import re
import sys
from typing import Optional, Union

re_entity = re.compile(r"^\s*entity\s+([A-Za-z_][A-Za-z0-9_]+)\s+is\s*$", re.IGNORECASE)
re_proc = re.compile(r"^\s*process\s*\(", re.IGNORECASE)
re_endproc = re.compile(r"^\s*end\s+process\s*;", re.IGNORECASE)
re_sequential = re.compile(r"^\s*process\s*\(\s*(clk|reset)\s*,\s*(clk|reset)\s*\)\s*$", re.IGNORECASE)
re_case_state_machine = re.compile(r"^\s*case\s+state_reg\s+is", re.IGNORECASE)
re_state = re.compile(r"^\s*when ([A-Za-z_][A-Za-z0-9_]+)\s*=>", re.IGNORECASE)
re_end_case = re.compile(r"^\s*end\s+case\s*;", re.IGNORECASE)
re_if = re.compile(r"^\s*if\s+\((.*)\)\s*then", re.IGNORECASE)
re_else = re.compile(r"^\s*else", re.IGNORECASE)
re_elsif = re.compile(r"^\s*elsif\s*\((.*)\)\s*then", re.IGNORECASE)
re_endif = re.compile(r"^\s*end\s+if;", re.IGNORECASE)
re_state_next = re.compile(r"^\s*state_next\s*<=\s*([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE)

_states_by_name: dict[str, any] = {}


class SVal:
    def __init__(self, strval: str):
        self.orig_strval: str = strval
        self.strval: str = strval.strip()
        self.next_states: dict[str, State] = {}

        for line in strval.splitlines():
            m = re_state_next.match(line)
            if m is not None:
                next_state_name = m.groups()[0]
                self.next_states[next_state_name] = State.get_state(next_state_name)

    def is_conditional(self):
        return False

    def next_states(self):
        return self.next_states

    def __add__(self, other):
        if isinstance(other, str):
            return SVal(self.orig_strval + other)
        elif isinstance(other, SVal):
            return SVal(self.orig_strval + other.orig_strval)
        else:
            return SVal(self.orig_strval + str(other))

    def __str__(self):
        return self.strval


class StateMachine:
    def __init__(self, parent: Optional['StateMachine']):
        self.parent: Optional[Union['Conditional', 'State']] = parent
        self.next_states: dict[str, Optional['State']] = {}

    def get_states(self) -> dict[str, 'State']:
        state_names = list(self.next_states.keys())
        for state_name in state_names:
            if self.next_states[state_name] is None:
                self.next_states[state_name] = State.get_state(state_name)
        return self.next_states

    def add_next_state(self, next_state_name: str) -> 'State':
        if next_state_name in self.next_states:
            return self.next_states[next_state_name]

        state: Optional['State'] = State.get_state(next_state_name)
        self.next_states[next_state_name] = state
        if self.parent is not None:
            self.parent.add_next_state(next_state_name)
        return state


class Content(StateMachine):
    def __init__(self, parent: Optional[Union['Conditional', 'State']]):
        super().__init__(parent)
        self.contents: list[Union[SVal, 'Conditional']] = []

    def append(self, static_or_conditional: Union[str, 'Conditional']) -> 'Content':
        if isinstance(static_or_conditional, Conditional):
            conditional: Conditional = static_or_conditional

            self.contents.append(conditional)
            for next_state_name in conditional.next_states:
                self.add_next_state(next_state_name)
        else:
            static: str = static_or_conditional
            if isinstance(static_or_conditional, SVal):
                sval: static_or_conditional = static_or_conditional
                static = sval.orig_strval

            m_next_state = re_state_next.match(static)
            if m_next_state:
                next_state_name = m_next_state.groups()[0]
                self.add_next_state(next_state_name)

            prev_is_static = len(self.contents) > 0 and isinstance(self.contents[-1], SVal)
            if prev_is_static:
                self.contents[-1] += static
            else:
                self.contents.append(SVal(static))

        return self

    def print(self, indent: int):
        ret = ""
        sindent: str = "   " * indent
        for content in self.contents:
            if ret != "":
                ret += "\n"
            if content.is_conditional():
                conditional: Conditional = content
                ret += conditional.print(indent)
            else:
                static: SVal = content
                lines = [l.strip() for l in static.orig_strval.splitlines()]
                ret += sindent + ("\n" + sindent).join(lines)
        return ret

    def __add__(self, other):
        if isinstance(other, str) or isinstance(other, Conditional) or isinstance(other, SVal):
            return self.append(other)
        else:
            raise RuntimeError(f"Trying to add {other} of type {type(other)} to Content")


class Conditional(StateMachine):
    def __init__(self, parent: Union['Conditional', 'State'], condition: str, is_elsif: bool = False):
        super().__init__(parent)
        self.condition: str = condition.strip()
        self.trueval: Content = Content(self)
        self.falseval: Optional[Content] = None
        self.elsifval: Optional[Conditional] = None
        self.is_elsif: bool = is_elsif

    def is_conditional(self):
        return True

    def append(self, val: Union[str, 'Conditional']) -> 'Conditional':
        if self.has_false():
            self.append_falseval(val)
        else:
            self.append_trueval(val)
        return self

    def append_trueval(self, trueval: Union[str, 'Conditional']):
        self.trueval += trueval

    def append_falseval(self, falseval: Union[str, 'Conditional']):
        if not self.has_false():
            self.falseval = Content(self)
        self.falseval += falseval

    def append_elsifval(self, elsifval: 'Conditional'):
        self.elsifval = elsifval

    def on_true(self):
        return self.trueval

    def has_false(self):
        return self.falseval is not None

    def has_elsif(self):
        return self.elsifval is not None

    def on_false(self):
        return self.falseval

    def print(self, indent: int):
        sindent = "   " * indent
        if self.is_elsif:
            ret = f"{sindent}elsif ({self.condition}) then\n"
        else:
            ret = f"{sindent}if ({self.condition}) then\n"
        ret += self.trueval.print(indent + 1) + "\n"

        if self.has_elsif():
            ret += self.elsifval.print(indent)
        elif self.has_false():
            ret += f"{sindent}else\n"
            ret += self.falseval.print(indent + 1) + "\n"
            ret += f"{sindent}end if;"
        else:
            ret += f"{sindent}end if;"
        return ret

    def __add__(self, other):
        if isinstance(other, str) or isinstance(other, Conditional) or isinstance(other, SVal):
            return self.append(other)
        else:
            raise RuntimeError(f"Trying to add {other} of type {type(other)} to Conditional")


class State(Content):
    def __init__(self, name: str):
        super().__init__(None)
        self.name: str = name.strip()
        _states_by_name[name] = self

    @classmethod
    def get_states(cls):
        return _states_by_name

    @classmethod
    def get_state(cls, state_name: str):
        if state_name not in _states_by_name:
            return None
        return _states_by_name[state_name]

    def get_transition_conditions(self) -> list[str]:
        ret = []
        next_transition = "__" # TODO get the actual transition strings
        for state_name, state in self.next_states.items():
            ret.append(next_transition)
            next_transition += "_"
        return ret

    def get_transitions(self, transition_conditions) -> list[str]:
        ret = list(self.next_states.keys())
        for i in range(len(ret)+1, len(transition_conditions)+1):
            ret.append("")
        return ret

    def print(self, indent):
        sindent = "   " * indent
        ret = f"{sindent}when {self.name} =>\n"
        ret += super().print(indent + 1)
        return ret


class Program():
    def __init__(self, filename: str):
        self.states: dict[str, State] = {}
        self.entity_name = "FSM"

        with open(filename, "r") as fin:

            # process all the lines in the first combination process to
            lineno = 1
            dval: dict[str:any] = {
                "entity_declared": False,
                "entity_name": "",
                "in_proc": False,
                "in_combinational": False,
                "in_state_machine": False,
                "state": None,
                "conditional": None,
            }
            for line in fin:
                try:
                    done, state = self._process_combination(line, lineno, dval)
                except Exception:
                    print(f"Error encountered while processing line {lineno}:\n\"{line}\"", file=sys.stderr)
                    raise
                if state is not None:
                    self.states[state.name] = state

                lineno += 1
                if done:
                    if dval["entity_declared"]:
                        self.entity_name = dval["entity_name"]
                    break

    def _process_combination(self, line: str, lineno: int, dval: dict[str:any]) -> tuple[bool, Optional[State]]:
        curr_state: State = dval["state"]
        sline = line.lstrip()
        if sline == "":
            sline = line

        if re_proc.match(sline):
            dval["in_proc"] = True
            if re_sequential.match(sline) is None:
                dval["in_combinational"] = True
        elif re_endproc.match(sline):
            if dval["in_combinational"]:
                return True, curr_state
            dval["in_state_machine"] = False
            dval["state"] = None
            dval["conditional"] = None
            dval["in_proc"] = False
            dval["in_combinational"] = False
        elif dval["in_combinational"]:
            if dval["in_state_machine"]:
                m_if = re_if.match(sline)
                m_else = re_else.match(sline)
                m_elsif = re_elsif.match(sline)
                m_endif = re_endif.match(sline)
                m_state = re_state.match(sline)
                m_end_case = re_end_case.match(sline)

                def get_conditional() -> Conditional:
                    if dval["conditional"] is None:
                        raise RuntimeError('Error at line ' + lineno + '. Not in a conditional! ' + line.strip())
                    return dval["conditional"]

                def append_lineval(lineval: str | Conditional):
                    if dval["conditional"] is not None:
                        conditional: Conditional = dval["conditional"]
                        conditional += lineval
                    else:
                        if dval["state"] is not None:
                            dval["state"] += lineval

                    if isinstance(lineval, Conditional):
                        dval["conditional"] = lineval

                if m_if:
                    parent = curr_state if (dval["conditional"] is None) else dval["conditional"]
                    append_lineval(Conditional(parent, m_if.groups()[0]))
                elif m_else:
                    conditional: Conditional = get_conditional()
                    conditional.append_falseval("")
                elif m_elsif:
                    conditional: Conditional = get_conditional()
                    elsifval = Conditional(conditional.parent, m_elsif.groups()[0], is_elsif=True)
                    conditional.append_elsifval(elsifval)
                    dval["conditional"] = elsifval
                elif m_endif:
                    conditional: Conditional = get_conditional()
                    parent = conditional.parent
                    dval["conditional"] = parent if (isinstance(parent, Conditional)) else None
                elif m_state:
                    dval["state"] = State(m_state.groups()[0])
                    return False, curr_state
                elif m_end_case:
                    dval["in_state_machine"] = False
                    dval["state"] = None
                    dval["conditional"] = None
                    dval["in_proc"] = False
                    dval["in_combinational"] = False
                    return True, curr_state
                else:
                    append_lineval(sline)

            else:  # if dval["in_state_machine"]
                m_case_state_machine = re_case_state_machine.match(sline)

                if m_case_state_machine:
                    dval["in_state_machine"] = True
        elif re_entity.match(sline):
            if not dval["entity_declared"]:
                dval["entity_name"] = re_entity.match(sline).groups()[0]
            dval["entity_declared"] = True
        else:
            pass

        return False, None

    def get_fsm_table(self) -> str:
        ret = "{'fsm_name': '" + self.entity_name + "', 'table_vals': ["
        state_strs: list[str] = []
        transition_conditions: list[str] = []

        for state_name, state in self.states.items():
            transition_conditions += state.get_transition_conditions()
        transition_conditions = list(sorted(set(transition_conditions)))
        for state_name, state in self.states.items():
            state_strs.append("'" + state_name + "', '" + "', '".join(state.get_transitions(transition_conditions)) + "'")

        print(transition_conditions)
        ret += "['', '" + "', '".join(transition_conditions) + "'], "
        ret += "[" + "], [".join(state_strs) + "]"
        ret += "]}"

        return ret

    def print(self, indent: int = 0) -> str:
        ret = ""
        for state_name, state in self.states.items():
            if ret != "":
                ret += "\n"
            ret += state.print(indent)
        return ret


if __name__ == "__main__":
    program = Program("C:/Users/gladc/Documents/School/UNM/ECE_522_codesign/current_lab/vhdl/Histo.vhd")

    stats = {
        "n_states": 0,
        "n_conditionals": 0,
        "n_statics": 0,
        "n_next_states": 0
    }
    for state_name, state in program.states.items():

        def process_conditional(conditional: Conditional):
            stats["n_conditionals"] += 1
            process_contents(conditional.trueval)
            if conditional.has_elsif():
                process_conditional(conditional.elsifval)
            elif conditional.has_false():
                process_contents(conditional.falseval)


        def process_contents(container: Content):
            for content in container.contents:
                if content.is_conditional():
                    process_conditional(content)
                else:
                    stats["n_statics"] += 1


        stats["n_states"] += 1
        stats["n_next_states"] += len(state.next_states)
        process_contents(state)

    print(stats)
