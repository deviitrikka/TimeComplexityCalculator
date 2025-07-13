import os, ast, streamlit as st
from groq import Client
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Client(api_key=GROQ_API_KEY)

def analyze_ast(code):
    tree = ast.parse(code)
    stats = {"loops":0, "recursion":False}
    class Visitor(ast.NodeVisitor):
        def visit_For(self, node):
            stats["loops"] += 1; self.generic_visit(node)
        def visit_While(self, node):
            stats["loops"] += 1; self.generic_visit(node)
        def visit_FunctionDef(self, node):
            name = node.name
            for call in ast.walk(node):
                if isinstance(call, ast.Call) and hasattr(call.func, "id") and call.func.id == name:
                    stats["recursion"] = True
            self.generic_visit(node)
    Visitor().visit(tree)
    return stats

def estimate_complexity(code):
    ast_info = analyze_ast(code)
    prompt = f'''
You are a time‑complexity expert.

Code:
{code}

AST analysis:
- loops: {ast_info["loops"]}
- recursion: {ast_info["recursion"]}

What is the time complexity? Reply with:
Time Complexity: O(...)
Reason: brief explanation.
'''
    resp = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[{"role":"user", "content": prompt}],
        max_tokens=200,
        temperature=0.0
    )
    return resp.choices[0].message.content

st.title("Time‑Complexity Estimator")
code = st.text_area("Paste your Python code here", height=250)

if st.button("Estimate Complexity"):
    if not code.strip():
        st.error("Please enter some code!")
    else:
        with st.spinner("Analyzing…"):
            try:
                result = estimate_complexity(code)
                st.markdown("**Estimated Complexity:**")
                st.code(result)
            except Exception as e:
                st.error(f"Error: {e}")
