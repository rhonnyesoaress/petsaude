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
        
    # CRIAÇÃO DO MAPA NOME -> CPF (Para esconder o CPF no selectbox)
    pacientes_options_map = {p['nome']: p_cpf for p_cpf, p in pacientes_list.items()}
    pacientes_display_names = ["Selecione um paciente..."] + list(pacientes_options_map.keys())

    # LÓGICA DE PRÉ-SELEÇÃO
    cpf_para_preselecao = st.session_state.get('last_registered_cpf')
    initial_index = 0
    if cpf_para_preselecao and cpf_para_preselecao in pacientes_list:
        nome_do_paciente = pacientes_list[cpf_para_preselecao]['nome']
        initial_index = pacientes_display_names.index(nome_do_paciente)
        # Não precisa deletar last_registered_cpf aqui, o tela_cadastro_paciente já cuida disso.

    selected_name = st.selectbox("Selecione o Paciente", pacientes_display_names, index=initial_index)
    
    if selected_name != "Selecione um paciente...":
        # RECUPERA O CPF ATRAVÉS DO NOME SELECIONADO
        selected_cpf = pacientes_options_map[selected_name]
        
        with st.form("form_consulta"):
            # min_value=date.today() impede agendamentos no passado
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
        
    # CRIAÇÃO DO MAPA NOME -> CPF (Para esconder o CPF no selectbox)
    pacientes_options_map = {p['nome']: p_cpf for p_cpf, p in pacientes_list.items()}
    pacientes_display_names = ["Selecione um paciente..."] + list(pacientes_options_map.keys())
    
    # LÓGICA DE PRÉ-SELEÇÃO
    cpf_para_preselecao = st.session_state.get('last_registered_cpf')
    initial_index = 0
    if cpf_para_preselecao and cpf_para_preselecao in pacientes_list:
        nome_do_paciente = pacientes_list[cpf_para_preselecao]['nome']
        initial_index = pacientes_display_names.index(nome_do_paciente)
        
    selected_name = st.selectbox("Selecione o Paciente", pacientes_display_names, index=initial_index)

    if selected_name != "Selecione um paciente...":
        # RECUPERA O CPF ATRAVÉS DO NOME SELECIONADO
        selected_cpf = pacientes_options_map[selected_name]
        paciente = st.session_state['pacientes'][selected_cpf]

        st.subheader(f"Dados de **{paciente['nome']}**")
        st.info(f"Idade: **{paciente['idade']}** anos | Faixa Etária: **{paciente['faixa_etaria']}**")
        
        st.markdown("---")
        
        # Criação das abas
        tab_atendimentos, tab_vacinacao = st.tabs(["Atendimentos (Consultas)", "Cartão de Vacina"])
        
        # Conteúdo da Aba 1: Atendimentos/Consultas
        with tab_atendimentos:
            st.subheader("📜 Histórico de Consultas")
            historico = st.session_state['consultas'].get(selected_cpf, [])

            if historico:
                df_consultas = pd.DataFrame(historico)
                df_consultas['data'] = pd.to_datetime(df_consultas['data']) 
                df_consultas['data'] = df_consultas['data'].dt.strftime('%d/%m/%Y')
                df_consultas = df_consultas.rename(columns={'data': 'Data', 'especialidade': 'Especialidade', 'observacoes': 'Observações'})
                df_consultas = df_consultas.sort_values(by='Data', ascending=False)
                
                st.dataframe(df_consultas, hide_index=True, use_container_width=True)
            else:
                st.info("Nenhuma consulta/atendimento registrado para este paciente.")

        # Conteúdo da Aba 2: Cartão de Vacina
        with tab_vacinacao:
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
                st.dataframe(df_vacinas, hide_index=True, use_container_width=True)
            else:
                st.write(f"Nenhuma vacina específica listada para a faixa '{faixa}'.")


