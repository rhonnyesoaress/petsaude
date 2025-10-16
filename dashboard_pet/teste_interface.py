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


# Inicializa o estado da sessão para armazenar os dados
if 'pacientes' not in st.session_state:
    st.session_state['pacientes'] = {}
if 'consultas' not in st.session_state:
    st.session_state['consultas'] = {}

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

# Adicione esta função junto das suas funções utilitárias (como formatar_cpf)

def is_cpf_valido(cpf):
    """
    Verifica se um CPF (string de 11 dígitos) é matematicamente válido.
    Não verifica se o CPF existe na Receita Federal, apenas a validade formal.
    """
    # 1. Remove caracteres não numéricos e verifica o tamanho
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11:
        return False

    # 2. Verifica CPFs inválidos conhecidos (todos iguais)
    if cpf == cpf[0] * 11:
        return False

    # 3. Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    digito_1 = 0 if resto < 2 else 11 - resto

    # 4. Verifica o primeiro dígito
    if int(cpf[9]) != digito_1:
        return False

    # 5. Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    digito_2 = 0 if resto < 2 else 11 - resto

    # 6. Verifica o segundo dígito
    if int(cpf[10]) != digito_2:
        return False

    return True

# O restante das funções utilitárias (formatar_cpf, calcular_idade_e_faixa_etaria) ...

def formatar_cpf(cpf):
    """Formata CPF para exibição (apenas se for 11 dígitos)."""
    if len(cpf) == 11 and cpf.isdigit():
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf


# --- Funções do Aplicativo Streamlit ---

def tela_cadastro_paciente():
    """Interface para cadastrar um novo paciente."""
    st.header("👤 Cadastro de Novo Paciente")
    
    data_padrao = date.today().replace(year=date.today().year - 100)

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
            elif cpf in st.session_state['pacientes']:
                st.error(f"Paciente com CPF {formatar_cpf(cpf)} já cadastrado.")
            else:
                idade, faixa_etaria = calcular_idade_e_faixa_etaria(data_nascimento)
                
                st.session_state['pacientes'][cpf] = {
                    'nome': nome,
                    'nascimento': data_nascimento,
                    'idade': idade,
                    'faixa_etaria': faixa_etaria,
                    'vacinas_tomadas': [],
                    'cidade': cidade,
                }
                st.session_state['consultas'][cpf] = []
                st.success(f"Paciente **{nome}** ({faixa_etaria}) cadastrado com sucesso!")
                
def tela_cadastro_consulta():
    """Interface para cadastrar uma nova consulta."""
    st.header("📝 Agendar Nova Consulta")
    
    pacientes_list = st.session_state['pacientes']
    if not pacientes_list:
        st.warning("Nenhum paciente cadastrado. Cadastre um paciente primeiro.")
        return
        
    # Cria uma lista de opções para o selectbox
    pacientes_options = {p_cpf: f"{p['nome']} ({formatar_cpf(p_cpf)})" for p_cpf, p in pacientes_list.items()}
    pacientes_display_names = ["Selecione um paciente..."] + list(pacientes_options.values())

    selected_name = st.selectbox("Selecione o Paciente", pacientes_display_names)
    
    if selected_name != "Selecione um paciente...":
        # Encontra o CPF correspondente ao nome selecionado
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
                    st.session_state['consultas'][selected_cpf].append(nova_consulta)
                    st.success(f"Consulta registrada para **{st.session_state['pacientes'][selected_cpf]['nome']}**!")

def tela_visualizar_historico():
    """Interface para visualizar histórico e vacinas."""
    st.header("📋 Histórico e Vacinação")
    
    pacientes_list = st.session_state['pacientes']
    if not pacientes_list:
        st.warning("Nenhum paciente cadastrado.")
        return
        
    pacientes_options = {p_cpf: f"{p['nome']} ({formatar_cpf(p_cpf)})" for p_cpf, p in pacientes_list.items()}
    pacientes_display_names = ["Selecione um paciente..."] + list(pacientes_options.values())
    selected_name = st.selectbox("Selecione o Paciente", pacientes_display_names)

    if selected_name != "Selecione um paciente...":
        selected_cpf = [cpf for cpf, name in pacientes_options.items() if name == selected_name][0]
        paciente = st.session_state['pacientes'][selected_cpf]

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
        historico = st.session_state['consultas'].get(selected_cpf, [])

        if historico:
            # Converte para DataFrame para visualização em tabela
            df_consultas = pd.DataFrame(historico)
            df_consultas['data'] = pd.to_datetime(df_consultas['data'])
            df_consultas['data'] = df_consultas['data'].dt.strftime('%d/%m/%Y')
            df_consultas = df_consultas.rename(columns={'data': 'Data', 'especialidade': 'Especialidade', 'observacoes': 'Observações'})
            # Ordena da mais recente para a mais antiga
            df_consultas = df_consultas.sort_values(by='Data', ascending=False)
            
            st.dataframe(df_consultas, hide_index=True, width='stretch')
        else:
            st.info("Nenhuma consulta registrada para este paciente.")

