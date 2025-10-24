PET-Saúde - Dashboard Pessoal de Saúde
Status: 🚧 Em Desenvolvimento 🚧

Um dashboard de saúde pessoal construído com Streamlit, projetado para que usuários individuais possam gerenciar e acompanhar seu histórico de consultas e seu status de vacinação. O sistema utiliza a lógica do calendário do Ministério da Saúde para sugerir vacinas com base na faixa etária do usuário.

🌟 Principais Funcionalidades
Sistema de Autenticação: Cadastro e login de usuários (pacientes) baseado em CPF, com validação de dados e armazenamento em sessão.

Dashboard Pessoal: Visualização rápida com métricas-chave (total de consultas, vacinas aplicadas vs. pendentes) e gráficos de distribuição.

Gestão de Consultas: Registro de futuras consultas médicas, separadas por especialidade.

Histórico Detalhado: Visualização em abas de todo o histórico de consultas passadas e do cartão de vacina completo.

Cartão de Vacina Inteligente: O sistema filtra e exibe automaticamente as vacinas relevantes (pendentes ou aplicadas) com base na faixa etária do usuário, calculada a partir da data de nascimento.

Página de FAQ: Seção de ajuda explicando a lógica do sistema (cálculo de idade, grupos de vacinas, etc.).

🛠️ Tech Stack (Tecnologias Utilizadas)
Framework Principal: Streamlit

Análise e Manipulação de Dados: Pandas

Linguagem: Python 3

📂 Estrutura do Projeto
O projeto utiliza a arquitetura nativa de Multi-Page App (MPA) do Streamlit, onde login.py atua como o script principal de autenticação e roteamento.

dashboard_pet/
│
├── 📄 login.py             # Script principal (Login, Cadastro de Usuário, Roteador)
├── 📄 utils.py             # Funções (cálculo de idade, listas de vacinas, validador de CPF)
│
└── 📁 pages/               # Páginas acessíveis após o login
    ├── 📄 dashboard.py
    ├── 📄 visualizar_historico.py
    ├── 📄 cadastro_consulta.py
    ├── 📄 registrar_vacina.py
    └── 📄 faq.py
🚀 Como Executar o Projeto
Siga os passos abaixo para executar o projeto localmente.

1. Pré-requisitos
Python 3.9+

Git (Opcional, para clonar)

2. Instalação
Clone o repositório:

Bash

git clone https://github.com/seu-usuario/dashboard_pet.git
cd dashboard_pet
(Recomendado) Crie e ative um ambiente virtual:

Bash

# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
Crie um arquivo requirements.txt na raiz do projeto com o seguinte conteúdo:

Plaintext

streamlit
pandas
Instale as dependências:

Bash

pip install -r requirements.txt
3. Execução
Na pasta raiz do projeto (onde está o login.py), execute o Streamlit:

Bash

streamlit run login.py
O aplicativo será aberto automaticamente no seu navegador padrão.