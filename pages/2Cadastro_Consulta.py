import streamlit as st
from datetime import date
from utils import ESPECIALIDADES

st.set_page_config(
    page_title="Dashboard PET-Saúde",
    layout="wide",
    initial_sidebar_state="expanded"
)

def tela_cadastro_consulta():
    """Interface para cadastrar uma nova consulta para o usuário logado."""
    st.header("📝 Agendar Nova Consulta")
    
    selected_cpf = st.session_state.get('cpf_logado')
    selected_name = st.session_state.get('nome_usuario')

    if not selected_cpf:
        st.error("Faça login para registrar consultas.")
        return
        
    st.info(f"Registrando nova consulta para: **{selected_name}**")
    
    with st.form("form_consulta"):
        # min_value=date.today() impede agendamentos no passado
        data_consulta = st.date_input("Data da Consulta", min_value=date.today(), format='DD/MM/YYYY')
        especialidade = st.selectbox("Especialidade", options=ESPECIALIDADES)
        observacoes = st.text_area("Observações (Motivo da consulta)").strip()

        submitted = st.form_submit_button("Registrar Consulta")

        if submitted:
            if not especialidade or not observacoes:
                st.error("Preencha a especialidade e as observações.")
            else:
                nova_consulta = {
                    'data': data_consulta,
                    'especialidade': especialidade,
                    'observacoes': observacoes
                }
                # Salva a consulta no CPF do usuário logado
                st.session_state['consultas'][selected_cpf].append(nova_consulta)
                st.success(f"Consulta registrada com sucesso!")

# Verifica se o usuário está logado
if st.session_state.get('status_login', False):
    tela_cadastro_consulta()
else:
    st.error("Faça login para acessar esta página.")