def tela_registrar_vacina():
    """Interface para registrar vacinas tomadas."""
    
    # 1. REMOVE a verificação do topo (será movida para o placeholder)
    # if 'vacina_success_message' in st.session_state:
    #     st.success(st.session_state['vacina_success_message'])
    #     del st.session_state['vacina_success_message']

    st.header("✅ Registrar Vacina Tomada")
    
    pacientes_list = st.session_state['pacientes']
    if not pacientes_list:
        st.warning("Nenhum paciente cadastrado.")
        
        # Cria um placeholder vazio no final, mesmo que não haja pacientes, para manter a estrutura
        placeholder_msg = st.empty() 
        return
    
    # ... código de seleção de paciente (selectbox) ...
    pacientes_options = {p_cpf: f"{p['nome']} ({formatar_cpf(p_cpf)})" for p_cpf, p in pacientes_list.items()}
    pacientes_display_names = ["Selecione um paciente..."] + list(pacientes_options.values())
    selected_name = st.selectbox("Selecione o Paciente", pacientes_display_names, key='select_pac_reg_vac')

    if selected_name != "Selecione um paciente...":
        selected_cpf = [cpf for cpf, name in pacientes_options.items() if name == selected_name][0]
        paciente = st.session_state['pacientes'][selected_cpf]
        
        faixa = paciente['faixa_etaria']
        vacinas_relevantes = VACINAS_POR_GRUPO.get(faixa, [])
        vacinas_tomadas_set = set(paciente['vacinas_tomadas'])
        
        pendentes_list = [v for v in vacinas_relevantes if v not in vacinas_tomadas_set]

        if not pendentes_list:
            st.success(f"Todas as vacinas relevantes para '{faixa}' já estão registradas como tomadas para {paciente['nome']}.")
            # Cria um placeholder vazio para manter a estrutura, mesmo que não seja usado.
            placeholder_msg = st.empty() 
            return

        st.subheader(f"Vacinas Pendentes para **{paciente['nome']}** ({faixa})")
        st.markdown("Marque as vacinas que foram **administradas**:")

        vacinas_para_registrar = []
        for vacina in pendentes_list:
            if st.checkbox(vacina, key=f"vac_check_{vacina}"): 
                vacinas_para_registrar.append(vacina)

        # Botão de confirmação
        print()
        if st.button("Confirmar Registro de Vacinas"):
            if vacinas_para_registrar:
                for v in vacinas_para_registrar:
                    st.session_state['pacientes'][selected_cpf]['vacinas_tomadas'].append(v)
                
                # Salva a mensagem no estado de sessão
                print()
                st.session_state['vacina_success_message'] = (
                    f"✅ **{len(vacinas_para_registrar)}** vacina(s) registrada(s) com sucesso "
                    f"para **{paciente['nome']}**!"
                )
                
                # Força a recarga
                st.rerun()
            else:
                st.warning("Selecione pelo menos uma vacina para registrar.")

    
    # 2. CRIA O PLACEHOLDER NA PARTE INFERIOR
    # O Streamlit renderiza os widgets na ordem. Este está no final da função.
    placeholder_msg = st.empty() 

    # 3. NA RECARGA, COLOCA A MENSAGEM NO PLACEHOLDER
    if 'vacina_success_message' in st.session_state:
        # Usa o placeholder criado na parte inferior da tela para exibir a mensagem
        placeholder_msg.success(st.session_state['vacina_success_message'])
        del st.session_state['vacina_success_message']

