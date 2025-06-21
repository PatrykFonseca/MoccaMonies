
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
    r = supabase.table("lancamentos").select("*, categorias(nome),contas(nome)").order("data", desc=True).execute()
    # Supabase retorna relacionamentos em 'categorias'
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