def tela_registrar_vacina():
    """Interface para registrar vacinas tomadas."""
    
    # 1. VERIFICAÇÃO E EXIBIÇÃO DA MENSAGEM (Com placeholder no final)
    st.header("✅ Registrar Vacina Tomada")
    
    pacientes_list = st.session_state['pacientes']
    if not pacientes_list:
        st.warning("Nenhum paciente cadastrado.")
        placeholder_msg = st.empty() 
        return
    
    # CRIAÇÃO DO MAPA NOME -> CPF (Para esconder o CPF no selectbox)
    pacientes_options_map = {p['nome']: p_cpf for p_cpf, p in pacientes_list.items()}
    pacientes_display_names = ["Selecione um paciente..."] + list(pacientes_options_map.keys())

    # LÓGICA DE PRÉ-SELEÇÃO
    cpf_para_preselecao = st.session_state.get('last_registered_cpf')
    initial_index = 0
    if cpf_para_preselecao and cpf_para_preselecao in pacientes_list:
        nome_do_paciente = pacientes_list[cpf_para_preselecao]['nome']
        initial_index = pacientes_display_names.index(nome_do_paciente)
        
    # Seleção de Paciente
    selected_name = st.selectbox(
        "Selecione o Paciente", 
        pacientes_display_names, 
        index=initial_index, 
        key='select_pac_reg_vac'
    )

    if selected_name == "Selecione um paciente...":
        # Interrompe a execução se o valor padrão for selecionado
        placeholder_msg = st.empty()
        return

    # RECUPERA O CPF ATRAVÉS DO NOME SELECIONADO
    selected_cpf = pacientes_options_map[selected_name]
    paciente = st.session_state['pacientes'][selected_cpf]
    
    # ... (restante da função para listar vacinas pendentes e checklist) ...
    
    faixa = paciente['faixa_etaria']
    vacinas_relevantes = VACINAS_POR_GRUPO.get(faixa, [])
    vacinas_tomadas_set = set(paciente['vacinas_tomadas'])
    
    pendentes_list = [v for v in vacinas_relevantes if v not in vacinas_tomadas_set]

    if not pendentes_list:
        st.success(f"Todas as vacinas relevantes para '{faixa}' já estão registradas como tomadas para {paciente['nome']}.")
        placeholder_msg = st.empty() 
        return

    st.subheader(f"Vacinas Pendentes para **{paciente['nome']}** ({faixa})")
    st.markdown("Marque as vacinas que foram **administradas**:")

    vacinas_para_registrar = []
    for vacina in pendentes_list:
        if st.checkbox(vacina, key=f"vac_check_{vacina}"): 
            vacinas_para_registrar.append(vacina)

    # Botão de confirmação
    if st.button("Confirmar Registro de Vacinas"):
        if vacinas_para_registrar:
            for v in vacinas_para_registrar:
                st.session_state['pacientes'][selected_cpf]['vacinas_tomadas'].append(v)
            
            st.session_state['vacina_success_message'] = (
                f"✅ **{len(vacinas_para_registrar)}** vacina(s) registrada(s) com sucesso "
                f"para **{paciente['nome']}**!"
            )
            st.rerun()
        else:
            st.warning("Selecione pelo menos uma vacina para registrar.")

    # 2. CRIA O PLACEHOLDER NA PARTE INFERIOR
    placeholder_msg = st.empty() 

    # 3. NA RECARGA, COLOCA A MENSAGEM NO PLACEHOLDER
    if 'vacina_success_message' in st.session_state:
        placeholder_msg.success(st.session_state['vacina_success_message'])
        del st.session_state['vacina_success_message']


