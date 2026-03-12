import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Simulatore finanziamento",
    page_icon="💶",
    layout="wide"
)

# ---------- LOGIN ----------
def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return True

    st.title("🔐 Accesso")
    st.write("Inserisci le credenziali per accedere al simulatore.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Accedi")

        if submitted:
            saved_user = st.secrets["auth"]["username"]
            saved_pass = st.secrets["auth"]["password"]

            if username == saved_user and password == saved_pass:
                st.session_state.logged_in = True
                st.success("Accesso effettuato con successo.")
                st.rerun()
            else:
                st.error("Username o password non corretti.")

    return False


def logout_button():
    with st.sidebar:
        st.markdown("### Account")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()


if not check_login():
    st.stop()

logout_button()

# ---------- CSS ----------
st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.card {
    background-color: white;
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid #e6e9ef;
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
}

.title {
    font-size: 2.3rem;
    font-weight: 700;
}

.subtitle {
    color: #6b7280;
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<div class="title">💶 Simulatore Finanziamento</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Piano di ammortamento alla francese</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.5], gap="large")

# ---------- INPUT ----------
with col1:
    st.subheader("Parametri")

    importo_fin = st.number_input(
        "Importo finanziato",
        min_value=0.0,
        max_value=500000.0,
        value=20000.0,
        step=500.0
    )

    manutenzione = st.number_input(
        "Manutenzione",
        min_value=0.0,
        max_value=50000.0,
        value=1000.0,
        step=100.0
    )

    assicurazione = st.number_input(
        "Assicurazione",
        min_value=0.0,
        max_value=50000.0,
        value=1000.0,
        step=100.0
    )

    tasso_annuo = st.number_input(
        "Tasso annuo (%)",
        min_value=0.0,
        max_value=20.0,
        value=5.0,
        step=0.1
    )

    durata_mesi = st.number_input(
        "Durata (mesi)",
        min_value=1,
        max_value=360,
        value=60,
        step=12
    )

    capitale = importo_fin + manutenzione + assicurazione

    st.divider()

    st.metric("💰 Capitale totale", f"{capitale:,.2f} €")

# ---------- CALCOLI ----------
tasso_mensile = tasso_annuo / 100 / 12

if tasso_mensile == 0:
    rata = capitale / durata_mesi
else:
    rata = capitale * (tasso_mensile * (1 + tasso_mensile) ** durata_mesi) / ((1 + tasso_mensile) ** durata_mesi - 1)

residuo = capitale
righe = []

for mese in range(1, durata_mesi + 1):
    interessi = residuo * tasso_mensile
    quota_capitale = rata - interessi

    if mese == durata_mesi:
        quota_capitale = residuo
        rata_effettiva = quota_capitale + interessi
    else:
        rata_effettiva = rata

    residuo -= quota_capitale

    righe.append({
        "Mese": mese,
        "Rata (€)": round(rata_effettiva, 2),
        "Quota interessi (€)": round(interessi, 2),
        "Quota capitale (€)": round(quota_capitale, 2),
        "Debito residuo (€)": round(max(residuo, 0), 2)
    })

tabella = pd.DataFrame(righe)

interessi_tot = tabella["Quota interessi (€)"].sum()
costo_totale = capitale + interessi_tot

# ---------- OUTPUT ----------
with col2:
    st.subheader("Risultato")

    m1, m2, m3 = st.columns(3)

    m1.metric("Rata mensile", f"{rata:,.2f} €")
    m2.metric("Interessi totali", f"{interessi_tot:,.2f} €")
    m3.metric("Costo totale", f"{costo_totale:,.2f} €")

    st.divider()

    st.dataframe(
        tabella,
        use_container_width=True,
        hide_index=True
    )