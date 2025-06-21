# File: app.py

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
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                st.session_state.access_token = response.session.access_token
                st.session_state.refresh_token = response.session.refresh_token
                st.session_state.user = response.user
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Credenciais inválidas")
        except Exception as e:
            st.error(f"Erro na autenticação: {str(e)}")

def logout():
    try:
        supabase.auth.sign_out()
    except:
        pass  # Ignore errors during sign out
    st.session_state.clear()
    st.rerun()

# Verifica sessão
if "access_token" in st.session_state and "user" in st.session_state:
    # Set the session using the stored access token and user info
    try:
        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
    except:
        # Alternative method if set_session doesn't work
        supabase.postgrest.auth(st.session_state.access_token)
    
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

if menu == "Contas":
    st.header("Contas")
    df = pd.DataFrame(get_accounts())
    st.table(df)
    with st.form("frm_conta", clear_on_submit=True):
        nome = st.text_input("Nome da conta")
        saldo = st.number_input("Saldo inicial", value=0.0)
        if st.form_submit_button("Adicionar conta"):
            add_account(nome, saldo)
            st.success("Conta adicionada com sucesso!")
            st.rerun()

elif menu == "Categorias":
    st.header("Categorias")
    df = pd.DataFrame(get_categories())
    st.table(df)
    with st.form("frm_cat", clear_on_submit=True):
        nome = st.text_input("Nome da categoria")
        tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
        if st.form_submit_button("Adicionar categoria"):
            add_category(nome, tipo)
            st.success("Categoria adicionada com sucesso!")
            st.rerun()

elif menu == "Lançamentos":
    st.header("Lançamentos")
    trans = get_transactions()
    df = pd.DataFrame(trans)
    if not df.empty:
        if not df.empty:
    # categoria
    df['categoria'] = df['categorias'].apply(lambda x: x.get('nome') if isinstance(x, dict) else None)
    # tipo de categoria (Receita/Despesa)
    df['tipo_categoria'] = df['categorias'].apply(lambda x: x.get('tipo') if isinstance(x, dict) else None)
    # conta
    df['conta'] = df['contas'].apply(lambda x: x.get('conta_nome') if isinstance(x, dict) else None)

    st.dataframe(df[[
        'id', 'valor', 'descricao', 'data', 'categoria',
        'tipo_categoria', 'conta', 'user_id', 'criado_em'
    ]])

    with st.form("frm_lanc", clear_on_submit=True):
        valor = st.number_input("Valor", value=0.0)
        descricao = st.text_input("Descrição")
        data = st.date_input("Data", value=datetime.today()).strftime('%Y-%m-%d')
        # Seleção de conta
        contas = get_accounts()
        conta_opts = {c['nome']: c['id'] for c in contas}
        conta_sel = st.selectbox("Conta", list(conta_opts.keys()))
        # Seleção de categoria
        cats = get_categories()
        cat_opts = {c['nome']: c['id'] for c in cats}
        cat_sel = st.selectbox("Categoria", list(cat_opts.keys()))
        if st.form_submit_button("Adicionar lançamento"):
            user_id = st.session_state.user.get('id')
            add_transaction(
                valor, descricao, data,
                cat_opts[cat_sel], conta_opts[conta_sel], user_id
            )
            st.success("Lançamento adicionado com sucesso!")
            st.experimental_rerun()

elif menu == "Dívidas":
    st.header("Dívidas")
    df = pd.DataFrame(get_debts())
    st.table(df)
    with st.form("frm_div", clear_on_submit=True):
        nome = st.text_input("Nome da dívida")
        valor = st.number_input("Valor da dívida", value=0.0)
        data_v = st.date_input("Data de vencimento", value=datetime.today()).strftime('%Y-%m-%d')
        juros = st.number_input("Juros (%)", value=0.0)
        if st.form_submit_button("Adicionar dívida"):
            add_debt(nome, valor, data_v, juros)
            st.success("Dívida adicionada com sucesso!")
            st.rerun()

