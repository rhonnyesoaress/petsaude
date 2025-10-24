import streamlit as st
from datetime import date

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
