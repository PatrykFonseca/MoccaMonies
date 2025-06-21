# File: supabase_client.py
import os
from supabase import create_client, Client

# Configure suas variáveis de ambiente (anon key para operações de usuário):
# SUPABASE_URL e SUPABASE_ANON_KEY
supabase_url: str = os.getenv("SUPABASE_URL")
supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_anon_key:
    raise RuntimeError("Defina SUPABASE_URL e SUPABASE_ANON_KEY no ambiente")

supabase: Client = create_client(supabase_url, supabase_anon_key)


# File: database.py
from supabase_client import supabase

# CONTAS

def add_account(nome: str, saldo: float):
    resp = supabase.table("contas").insert({"nome": nome, "saldo": saldo}).execute()
    return resp.data

def get_accounts():
    resp = supabase.table("contas").select("*").order("id").execute()
    return resp.data

# CATEGORIAS

def get_categories():
    resp = supabase.table("categorias").select("*").order("nome").execute()
    return resp.data

def add_category(nome: str, tipo: str):
    resp = supabase.table("categorias").insert({"nome": nome, "tipo": tipo}).execute()
    return resp.data

# Utility para mapping

def get_or_create_category(nome: str, tipo: str = "Despesa") -> int:
    r = supabase.table("categorias").select("id").eq("nome", nome).execute()
    if r.data:
        return r.data[0]["id"]
    cr = supabase.table("categorias").insert({"nome": nome, "tipo": tipo}).execute()
    return cr.data[0]["id"]

# LANÇAMENTOS

def add_transaction(tipo: str, valor: float, descricao: str, data: str, categoria_id: int):
    resp = supabase.table("lancamentos").insert({
        "tipo": tipo,
        "valor": valor,
        "descricao": descricao,
        "data": data,
        "categoria_id": categoria_id
    }).execute()
    return resp.data

def get_transactions():
    r = supabase.table("lancamentos").select("*, categorias(nome)").order("data", desc=True).execute()
    return r.data

# DÍVIDAS

def add_debt(nome: str, valor: float, data_vencimento: str, juros: float):
    resp = supabase.table("dividas").insert({
        "nome": nome,
        "valor": valor,
        "data_vencimento": data_vencimento,
        "juros": juros
    }).execute()
    return resp.data

def get_debts():
    resp = supabase.table("dividas").select("*").order("data_vencimento").execute()
    return resp.data

# METAS

def add_goal(nome: str, valor: float, data_limite: str):
    resp = supabase.table("metas").insert({
        "nome": nome,
        "valor": valor,
        "data_limite": data_limite
    }).execute()
    return resp.data

def get_goals():
    resp = supabase.table("metas").select("*").order("data_limite").execute()
    return resp.data


# File: app.py (Streamlit com autenticação)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO
import msoffcrypto
from supabase_client import supabase
from database import (
    get_accounts, add_account,
    get_categories, add_category, get_or_create_category,
    get_transactions, add_transaction,
    get_debts, add_debt,
    get_goals, add_goal
)

# Configurações da página
st.set_page_config(page_title="Finanças Casa", layout="wide")

# --- Funções de Autenticação ---
def login():
    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if hasattr(response, "error") and response.error:
            st.error(f"Falha na autenticação: {response.error.message}")
        else:
            data = getattr(response, "data", {})
            session = data.get("session", {})
            user = data.get("user")
            st.session_state.access_token = session.get("access_token")
            st.session_state.user = user
            st.experimental_rerun()


def logout():
    supabase.auth.sign_out()
    st.session_state.clear()
    st.experimental_rerun()

# Verifica sessão
if "access_token" in st.session_state:
    supabase.auth.set_auth(st.session_state.access_token)
    if st.sidebar.button("Logout 🚪"):
        logout()
else:
    login()
    st.stop()

# --- Interface após login ---
st.title("Sistema de Finanças com Supabase + Streamlit")
menu = st.sidebar.selectbox(
    "Navegação", 
    ["Contas", "Categorias", "Lançamentos", "Dívidas", "Metas", "Importar Excel", "Relatórios", "Gráficos"]
)

# ... resto do código permanece inalterado ...
