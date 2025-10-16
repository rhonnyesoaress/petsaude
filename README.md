# 🏥 Sistema de Gestão de Unidade de Saúde (PET Saúde - UFPB)

> Dashboard e Sistema de Cadastro para Unidades de Saúde, focado no gerenciamento de pacientes, agendamento de consultas e rastreamento de vacinação.

Desenvolvido como parte das atividades do **PET Saúde/Interprofissionalidade - Grupo de Trabalho 09 (GT09)** da **Universidade Federal da Paraíba (UFPB)**.

## 🌟 Recursos Principais

O sistema foi desenhado para ser intuitivo e funcional, com foco na integridade e privacidade dos dados:

* **👤 Cadastro Inteligente:** Registro com validação de CPF, cálculo automático de idade e classificação de faixa etária (Recém-Nascido, Criança, Adolescente/Jovem, Adulto, Idoso).
* **📝 Agendamento:** Permite agendamentos futuros de consultas, com seleção de especialidade padronizada e registro de observações.
* **💉 Cartão de Vacinação Dinâmico:** Visualização do status vacinal por faixa etária, com marcação de doses **[TOMADA]** através de cartões clicáveis, simulando um cartão de vacina real.
* **📊 Dashboard Gerencial (LGPD Compliant):** Indicadores agregados e anonimizados, como distribuição por faixa etária, origem dos pacientes (cidade) e demanda por especialidade, sem exposição de dados sensíveis.
* **❓ FAQ Integrado:** Página de Dúvidas Frequentes para auto-serviço e referência rápida sobre as regras do sistema e calendário vacinal.
* **✨ Interface Moderna:** Desenvolvido com Streamlit, utilizando o tema claro (branco/azul) para melhor usabilidade e experiência visual.

## 🛡️ Conformidade e Privacidade (LGPD)

Em todas as análises gerenciais, o sistema prioriza a segurança dos dados, seguindo os princípios da Lei Geral de Proteção de Dados (LGPD):

* **Anonimato no Dashboard:** Dados sensíveis (Nomes, CPFs, Datas de Nascimento) são estritamente mantidos nas telas de gerenciamento individual. O Dashboard exibe apenas **contagens, médias e distribuições**.
* **Integridade do CPF:** Utiliza validação matemática para garantir que apenas CPFs formalmente válidos sejam cadastrados.

## ⚙️ Tecnologias Utilizadas

O projeto é 100% baseado em Python e suas bibliotecas:

| Tecnologia | Versão Mínima | Função Principal |
| :--- | :--- | :--- |
| **Python** | 3.8+ | Linguagem principal de backend. |
| **Streamlit** | 1.28+ | Framework para construção da Interface Gráfica Web. |
| **Pandas** | 1.0+ | Manipulação, agregação de dados e visualização do Dashboard. |

## 🚀 Como Rodar o Sistema Localmente

Siga os passos abaixo para instalar e executar o projeto em seu ambiente:

### Pré-requisitos

Certifique-se de ter o **Python (versão 3.8 ou superior)** e o **Git** instalados.

1.  **Clone o Repositório:**
    ```bash
    git clone [LINK DO SEU REPOSITÓRIO NO GITHUB]
    cd nome_do_seu_diretorio
    ```

2.  **Crie e Ative o Ambiente Virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows (CMD/PowerShell) use: .\venv\Scripts\activate
    ```

3.  **Instale as Dependências:**
    Crie o arquivo `requirements.txt` se ele não existir e instale as bibliotecas:
    ```bash
    pip install -r requirements.txt
    ```


4.  **Execute o Aplicativo:**
    ```bash
    streamlit run app_pet.py
    ```

O sistema será aberto automaticamente no seu navegador, geralmente em `http://localhost:8501`.

## 🤝 Contribuição e Contato

Este projeto é um esforço contínuo do **PET Saúde - GT09** da UFPB.

Para sugestões, relatórios de bugs, ou dúvidas sobre o projeto, por favor, utilize o sistema de **Issues** do GitHub.

---
*Desenvolvedor Principal: Rhonnye Wendell | UFPB | PET Saúde*
