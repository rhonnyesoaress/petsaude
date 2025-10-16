🏥 Sistema de Gestão de Unidade de Saúde (PET Saúde - UFPB)

Dashboard e Sistema de Cadastro para Unidades de Saúde, focado no gerenciamento de pacientes, agendamento de consultas e rastreamento de vacinação.

Desenvolvido como parte das atividades do PET Saúde/Interprofissionalidade - Grupo de Trabalho 09 (GT09) da Universidade Federal da Paraíba (UFPB).

🌟 Recursos Principais

O sistema foi desenhado para ser intuitivo e funcional, com foco na integridade e privacidade dos dados:

    Cadastro Completo de Pacientes: Registro com cálculo automático de idade e classificação de faixa etária (Recém-Nascido, Criança, Adolescente/Jovem, Adulto, Idoso).

    Gestão de Consultas: Agendamento futuro de consultas e registro de observações por especialidade.

    Cartão de Vacinação Dinâmico: Visualização do status vacinal por faixa etária, com marcação de doses [TOMADA] ou [PENDENTE].

    Dashboard Gerencial (LGPD Compliant): Indicadores agregados e anonimizados, como distribuição por faixa etária e origem dos pacientes (cidade), sem exposição de dados pessoais sensíveis.

    Interface Gráfica (Streamlit): Interface web moderna com tema claro (branco/azul) e navegação intuitiva.

🛡️ Conformidade e Privacidade (LGPD)

Em todas as análises gerenciais, o sistema segue o princípio da anonimização de dados:

    Dashboard: Nomes, CPFs e Datas de Nascimento nunca são exibidos. O foco é em contagens e tendências.

    Dados Sensíveis: O sistema trata as informações de saúde (vacinas, consultas) com a devida cautela, acessíveis apenas nas telas de gerenciamento do paciente.

⚙️ Tecnologias Utilizadas

Tecnologia	Função
Python	Linguagem principal de backend e lógica de negócios.
Streamlit	Framework para construção da interface gráfica web.
Pandas	Biblioteca essencial para manipulação, agregação e visualização de dados (Dashboard).
datetime	Manipulação de datas e cálculo de idade/faixa etária.

🚀 Como Rodar o Sistema Localmente

Siga os passos abaixo para instalar e executar o projeto em seu ambiente:

Pré-requisitos

Você deve ter o Python (versão 3.8+) instalado.

    Clone o Repositório:
    Bash

git clone [LINK DO SEU REPOSITÓRIO NO GITHUB]
cd nome_do_seu_diretorio

Crie e Ative o Ambiente Virtual (Recomendado):
Bash

python -m venv venv
source venv/bin/activate  # No Windows use: .\venv\Scripts\activate

Instale as Dependências:
Bash

pip install -r requirements.txt

(Certifique-se que seu requirements.txt contenha streamlit e pandas.)

Execute o Aplicativo:
Bash

    streamlit run app_pet.py

O sistema será aberto automaticamente no seu navegador, geralmente em http://localhost:8501.

🤝 Contribuição e Contato

Este projeto é um esforço do PET Saúde - GT09 da UFPB.

Para sugestões, relatórios de bugs ou dúvidas, entre em contato com o coordenador do projeto ou use o sistema de Issues do GitHub.

Desenvolvido por: Rhonnye Wendell | UFPB | PET Saúde
