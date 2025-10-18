import streamlit as st
from datetime import date
import pandas as pd


st.set_page_config(
    page_title="Dashboard PET-Saúde",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Cor de fundo primária (fundo principal e sidebar) */
    .stApp {
        background-color: black; 
    }
    /* Cor primária para botões, sliders, etc. (Azul Claro) */
    :root {
        --primary-color: #87CEFA; /* Light Sky Blue */
    }
    /* Mudar a cor do texto do sidebar para combinar */
    section[data-testid="stSidebar"] div.stButton button {
        background-color: #E0FFFF; /* Azure */
        color: black;
        border: 1px solid #87CEFA;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background-color: #B0E0E6; /* Powder Blue mais escuro no hover */
    }
</style>
""", unsafe_allow_html=True)


# --- INICIALIZAÇÃO DE DADOS E AUTENTICAÇÃO ---

# Inicializa o estado da sessão para autenticação
if 'users' not in st.session_state:
    # Usuários e senhas (apenas para simulação, inseguro para produção)
    st.session_state['users'] = {'admin': 'admin'} 
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

# A estrutura de dados agora é aninhada por usuário
if 'user_data' not in st.session_state:
    # { user_id: { 'pacientes': {cpf: {}}, 'consultas': {cpf: []} } }
    st.session_state['user_data'] = {
        'admin': {'pacientes': {}, 'consultas': {}}
    }
    
# Determina a página inicial
if 'page' not in st.session_state:
    st.session_state['page'] = 'Login'

ESPECIALIDADES = [
    "Clínica Geral",
    "Pediatria",
    "Ginecologia",
    "Cardiologia",
    "Dermatologia",
    "Oftalmologia",
    "Otorrinolaringologia",
    "Neurologia",
    "Ortopedia",
    "Psicologia",
    "Fisioterapia",
    "Outra"
]

# Esquema de vacinação
VACINAS_POR_GRUPO = {
    "Recém-Nascido": [
        "BCG - nascimento (dose única)", "Hepatite B - nascimento (dose única)", "Penta - 2 meses (1ª dose)", 
        "Poliomielite inativada VIP - 2 meses (1ª dose)", "Pneumocócica 10-valente - 2 meses (1ª dose)",
        "Rotavírus Humano - 2 meses (1ª dose)", "Meningocócica C - 3 meses (1ª dose)", "Penta - 4 meses (2ª dose)", 
        "Poliomielite inativada VIP - 4 meses (2ª dose)", "Pneumocócica 10-valente - 4 meses (2ª dose)",
        "Rotavírus Humano - 4 meses (2ª dose)", "Meningocócica C - 5 meses (2ª dose)", 
        "Penta - 6 meses (3ª dose)", "Poliomielite inativada VIP - 6 meses (3ª dose)", "Influenza Trivalente - 6 meses (1ª dose)",
        "Covid-19 - 6 meses (1ª dose)", "Covid-19 - 7 meses (2ª dose)", "Covid-19 - 9 meses (3ª dose)", "Febre Amarela - 9 meses (1ª dose)",
        "Pneumocócica 10-valente - 12 meses (dose reforço)", "Meningocócica ACWY - 12 meses (dose única)", "Tríplice viral SCR - 12 meses (dose única)"
    ],
    "Criança": [
        "Tríplice Viral (12 meses e reforço 4-6 anos)", "Hepatite A (15 meses)",
        "DTP (Difteria, Tétano e Coqueluche) (15 meses e 4 anos)", "Varicela (4 anos)",
        "HPV (9 a 14 anos)"
    ],
    "Adolescentes e Jovens": [
        "HPV4 9-14 anos (dose única)", "Meningocócica ACWY 11-14 anos (dose única)",
        "Hepatite B 10-24 anos (dose tripla)", "Difteria e Tétano (dT) 10-24 anos (dose tripla)",
        "Febre Amarela 10-24 anos (dose única)", "Tríplice Viral SCR 10-24 anos (dose dupla)",
        "Pneumocócica 23-valente 10-24 anos(dose dupla)", "Varicela (dose dupla)"
    ],
    "Adulto": [
        "Difteria e Tétano (dT) (dose tripla)", "Hepatite B (dose tripla)",
        "Tríplice Viral (1 ou 2 doses, a depender do histórico)", "Febre Amarela (dose única, a depender da área de residência)",
        "Pneumocócica 23-valente (dose dupla)", "Varicela (dose dupla)"
    ],
    "Idoso": [
        "Hepatite B (dose tripla)", "Difteria e Tétano (dT) (dose tripla)", "Influenza trivalente (dose anual)", 
        "Pneumocócica 23-valente (dose dupla)", "Febre Amarela (dose única)", 
        "Tríplice Viral SCR (dose dupla)", "Varicela (dose dupla)", "Covid-19 (dose semestral)"
    ]
}

# --- Funções de Lógica e Utilitários ---

def get_user_data():
    """Retorna os dados (pacientes e consultas) do usuário logado."""
    user_id = st.session_state.get('current_user')
    # Se o usuário não estiver logado, retorna um dicionário vazio para evitar erros
    if not user_id or user_id not in st.session_state['user_data']:
        return {'pacientes': {}, 'consultas': {}}
    return st.session_state['user_data'][user_id]

def calcular_idade_e_faixa_etaria(data_nascimento):
    """Calcula a idade e determina a faixa etária do paciente."""
    hoje = date.today()
    idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))

    if idade <= 1:
        faixa = "Recém-Nascido"
    elif 2 <= idade <= 9:
        faixa = "Criança"
    elif 10 <= idade <= 24:
        faixa = "Adolescentes e Jovens"
    elif 25 <= idade <= 59:
        faixa = "Adulto"
    else: # idade >= 60
        faixa = "Idoso"

    return idade, faixa

def is_cpf_valido(cpf):
    """
    Verifica se um CPF (string de 11 dígitos) é matematicamente válido.
    """
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    def calcula_digito(cpf_subset, peso_inicial):
        soma = 0
        for i, digito in enumerate(cpf_subset):
            soma += int(digito) * (peso_inicial - i)
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    digito_1 = calcula_digito(cpf[:9], 10)
    if int(cpf[9]) != digito_1:
        return False

    digito_2 = calcula_digito(cpf[:10], 11)
    if int(cpf[10]) != digito_2:
        return False

    return True

def formatar_cpf(cpf):
    """Formata CPF para exibição (apenas se for 11 dígitos)."""
    if len(cpf) == 11 and cpf.isdigit():
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf


# --- Funções de Autenticação ---

def tela_cadastro_usuario():
    st.header("✨ Cadastro de Novo Usuário")
    st.caption("Crie suas credenciais para gerenciar seus dados de saúde.")

    with st.form("form_cadastro_usuario"):
        new_username = st.text_input("Nome de Usuário (login)", max_chars=20).strip().lower()
        new_password = st.text_input("Senha", type="password", max_chars=30)
        confirm_password = st.text_input("Confirme a Senha", type="password", max_chars=30)
        
        submitted = st.form_submit_button("Criar Conta")

        if submitted:
            if not new_username or not new_password or not confirm_password:
                st.error("Preencha todos os campos.")
            elif new_password != confirm_password:
                st.error("As senhas não coincidem.")
            elif new_username in st.session_state['users']:
                st.error("Nome de usuário já existe.")
            else:
                st.session_state['users'][new_username] = new_password
                
                # Inicializa os dados do novo usuário
                st.session_state['user_data'][new_username] = {
                    'pacientes': {},
                    'consultas': {}
                }
                
                st.success("Usuário cadastrado com sucesso! Redirecionando para o login...")
                st.session_state['page'] = 'Login'
                st.rerun()

def tela_login():
    st.header("🔑 Acesso ao Sistema")
    st.caption("Faça login para acessar seu painel pessoal de saúde.")

    if st.session_state['logged_in']:
        st.success(f"Você já está logado como **{st.session_state['current_user'].title()}**.")
        return

    with st.form("form_login"):
        username = st.text_input("Nome de Usuário").strip().lower()
        password = st.text_input("Senha", type="password")
        
        submitted = st.form_submit_button("Entrar")

        if submitted:
            if username in st.session_state['users'] and st.session_state['users'][username] == password:
                st.session_state['logged_in'] = True
                st.session_state['current_user'] = username
                st.success(f"Bem-vindo, {username.title()}! Redirecionando para o painel...")
                st.session_state['page'] = 'Minha Saúde'
                st.rerun()
            else:
                st.error("Nome de usuário ou senha incorretos.")

def tela_logout():
    st.session_state['logged_in'] = False
    st.session_state['current_user'] = None
    st.session_state['page'] = 'Login'
    st.info("Você foi desconectado.")
    st.rerun()


# --- Funções do Aplicativo Streamlit (Adaptadas para Usuário) ---

def tela_cadastro_paciente():
    """Interface para cadastrar um novo paciente."""
    user_data = get_user_data()
    st.header("👤 Cadastro de Novo Paciente")
    
    data_padrao = date.today().replace(year=date.today().year - 30) # Padrão mais razoável

    with st.form("form_paciente"):
        cpf = st.text_input("CPF (apenas números)", max_chars=11).strip()
        nome = st.text_input("Nome Completo").strip().title()
        data_nascimento = st.date_input(
            "Data de Nascimento", value=data_padrao, max_value=date.today(), format='DD/MM/YYYY'
            )
        cidade = st.text_input("Cidade de Residência").strip().title()

        submitted = st.form_submit_button("Cadastrar Paciente")

        if submitted:
            if not cpf or not nome or not data_nascimento:
                st.error("Preencha todos os campos.")
            elif not cpf.isdigit() or len(cpf) != 11:
                st.error("CPF deve conter 11 dígitos e apenas números.")
            elif not is_cpf_valido(cpf):
                st.error("O CPF informado não é válido. Por favor, verifique.")
            elif cpf in user_data['pacientes']: # Acesso de usuário
                st.error(f"Paciente com CPF {formatar_cpf(cpf)} já cadastrado.")
            else:
                idade, faixa_etaria = calcular_idade_e_faixa_etaria(data_nascimento)
                
                user_data['pacientes'][cpf] = { # Acesso de usuário
                    'nome': nome,
                    'nascimento': data_nascimento,
                    'idade': idade,
                    'faixa_etaria': faixa_etaria,
                    'vacinas_tomadas': [],
                    'cidade': cidade,
                }
                user_data['consultas'][cpf] = [] # Acesso de usuário
                
                # ALTERAÇÃO: Redireciona para a tela Minha Saúde após o sucesso
                st.success(f"Paciente **{nome}** ({faixa_etaria}) cadastrado com sucesso! Redirecionando para Minha Saúde...")
                st.session_state['page'] = 'Minha Saúde'
                st.rerun()

def tela_cadastro_consulta():
    """Interface para cadastrar uma nova consulta."""
    user_data = get_user_data()
    st.header("📝 Agendar Nova Consulta")
    
    pacientes_list = user_data['pacientes'] # Acesso de usuário
    if not pacientes_list:
        st.warning("Nenhum paciente cadastrado. Cadastre um paciente primeiro.")
        return
        
    pacientes_options = {p_cpf: f"{p['nome']} ({formatar_cpf(p_cpf)})" for p_cpf, p in pacientes_list.items()}
    pacientes_display_names = ["Selecione um paciente..."] + list(pacientes_options.values())

    selected_name = st.selectbox("Selecione o Paciente", pacientes_display_names)
    
    if selected_name != "Selecione um paciente...":
        selected_cpf = [cpf for cpf, name in pacientes_options.items() if name == selected_name][0]
        
        with st.form("form_consulta"):
            data_consulta = st.date_input("Data da Consulta", min_value=date.today(), format='DD/MM/YYYY')
            especialidade = st.selectbox("Especialidade", options=ESPECIALIDADES)
            observacoes = st.text_area("Observações").strip()

            submitted = st.form_submit_button("Registrar Consulta")

            if submitted:
                if not especialidade or not observacoes:
                    st.error("Preencha todos os campos da consulta.")
                else:
                    nova_consulta = {
                        'data': data_consulta,
                        'especialidade': especialidade,
                        'observacoes': observacoes
                    }
                    user_data['consultas'][selected_cpf].append(nova_consulta) # Acesso de usuário
                    st.success(f"Consulta registrada para **{user_data['pacientes'][selected_cpf]['nome']}**!") # Acesso de usuário

def tela_visualizar_historico():
    """Interface para visualizar histórico e vacinas."""
    user_data = get_user_data()
    st.header("📋 Histórico e Vacinação")
    
    pacientes_list = user_data['pacientes'] # Acesso de usuário
    if not pacientes_list:
        st.warning("Nenhum paciente cadastrado.")
        return
        
    pacientes_options = {p_cpf: f"{p['nome']} ({formatar_cpf(p_cpf)})" for p_cpf, p in pacientes_list.items()}
    pacientes_display_names = ["Selecione um paciente..."] + list(pacientes_options.values())
    selected_name = st.selectbox("Selecione o Paciente", pacientes_display_names)

    if selected_name != "Selecione um paciente...":
        selected_cpf = [cpf for cpf, name in pacientes_options.items() if name == selected_name][0]
        paciente = user_data['pacientes'][selected_cpf] # Acesso de usuário

        st.subheader(f"Dados de **{paciente['nome']}**")
        st.info(f"Idade: **{paciente['idade']}** anos | Faixa Etária: **{paciente['faixa_etaria']}**")
        
        st.markdown("---")
        
        # --- Seção de Vacinas ---
        st.subheader("💉 Status de Vacinação")
        faixa = paciente['faixa_etaria']
        vacinas_relevantes = VACINAS_POR_GRUPO.get(faixa, [])
        vacinas_tomadas_set = set(paciente['vacinas_tomadas'])
        
        dados_vacinas = []
        for vacina in vacinas_relevantes:
            status = "✅ APLICADA" if vacina in vacinas_tomadas_set else "❌ PENDENTE"
            dados_vacinas.append({"Vacina": vacina, "Status": status})

        if dados_vacinas:
            df_vacinas = pd.DataFrame(dados_vacinas)
            st.dataframe(df_vacinas, hide_index=True, width='stretch')
        else:
            st.write(f"Nenhuma vacina específica listada para a faixa '{faixa}'.")

        st.markdown("---")
        
        # --- Seção de Histórico de Consultas ---
        st.subheader("📜 Histórico de Consultas")
        historico = user_data['consultas'].get(selected_cpf, []) # Acesso de usuário

        if historico:
            df_consultas = pd.DataFrame(historico)
            df_consultas['data'] = pd.to_datetime(df_consultas['data'])
            df_consultas['data'] = df_consultas['data'].dt.strftime('%d/%m/%Y')
            df_consultas = df_consultas.rename(columns={'data': 'Data', 'especialidade': 'Especialidade', 'observacoes': 'Observações'})
            df_consultas = df_consultas.sort_values(by='Data', ascending=False)
            
            st.dataframe(df_consultas, hide_index=True, width='stretch')
        else:
            st.info("Nenhuma consulta registrada para este paciente.")

def tela_registrar_vacina():
    """Interface para registrar vacinas tomadas."""
    user_data = get_user_data()
    
    # O Streamlit renderiza os widgets na ordem. Este está no final da função no código original.
    placeholder_msg = st.empty() 

    if 'vacina_success_message' in st.session_state:
        placeholder_msg.success(st.session_state['vacina_success_message'])
        del st.session_state['vacina_success_message']

    st.header("✅ Registrar Vacina Tomada")
    
    pacientes_list = user_data['pacientes'] # Acesso de usuário
    if not pacientes_list:
        st.warning("Nenhum paciente cadastrado.")
        return
    
    pacientes_options = {p_cpf: f"{p['nome']} ({formatar_cpf(p_cpf)})" for p_cpf, p in pacientes_list.items()}
    pacientes_display_names = ["Selecione um paciente..."] + list(pacientes_options.values())
    selected_name = st.selectbox("Selecione o Paciente", pacientes_display_names, key='select_pac_reg_vac')

    if selected_name != "Selecione um paciente...":
        selected_cpf = [cpf for cpf, name in pacientes_options.items() if name == selected_name][0]
        paciente = user_data['pacientes'][selected_cpf] # Acesso de usuário
        
        faixa = paciente['faixa_etaria']
        vacinas_relevantes = VACINAS_POR_GRUPO.get(faixa, [])
        vacinas_tomadas_set = set(paciente['vacinas_tomadas'])
        
        pendentes_list = [v for v in vacinas_relevantes if v not in vacinas_tomadas_set]

        if not pendentes_list:
            st.success(f"Todas as vacinas relevantes para '{faixa}' já estão registradas como tomadas para **{paciente['nome']}**.")
            return

        st.subheader(f"Vacinas Pendentes para **{paciente['nome']}** ({faixa})")
        st.markdown("Marque as vacinas que foram **administradas**:")

        vacinas_para_registrar = []
        for vacina in pendentes_list:
            if st.checkbox(vacina, key=f"vac_check_{vacina}"): 
                vacinas_para_registrar.append(vacina)

        if st.button("Confirmar Registro de Vacinas"):
            if vacinas_para_registrar:
                for v in vacinas_para_registrar:
                    user_data['pacientes'][selected_cpf]['vacinas_tomadas'].append(v) # Acesso de usuário
                
                st.session_state['vacina_success_message'] = (
                    f"✅ **{len(vacinas_para_registrar)}** vacina(s) registrada(s) com sucesso "
                    f"para **{paciente['nome']}**!"
                )
                
                st.rerun()
            else:
                st.warning("Selecione pelo menos uma vacina para registrar.")

def tela_dashboard():
    """
    Dashboard de Indicadores de Saúde.
    Apresenta apenas dados anonimizados e agregados DO USUÁRIO logado.
    """
    user_data = get_user_data()
    st.header(f"📊 Dashboard Pessoal de Saúde - {st.session_state['current_user'].title()}")
    st.caption("Visualize indicadores dos pacientes que você gerencia. **Dados do usuário logado.**")
    st.markdown("---")

    pacientes_data = user_data['pacientes'] # Acesso de usuário
    consultas_data = user_data['consultas'] # Acesso de usuário

    # 1. Preparação dos Dados Anonimizados
    
    if pacientes_data:
        # Transforma o dicionário de pacientes do usuário em um DataFrame
        pacientes_df = pd.DataFrame(pacientes_data).T.reset_index(names=['cpf'])
        pacientes_anon_df = pacientes_df[['idade', 'faixa_etaria', 'cidade']].copy()
        pacientes_anon_df['cidade'] = pacientes_anon_df['cidade'].fillna('Não Informada')
    else:
        pacientes_anon_df = pd.DataFrame(columns=['idade', 'faixa_etaria', 'cidade'])

    # 2. Key Metrics (Indicadores Chave)
    
    total_pacientes = len(pacientes_data)
    total_consultas = sum(len(c) for c in consultas_data.values())

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total de Pacientes Cadastrados", total_pacientes)
    col2.metric("Total de Consultas Registradas", total_consultas)
    
    if total_pacientes > 0:
        pacientes_vacinados = sum(1 for p in pacientes_data.values() if p.get('vacinas_tomadas'))
        cobertura_perc = (pacientes_vacinados / total_pacientes) * 100 if total_pacientes else 0
        col3.metric("Pacientes com Vacinas Registradas", f"{pacientes_vacinados} de {total_pacientes}", delta=f"{cobertura_perc:.1f}%")
        
        media_idade = pacientes_anon_df['idade'].mean() if not pacientes_anon_df.empty else 0
        col4.metric("Média de Idade dos Pacientes", f"{media_idade:.1f} anos")
    
    st.markdown("---")
    
    col_faixa, col_cidade = st.columns(2)
    
    # 3.1. Distribuição por Faixa Etária
    with col_faixa:
        st.subheader("Distribuição de Pacientes por Faixa Etária")
        if not pacientes_anon_df.empty:
            contagem_faixa = pacientes_anon_df['faixa_etaria'].value_counts().reset_index()
            contagem_faixa.columns = ['Faixa Etária', 'Total']
            st.bar_chart(contagem_faixa, x='Faixa Etária', y='Total')
        else:
            st.info("Cadastre pacientes para visualizar esta distribuição.")

    # 3.2 Cidade de Origem
    with col_cidade:
        st.subheader("Origem dos Pacientes por Cidade de Residência")
        if not pacientes_anon_df.empty:
            contagem_cidade = pacientes_anon_df['cidade'].value_counts().reset_index()
            contagem_cidade.columns = ['Cidade', 'Total']
            st.bar_chart(contagem_cidade.head(10), x='Cidade', y='Total')
        else:
            st.info("Cadastre pacientes com a cidade de residência para visualizar a distribuição.")

    st.markdown("---")
    
    # 3.3. Consultas por Especialidade
    st.subheader("Consultas Agendadas por Especialidade")
    if total_consultas > 0:
        todas_consultas = []
        for cpf, consultas in consultas_data.items():
            for c in consultas:
                todas_consultas.append({'especialidade': c['especialidade']})
        
        consultas_df = pd.DataFrame(todas_consultas)
        
        contagem_especialidade = consultas_df['especialidade'].value_counts().reset_index()
        contagem_especialidade.columns = ['Especialidade', 'Contagem']
        
        st.dataframe(contagem_especialidade, width='stretch', hide_index=True)
    else:
        st.info("Registre consultas para visualizar esta distribuição.")

def tela_faq():
    """
    Página de Dúvidas Frequentes (FAQ) sobre o Sistema e as Regras de Saúde.
    """
    st.header("❓ Dúvidas Frequentes (FAQ)")
    st.caption("Encontre aqui respostas para as questões mais comuns sobre o uso do sistema e a lógica de saúde.")
    st.markdown("---")

    # ----------------------------------------
    # SEÇÃO 1: SOBRE O SISTEMA E CADASTRO
    # ----------------------------------------
    st.subheader("1. Uso do Sistema")

    with st.expander("Como a idade e a faixa etária são calculadas?"):
        st.markdown(
            """
            A idade é calculada automaticamente com base na Data de Nascimento informada e a data de hoje. 
            A faixa etária é determinada com base na idade, conforme as diretrizes do Programa de Saúde:
            * **Recém-Nascido:** 0 a 1 ano
            * **Criança:** 2 a 9 anos
            * **Adolescentes e Jovens:** 10 a 24 anos
            * **Adulto:** 25 a 59 anos
            * **Idoso:** 60 anos ou mais
            """
        )
        
    with st.expander("Este sistema armazena meus dados de forma segura?"):
        st.markdown(
            """
            **ATENÇÃO:** Esta aplicação Streamlit é um protótipo e utiliza a memória do seu navegador (`st.session_state`) para armazenar dados.
            * **Segurança:** Embora os dados sejam segregados por usuário logado, eles não são criptografados nem persistidos em um banco de dados real.
            * **Produção:** Para uma solução real de multiusuário, seria necessário integrar um banco de dados seguro (como Firebase Firestore ou outro) e implementar criptografia de senha robusta.
            """
        )

    with st.expander("O que devo fazer se o paciente estiver em uma faixa etária de transição?"):
        st.markdown(
            """
            O sistema faz uma classificação estrita. Se o paciente acabou de completar a idade de transição (ex: 10 anos, passando de Criança para Adolescente/Jovem), o sistema exibirá o calendário da nova faixa. O profissional deve sempre verificar se todas as doses da faixa etária anterior foram concluídas.
            """
        )
        
    st.markdown("---")

    # ----------------------------------------
    # SEÇÃO 2: SOBRE O CARTÃO DE VACINA
    # ----------------------------------------
    st.subheader("2. Vacinação e Informações de Saúde")

    with st.expander("De onde vêm as vacinas sugeridas no Cartão de Vacina?"):
        st.markdown(
            """
            As vacinas sugeridas são baseadas nos esquemas vacinais do Calendário Vacinal do **Ministério da Saúde** e são filtradas pela faixa etária do paciente. Elas representam as vacinas que são tipicamente 
            necessárias para aquele grupo etário.
            """
        )

    with st.expander("O status [PENDENTE] significa que a vacina está atrasada?"):
        st.markdown(
            """
            O status **[PENDENTE]** significa apenas que a vacina é **relevante para a faixa etária do paciente e ainda não foi marcada como aplicada no sistema**. 
            Para saber se uma vacina está **atrasada**, o profissional de saúde deve cruzar esta informação 
            com a idade atual do paciente e o calendário oficial de doses (ex: "1ª dose aos 2 meses").
            """
        )

    with st.expander("Por que não vejo nomes ou CPFs no Dashboard?"):
        st.markdown(
            """
            O Dashboard Pessoal exibe apenas dados **agregados e anonimizados** (como contagem de pacientes por cidade ou especialidade) dos pacientes que você cadastrou. Isso serve como um resumo gerencial da sua coorte de pacientes.
            """
        )


# --- Menu Principal (Sidebar) ---

st.sidebar.title("🏥 PET Saúde - GT09")

if st.session_state['logged_in']:
    st.sidebar.markdown(f"**Usuário Ativo:** **{st.session_state['current_user'].title()}**")
    st.sidebar.markdown("---")
    
    menu_options = {
        "Minha Saúde": tela_visualizar_historico,
        "Registrar Vacina": tela_registrar_vacina,
        "Agendar Consulta": tela_cadastro_consulta,
        "Cadastro de Paciente": tela_cadastro_paciente,
        "Dashboard Pessoal" : tela_dashboard,
        "Dúvidas Frequentes (FAQ)" : tela_faq,
        "Sair (Logout)": tela_logout,
    }
    
    # Define a seleção baseada na última página acessada ou 'Minha Saúde'
    default_page = 'Minha Saúde'
    if st.session_state['page'] in menu_options:
         default_index = list(menu_options.keys()).index(st.session_state['page'])
    else:
         default_index = list(menu_options.keys()).index(default_page)
         st.session_state['page'] = default_page
         
    selection = st.sidebar.radio("Navegação", list(menu_options.keys()), index=default_index)
    st.session_state['page'] = selection

else: # Não logado
    st.sidebar.markdown("---")
    st.sidebar.markdown("Faça login para começar.")
    
    menu_options = {
        "Login": tela_login,
        "Criar Conta": tela_cadastro_usuario,
        "FAQ Público": tela_faq,
    }
    
    # Define a seleção baseada na última página acessada ou 'Login'
    default_page = 'Login'
    if st.session_state['page'] in menu_options:
         default_index = list(menu_options.keys()).index(st.session_state['page'])
    else:
         default_index = list(menu_options.keys()).index(default_page)
         st.session_state['page'] = default_page
         
    selection = st.sidebar.radio("Navegação", list(menu_options.keys()), index=default_index)
    st.session_state['page'] = selection
         
# Executa a função da tela selecionada
menu_options[selection]()