def tela_dashboard():
    """
    Dashboard de Indicadores de Saúde.
    Apresenta apenas dados anonimizados e agregados em conformidade com a LGPD.
    """
    st.header("📊 Dashboard de Indicadores de Saúde")
    st.caption("Dados agregados para análise de tendências. **Nenhuma informação pessoal sensível é exibida (LGPD).**")
    st.markdown("---")

    pacientes_data = st.session_state['pacientes']
    consultas_data = st.session_state['consultas']

    # 1. Preparação dos Dados Anonimizados
    
    # Cria um DataFrame de pacientes para fácil agregação
    if pacientes_data:
        pacientes_df = pd.DataFrame(pacientes_data).T.reset_index(names=['cpf'])
        # Apenas as colunas necessárias para agregação (anonimização)
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
    
    # ----------------------------------------------------
    # Indicador de Cobertura Vacinal (Simulado)
    # Apenas para pacientes com faixa etária definida
    # ----------------------------------------------------
    
    if total_pacientes > 0:
        # Conta quantos pacientes têm alguma vacina registrada
        pacientes_vacinados = sum(1 for p in pacientes_data.values() if p.get('vacinas_tomadas'))
        cobertura_perc = (pacientes_vacinados / total_pacientes) * 100 if total_pacientes else 0
        col3.metric("Pacientes com Vacinas Registradas", f"{pacientes_vacinados} de {total_pacientes}", delta=f"{cobertura_perc:.1f}%")
        
        # Média de Idade
        media_idade = pacientes_anon_df['idade'].mean() if not pacientes_anon_df.empty else 0
        col4.metric("Média de Idade dos Pacientes", f"{media_idade:.1f} anos")
    
    st.markdown("---")
    
    # 3. Gráficos de Distribuição (Tendências)

    # 3.2 Cidade de Origem
    st.subheader("Origem dos Pacientes por Cidade de Residência")

    # 3.1. Distribuição por Faixa Etária
    st.subheader("Distribuição de Pacientes por Faixa Etária")
    if not pacientes_anon_df.empty:
        contagem_faixa = pacientes_anon_df['faixa_etaria'].value_counts().reset_index()
        contagem_faixa.columns = ['Faixa Etária', 'Total']
        
        st.bar_chart(contagem_faixa, x='Faixa Etária', y='Total')
    else:
        st.info("Cadastre pacientes para visualizar esta distribuição.")

    st.markdown("---")

    # 3.2. Consultas por Especialidade (Se houver consultas)
    st.subheader("Consultas Agendadas por Especialidade")

    if not pacientes_anon_df.empty:
        contagem_cidade = pacientes_anon_df['cidade'].value_counts().reset_index()
        contagem_cidade.columns = ['Cidade', 'Total']
        
        # Exibir as Top 10 cidades em um gráfico de barras
        st.bar_chart(contagem_cidade.head(10), x='Cidade', y='Total')
    else:
        st.info("Cadastre pacientes com a cidade de residência para visualizar a distribuição.")

    
    if total_consultas > 0:
        # Achata a lista de consultas em um DataFrame único
        todas_consultas = []
        for cpf, consultas in consultas_data.items():
            for c in consultas:
                todas_consultas.append({'especialidade': c['especialidade']})
        
        consultas_df = pd.DataFrame(todas_consultas)
        
        contagem_especialidade = consultas_df['especialidade'].value_counts().reset_index()
        contagem_especialidade.columns = ['Especialidade', 'Contagem']
        
        st.dataframe(contagem_especialidade, width='stretch', hide_index=True)
        # st.bar_chart(contagem_especialidade, x='Especialidade', y='Contagem') # Gráfico opcional
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

    with st.expander("Por que preciso informar a Cidade de Residência?"):
        st.markdown(
            """
            A Cidade de Residência é utilizada exclusivamente para fins de **gestão e planejamento (Dashboard)**. 
            Ao agregar os dados por cidade, a Unidade de Saúde pode identificar áreas com maior demanda 
            e otimizar a distribuição de recursos, mantendo a conformidade com a LGPD.
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
    st.subheader("2. Vacinação e LGPD")

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

    with st.expander("Por que o nome da vacina aparece com detalhes da dose (ex: 'Penta - 2 meses')?"):
        st.markdown(
            """
            O sistema lista a dose específica (ex: 1ª, 2ª, reforço) para que o registro de vacinação seja o mais detalhado possível, auxiliando na conferência do calendário. Se a vacina for marcada como tomada, aquela dose específica será marcada como concluída.
            """
        )

    with st.expander("Por que não vejo nomes ou CPFs no Dashboard?"):
        st.markdown(
            """
            Em cumprimento à **Lei Geral de Proteção de Dados (LGPD)**, o Dashboard exibe apenas dados **agregados e anonimizados** (como contagem de pacientes por cidade ou especialidade). Isso protege a privacidade de todos os pacientes.
            """
        )

# --- Menu Principal (Sidebar) ---

st.sidebar.title("🏥 PET Saúde - GT09")
st.sidebar.markdown("Gerencie pacientes, consultas e vacinas.")

menu_options = {
    "Cadastro de Paciente": tela_cadastro_paciente,
    "Minha Saúde": tela_visualizar_historico,
    "Registrar Vacina": tela_registrar_vacina,
    "Agendar Consulta": tela_cadastro_consulta,
    "Dashboard" : tela_dashboard,
    "Dúvidas Frequentes (FAQ)" : tela_faq,

}

selection = st.sidebar.radio("Navegação", list(menu_options.keys()))

# Executa a função da tela selecionada
menu_options[selection]()