def tela_dashboard():
    """
    Dashboard de Resumo Individual do Paciente.
    Apresenta métricas e status de saúde do paciente selecionado.
    """
    st.header("📋 Resumo do Paciente")
    st.caption("Visualização rápida de métricas e status de consultas/vacinas.")
    st.markdown("---")

    pacientes_list = st.session_state['pacientes']
    if not pacientes_list:
        st.warning("Nenhum paciente cadastrado.")
        return
        
    # CRIAÇÃO DO MAPA NOME -> CPF (Para esconder o CPF no selectbox)
    pacientes_options_map = {p['nome']: p_cpf for p_cpf, p in pacientes_list.items()}
    pacientes_display_names = ["Selecione um paciente..."] + list(pacientes_options_map.keys())
    
    # LÓGICA DE PRÉ-SELEÇÃO
    cpf_para_preselecao = st.session_state.get('last_registered_cpf')
    initial_index = 0
    if cpf_para_preselecao and cpf_para_preselecao in pacientes_list:
        nome_do_paciente = pacientes_list[cpf_para_preselecao]['nome']
        initial_index = pacientes_display_names.index(nome_do_paciente)
        
    selected_name = st.selectbox("Selecione o Paciente para Visualizar o Resumo", pacientes_display_names, index=initial_index)

    if selected_name != "Selecione um paciente...":
        selected_cpf = pacientes_options_map[selected_name]
        paciente = st.session_state['pacientes'][selected_cpf]
        historico = st.session_state['consultas'].get(selected_cpf, [])
        faixa = paciente['faixa_etaria']
        vacinas_relevantes = VACINAS_POR_GRUPO.get(faixa, [])
        vacinas_tomadas_set = set(paciente['vacinas_tomadas'])

        st.subheader(f"Resumo de **{paciente['nome']}**")
        st.info(f"Idade: **{paciente['idade']}** anos | Faixa Etária: **{paciente['faixa_etaria']}** | Cidade: **{paciente['cidade']}**")
        st.markdown("---")

        # 1. Indicadores Chave (Metrics)
        total_consultas = len(historico)
        vacinas_pendentes = len(vacinas_relevantes) - len([v for v in vacinas_relevantes if v in vacinas_tomadas_set])
        vacinas_aplicadas = len([v for v in vacinas_relevantes if v in vacinas_tomadas_set])
        
        col1, col2, col3 = st.columns(3)

        col1.metric("Consultas Registradas", total_consultas)
        col2.metric("Vacinas Aplicadas (Relevantes)", vacinas_aplicadas)
        col3.metric("Vacinas Pendentes (Relevantes)", vacinas_pendentes)
        
        st.markdown("---")

        # 2. Gráficos de Distribuição
        
        # 2.1. Gráfico de Distribuição de Vacinas (Aplicadas vs. Pendentes)
        st.subheader("Cobertura Vacinal do Paciente")
        
        dados_cobertura = pd.DataFrame({
            'Status': ['Aplicadas', 'Pendentes'],
            'Contagem': [vacinas_aplicadas, vacinas_pendentes]
        })
        
        # Gráfico de setores (Pie Chart)
        if vacinas_aplicadas > 0 or vacinas_pendentes > 0:
            st.bar_chart(
                dados_cobertura,
                x='Status',
                y='Contagem',
                color='Status'
            )
        else:
            st.info("Nenhuma vacina relevante para esta faixa etária.")

        st.markdown("---")
        
        # 2.2. Resumo de Consultas Recentes
        st.subheader("Consultas por Especialidade")
        
        if historico:
            # Cria DataFrame apenas com a coluna de especialidade
            df_especialidades = pd.DataFrame(historico)['especialidade'].value_counts().reset_index()
            df_especialidades.columns = ['Especialidade', 'Contagem']
            
            # Gráfico de barras
            st.bar_chart(
                df_especialidades,
                x='Especialidade',
                y='Contagem'
            )
            
            st.caption("Últimas 5 Consultas Detalhadas:")
            # Tabela de últimas consultas (como antes)
            df_consultas = pd.DataFrame(historico)
            df_consultas['data'] = pd.to_datetime(df_consultas['data']) 
            df_consultas['data'] = df_consultas['data'].dt.strftime('%d/%m/%Y')
            df_consultas = df_consultas.rename(columns={'data': 'Data', 'especialidade': 'Especialidade', 'observacoes': 'Observações'})
            df_consultas = df_consultas.sort_values(by='Data', ascending=False)
            
            st.dataframe(df_consultas.head(5), hide_index=True, use_container_width=True)
        else:
            st.info("Nenhuma consulta registrada para exibir a distribuição por especialidade.")

        st.markdown("---")

        # 3. Resumo do Status Vacinal (Expander)
        st.subheader("Status Detalhado da Vacinação")
        
        if vacinas_relevantes:
            pendentes_list = [v for v in vacinas_relevantes if v not in vacinas_tomadas_set]
            
            if pendentes_list:
                st.warning(f"Atenção: Existem {vacinas_pendentes} vacinas pendentes para a faixa etária {faixa}.")
                
                with st.expander("Ver Vacinas Pendentes"):
                    for v in pendentes_list:
                        st.markdown(f"- ❌ {v}")
            else:
                st.success(f"Excelente! Todas as {len(vacinas_relevantes)} vacinas relevantes para {faixa} estão registradas como aplicadas.")




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