elif menu == "Metas":
    st.header("Metas")
    df = pd.DataFrame(get_goals())
    st.table(df)
    with st.form("frm_meta", clear_on_submit=True):
        nome = st.text_input("Nome da meta")
        valor = st.number_input("Valor alvo", value=0.0)
        data_l = st.date_input("Data limite", value=datetime.today()).strftime('%Y-%m-%d')
        if st.form_submit_button("Adicionar meta"):
            add_goal(nome, valor, data_l)
            st.success("Meta adicionada com sucesso!")
            st.rerun()

elif menu == "Importar Excel":
    st.header("Importar Excel C6Bank")
    file = st.file_uploader("Selecione o arquivo Excel (.xls/.xlsx)", type=["xls", "xlsx"])
    senha = st.text_input("Senha do arquivo", type="password")
    if st.button("Importar"):
        if file and senha:
            try:
                arquivo = msoffcrypto.OfficeFile(file)
                arquivo.load_key(password=senha)
                buf = BytesIO()
                arquivo.decrypt(buf)
                buf.seek(0)
                df = pd.read_excel(buf, skiprows=1)
                df.columns = df.columns.str.strip().str.replace(r'\n', ' ', regex=True)
                col_val = [c for c in df.columns if "Valor" in c and "(em R$)" in c]
                if not col_val:
                    st.error("Coluna 'Valor (em R$)' não encontrada")
                else:
                    col_val = col_val[0]
                    df[col_val] = pd.to_numeric(
                        df[col_val].astype(str).str.replace('[R$,\s]', '', regex=True),
                        errors='coerce'
                    ).fillna(0).abs()
                    df['Tipo'] = df[col_val].apply(lambda x: 'Despesa' if x > 0 else 'Receita')
                    df['Data'] = pd.to_datetime(
                        df['Data de compra'], dayfirst=True, errors='coerce'
                    ).dt.strftime('%Y-%m-%d')
                    df['CategoriaName'] = df.get('Categoria', 'Sem categoria')
                    df['Descrição'] = df.get('Descrição', '')
                    for _, row in df.iterrows():
                        cat_id = get_or_create_category(row['CategoriaName'])
                        add_transaction(row['Tipo'], row[col_val], row['Descrição'], row['Data'], cat_id)
                    st.success("Importação concluída com sucesso!")
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao importar: {e}")
        else:
            st.warning("Arquivo e senha são obrigatórios")

elif menu == "Relatórios":
    st.header("Relatórios Mensais")
    trans = get_transactions()
    df = pd.DataFrame(trans)
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'])
        anos = df['data'].dt.year.unique().tolist()
        meses = list(range(1, 13))
        sel_ano = st.selectbox("Ano", sorted(anos))
        sel_mes = st.selectbox("Mês", meses)
        dff = df[(df['data'].dt.year == sel_ano) & (df['data'].dt.month == sel_mes)]
        st.dataframe(dff)
        towrite = BytesIO()
        dff.to_excel(towrite, index=False, sheet_name=f"{sel_mes}-{sel_ano}")
        towrite.seek(0)
        st.download_button(
            "Baixar Excel",
            data=towrite,
            file_name=f"relatorio_{sel_mes}_{sel_ano}.xlsx"
        )
    else:
        st.info("Nenhum lançamento encontrado.")

elif menu == "Gráficos":
    st.header("Gráficos de Receitas x Despesas")
    trans = get_transactions()
    df = pd.DataFrame(trans)
    if not df.empty:
        resumo = df.groupby('tipo')['valor'].sum().reset_index()
        fig, ax = plt.subplots()
        ax.pie(resumo['valor'], labels=resumo['tipo'], autopct='%1.1f%%', startangle=90)
        ax.set_title('Distribuição Receitas vs Despesas')
        st.pyplot(fig)
    else:
        st.info("Nenhum dado para plotar.")