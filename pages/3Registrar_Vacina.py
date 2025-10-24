import streamlit as st
from utils import VACINAS_POR_GRUPO

st.set_page_config(
    page_title="Dashboard PET-Saúde",
    layout="wide",
    initial_sidebar_state="expanded"
)

def tela_registrar_vacina():
    """Interface para registrar vacinas tomadas."""
    
    st.header("✅ Registrar Vacina Tomada")
    
    selected_cpf = st.session_state.get('cpf_logado')

    if not selected_cpf:
        st.error("Faça login para registrar vacinas.")
        placeholder_msg = st.empty()
        return
    
    # Busca os dados do usuário/paciente
    paciente = st.session_state['usuarios'][selected_cpf]
    
    faixa = paciente['faixa_etaria']
    vacinas_relevantes = VACINAS_POR_GRUPO.get(faixa, [])
    vacinas_tomadas_set = set(paciente['vacinas_tomadas'])
    
    pendentes_list = [v for v in vacinas_relevantes if v not in vacinas_tomadas_set]

    if not pendentes_list:
        st.success(f"Todas as vacinas relevantes para '{faixa}' já estão registradas como tomadas.")
        placeholder_msg = st.empty() 
        return

    st.subheader(f"Vacinas Pendentes para sua faixa etária ({faixa})")
    st.markdown("Marque as vacinas que foram **administradas**:")

    vacinas_para_registrar = []
    for vacina in pendentes_list:
        if st.checkbox(vacina, key=f"vac_check_{vacina}"): 
            vacinas_para_registrar.append(vacina)

    # Botão de confirmação
    if st.button("Confirmar Registro de Vacinas"):
        if vacinas_para_registrar:
            for v in vacinas_para_registrar:
                st.session_state['usuarios'][selected_cpf]['vacinas_tomadas'].append(v)
            
            st.session_state['vacina_success_message'] = (
                f"✅ **{len(vacinas_para_registrar)}** vacina(s) registrada(s) com sucesso!"
            )
            st.rerun()
        else:
            st.warning("Selecione pelo menos uma vacina para registrar.")

    # Placeholder para mensagens de sucesso
    placeholder_msg = st.empty() 
    if 'vacina_success_message' in st.session_state:
        placeholder_msg.success(st.session_state['vacina_success_message'])
        del st.session_state['vacina_success_message']

# Verifica se o usuário está logado
if st.session_state.get('status_login', False):
    tela_registrar_vacina()
else:
    st.error("Faça login para acessar esta página.")