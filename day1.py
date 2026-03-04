import ast
import re

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Calculator", page_icon=":abacus:", layout="centered")


if "expr" not in st.session_state:
    st.session_state.expr = ""
if "just_evaluated" not in st.session_state:
    st.session_state.just_evaluated = False


def press(token: str) -> None:
    if st.session_state.just_evaluated and token.isdigit():
        st.session_state.expr = token
    else:
        st.session_state.expr += token
    st.session_state.just_evaluated = False


def clear_expr() -> None:
    st.session_state.expr = ""
    st.session_state.just_evaluated = False


def backspace() -> None:
    st.session_state.expr = st.session_state.expr[:-1]
    st.session_state.just_evaluated = False


def is_safe_expression(expr: str) -> bool:
    if not expr:
        return False
    if not re.fullmatch(r"[0-9+\-/.() ]", expr):
        return False
    if expr.count("(") != expr.count(")"):
        return False
    return True


def evaluate_expression() -> None:
    expr = st.session_state.expr.strip()

    if not is_safe_expression(expr):
        st.session_state.expr = "Error"
        st.session_state.just_evaluated = True
        return

    try:
        node = ast.parse(expr, mode="eval")
        allowed_nodes = (
            ast.Expression,
            ast.BinOp,
            ast.UnaryOp,
            ast.Add,
            ast.Sub,
            ast.Mult,
            ast.Div,
            ast.UAdd,
            ast.USub,
            ast.Constant,
            ast.Load,
        )
        if any(not isinstance(n, allowed_nodes) for n in ast.walk(node)):
            raise ValueError("Unsupported expression")

        result = eval(compile(node, "<calc>", "eval"), {"_builtins_": {}}, {})
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        st.session_state.expr = str(result)
    except Exception:
        st.session_state.expr = "Error"

    st.session_state.just_evaluated = True


st.title("Calculator", text_alignment = "center")
st.caption("")

input_value = st.text_input(
    "Input",
    value=st.session_state.expr,
    placeholder="",
    label_visibility="collapsed",
)

if input_value != st.session_state.expr:
    st.session_state.expr = input_value
    st.session_state.just_evaluated = False

import streamlit as st

rows = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", " * "],
    ["1", "2", "3", " - "],
    ["0", ".", "=", " + "],
]

for row in rows:
    cols = st.columns(4)
    for i, button in enumerate(row):
        if cols[i].button(str(button)):
            if button == "=":
                evaluate_expression()
            else:
                press(button.strip())
            st.rerun()

action_cols = st.columns(2)
with action_cols[0]:
    if st.button("←", use_container_width=True):
        backspace()
        st.rerun()
with action_cols[1]:
    if st.button("Clear", use_container_width=True):
        clear_expr()
        st.rerun()

components.html(
    """
    <script>
    const doc = window.parent.document;

    function clickByText(text) {
      const buttons = doc.querySelectorAll('button');
      for (const b of buttons) {
        if (b.innerText.trim() === text) {
          b.click();
          return true;
        }
      }
      return false;
    }

    if (!window._calc_key_handler_attached_) {
      doc.addEventListener('keydown', (e) => {
        const key = e.key;

        if (key === "Enter") {
          e.preventDefault();
          clickByText("=");
          return;
        }

        if (key === "Backspace") {
          e.preventDefault();
          clickByText("Backspace");
          return;
        }

        if (key === "Escape") {
          e.preventDefault();
          clickByText("C Clear");
          return;
        }

        const allowed = "0123456789+-*/.";
        if (allowed.includes(key)) {
          e.preventDefault();
          clickByText(key);
        }
      });
      window._calc_key_handler_attached_ = true;
    }
    </script>
    """,
    height=0,
)