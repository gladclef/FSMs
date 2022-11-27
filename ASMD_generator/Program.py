import re
from typing import Optional, Union

re_proc = re.compile(r"^\s*process\s*\(")
re_endproc = re.compile(r"^\s*end\s+process\s*;")
re_sequential = re.compile(r"^\s*process\s*\(\s*(clk|reset)\s*,\s*(clk|reset)\s*\)\s*$")
re_case_state_machine = re.compile(r"^\s*case\s+state_reg\s+is")
re_state = re.compile(r"^\s*when ([A-Za-z_][A-Za-z0-9_]+)\s*=>")
re_end_case = re.compile(r"^\s*end\s+case\s*;")
re_if = re.compile(r"^\s*if\s+\((.*)\)\s*then")
re_else = re.compile(r"^\s*else")
re_elsif = re.compile(r"^\s*elsif (.*)\s*then")
re_endif = re.compile(r"^\s*end\s+if;")
re_state_next = re.compile(r"^\s*state_next\s*<=\s*([A-Za-z_][A-Za-z0-9_]*)")

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
        self.parent: Optional[Union['Conditional','State']] = parent
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
        self.contents: list[Union[SVal,'Conditional']] = []

    def append(self, static_or_conditional: Union[str,'Conditional']) -> 'Content':
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
        sindent: str = "   " * indent
        for content in self.contents:
            if content.is_conditional():
                conditional: Conditional = content
                conditional.print(indent)
            else:
                static: SVal = content
                lines = [l.strip() for l in static.orig_strval.splitlines()]
                print(sindent + ("\n"+sindent).join( lines ))

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

    def append(self, val: Union[str,'Conditional']) -> 'Conditional':
        if self.has_false():
            self.append_falseval(val)
        else:
            self.append_trueval(val)
        return self

    def append_trueval(self, trueval: Union[str,'Conditional']):
        self.trueval += trueval

    def append_falseval(self, falseval: Union[str,'Conditional']):
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
        sindent = "   "*indent
        if self.is_elsif:
            print(f"{sindent}elsif ({self.condition}) then")
        else:
            print(f"{sindent}if ({self.condition}) then")
        self.trueval.print(indent+1)

        if self.has_elsif():
            self.elsifval.print(indent)
        elif self.has_false():
            print(f"{sindent}else")
            self.falseval.print(indent+1)
            print(f"{sindent}end if;")
        else:
            print(f"{sindent}end if;")

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

    def print(self, indent):
        sindent = "   "*indent
        print(f"{sindent}when {self.name} =>")
        super().print(indent+1)


class Program():
    def __init__(self, filename: str):
        self.states: dict[str,State] = {}

        with open(filename, "r") as fin:

            # process all the lines in the first combination process to
            lineno = 1
            dval: dict[str:any] = {
                "in_proc": False,
                "in_combinational": False,
                "in_state_machine": False,
                "state": None,
                "conditional": None,
            }
            for line in fin:
                done = self._process_combination(line, lineno, dval)
                lineno += 1

                if done:
                    self.states = State.get_states()
                    break

    def _process_combination(self, line, lineno, dval):
        lline = line.lower().lstrip()

        if re_proc.match(lline):
            dval["in_proc"] = True
            if re_sequential.match(lline) is None:
                dval["in_combinational"] = True
        elif re_endproc.match(lline):
            if dval["in_combinational"]:
                return True
            dval["in_state_machine"] = False
            dval["state"] = None
            dval["conditional"] = None
            dval["in_proc"] = False
            dval["in_combinational"] = False
        elif dval["in_combinational"]:
            if dval["in_state_machine"]:
                m_if = re_if.match(lline)
                m_else = re_else.match(lline)
                m_elsif = re_elsif.match(lline)
                m_endif = re_endif.match(lline)
                m_state = re_state.match(lline)
                m_end_case = re_end_case.match(lline)

                def get_conditional() -> Conditional:
                    if dval["conditional"] is None:
                        raise RuntimeError('Error at line '+lineno+'. Not in a conditional! '+line.strip())
                    return dval["conditional"]

                def append_lineval(lineval: str | Conditional):
                    if dval["conditional"] is not None:
                        conditional: Conditional = dval["conditional"]
                        conditional += lineval
                    else:
                        state: State = dval["state"]
                        state += lineval

                    if isinstance(lineval, Conditional):
                        dval["conditional"] = lineval

                if m_if:
                    parent = dval["state"] if (dval["conditional"] is None) else dval["conditional"]
                    append_lineval(Conditional(parent, m_if.groups()[0]))
                elif m_else:
                    conditional:Conditional = get_conditional()
                    conditional.append_falseval("")
                elif m_elsif:
                    conditional:Conditional = get_conditional()
                    elsifval = Conditional(conditional.parent, m_elsif.groups()[0], is_elsif=True)
                    conditional.append_elsifval(elsifval)
                    dval["conditional"] = elsifval
                elif m_endif:
                    conditional:Conditional = get_conditional()
                    parent = conditional.parent
                    dval["conditional"] = parent if (isinstance(parent, Conditional)) else None
                elif m_state:
                    dval["state"] = State(m_state.groups()[0])
                elif m_end_case:
                    dval["in_state_machine"] = False
                    dval["state"] = None
                    dval["conditional"] = None
                    dval["in_proc"] = False
                    dval["in_combinational"] = False
                    return True
                else:
                    append_lineval(line)

            else: # if dval["in_state_machine"]
                m_case_state_machine = re_case_state_machine.match(lline)

                if m_case_state_machine:
                    dval["in_state_machine"] = True

        else:
            pass

        return False

    def print(self, indent: int = 0):
        for state_name, state in self.states.items():
            state.print(0)

if __name__ == "__main__":
    program = Program("C:/Users/gladc/Documents/School/UNM/ECE_595_intermediate_logic_design/project/vhdl/RenderText.vhd")

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