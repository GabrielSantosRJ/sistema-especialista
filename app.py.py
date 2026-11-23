from html import escape
import streamlit as st
from engine import executar_inferencia

st.set_page_config(
    page_title="DermaTech | Triagem Inicial (MVP)",
    page_icon="✳",
    layout="wide",
)

st.markdown(
    """
<style>
:root{--paper:#f7f6f1;--ink:#25372f;--forest:#29463a;--line:#e4e2d9;--white:#fffefa;}
.stApp{background:var(--paper);color:var(--ink);}
.hero{background:linear-gradient(120deg,#e8e9df,#f7f3eb);border:1px solid var(--line);border-radius:18px;padding:1.5rem;margin-bottom:1.2rem;}
.card{background:var(--white);border:1px solid var(--line);border-radius:14px;padding:1rem 1.2rem;margin:.5rem 0;}
.status-banner{border-radius:12px;padding:.9rem 1.1rem;margin:.8rem 0;font-weight:700;color:#fff;}
.status-banner.success{background:#173f32;}
.status-banner.error{background:#873d43;}
</style>
""",
    unsafe_allow_html=True,
)

COMPLAINTS = [
    "Acne e oleosidade", "Manchas e melasma", "Linhas e rugas",
    "Firmeza e flacidez da pele", "Ressecamento da pele", "Sensibilidade e vermelhidão",
    "Poros dilatados e textura irregular", "Olheiras", "Cicatrizes de acne",
    "Cuidados preventivos", "Outras queixas",
]

if "result" not in st.session_state:
    st.session_state.result = None

st.markdown(
    '<div class="hero"><h1>✳ DermaTech — Triagem Inicial</h1>'
    '<p>Responda às perguntas abaixo para obter um encaminhamento inicial.</p></div>',
    unsafe_allow_html=True,
)

with st.form("mvp_triage_form"):
    c1, c2 = st.columns(2)
    with c1:
        queixa = st.selectbox("Qual é sua principal queixa?", COMPLAINTS)
        gravidade = st.selectbox("Como você descreveria o incômodo?", ["Leve", "Moderada", "Intensa"])
        duracao = st.selectbox(
            "Há quanto tempo percebe essa queixa?",
            ["Até 3 meses", "De 3 a 6 meses", "Mais de 6 meses", "Não sei informar"],
        )
    with c2:
        sensibilidade = st.selectbox("Sua pele costuma apresentar sensibilidade?", ["Não", "Sim", "Não sei informar"])
        alergia = st.selectbox("Possui alergias conhecidas?", ["Não", "Sim", "Não sei informar"])
        avaliacao_anterior = st.selectbox("Já realizou avaliação profissional para essa queixa?", ["Não", "Sim"])

    submitted = st.form_submit_button("Analisar respostas", use_container_width=True)

if submitted:
    facts_input = {
        "queixa": queixa,
        "gravidade": gravidade,
        "duracao": duracao,
        "sensibilidade": sensibilidade,
        "alergia": alergia,
        "avaliacao_anterior": avaliacao_anterior,
    }
    st.session_state.result = executar_inferencia(facts_input)

if st.session_state.result:
    res = st.session_state.result
    fatos = res["fatos"]
    st.markdown("---")
    if not res.get("conclusao") or not fatos.get("area"):
        st.markdown('<div class="status-banner error">Não foi possível concluir com os dados informados.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-banner success">Triagem concluída: encaminhamento inicial identificado.</div>', unsafe_allow_html=True)
        st.subheader(res["conclusao"])
        st.write(f"**Área sugerida:** {fatos.get('area')}")
        st.write(f"**Profissional de referência:** {fatos.get('profissional')}")
        st.write(f"**Prioridade:** {fatos.get('prioridade', 'Rotina')}")

        st.markdown("#### Regras acionadas")
        for rule in res["regras"]:
            st.markdown(
                f'<div class="card"><b>{escape(rule["id"])} — {escape(rule["descricao"])}</b><br>'
                f'<small>Condição: <code>{escape(rule["condicao"])}</code> | Fator heurístico: {rule["cf"]:.0%}</small></div>',
                unsafe_allow_html=True,
            )