import time
import random
import getpass
import os
from pathlib import Path
from datetime import datetime, timedelta

# Dicionários de usuários
usuarios = {
    "Aluno": {"senha": "123", "tipo": 1},
    "Professor": {"senha": "123", "tipo": 2},
    "Cordenação": {"senha": "123", "tipo": 3}
}

# Alunos (observe que já converti "15:30" e "16:40" para datetime; o código lida também com strings)
Alunos = {
    "matheos":  {"senha": "123", "turma": "1°", "pc": 19,
                 "entrada": datetime.strptime("15:30", "%H:%M"),
                 "saida": datetime.strptime("16:40", "%H:%M")},
    "pedro":    {"senha": "123", "turma": "2°", "pc": None, "entrada": None, "saida": None},
    "henrique": {"senha": "123", "turma": "3°", "pc": None, "entrada": None, "saida": None}
}

Professor = {
    "erick":  {"senha": "123", "turma": "1°"},
    "angela": {"senha": "123", "turma": "2°"},
    "luiz":   {"senha": "123", "turma": "3°"},
    "marcos": {"senha": "123", "turma": "4°"}
}

Coordenacao = {
    "monica":  {"senha": "123", "turma": "1°"},
    "alesandra": {"senha": "123", "turma": "2°"},
    "marta":   {"senha": "123", "turma": "3°"}
}

# Pequenos stubs para evitar NameError (se quiser, substitua pela lógica real)
horarios_disponiveis = {
    "Segunda": [("08:00", "09:00"), ("09:00", "10:00")],
    "Terça": [("08:00", "09:00")]
}
horarios_reservados = {}

def cancelar_agendamento_professor(nome):
    removidos = []
    for key, prof in list(horarios_reservados.items()):
        if prof == nome:
            removidos.append(key)
            del horarios_reservados[key]
    if removidos:
        print(f"Agendamentos removidos: {removidos}")
    else:
        print("Nenhum agendamento encontrado para você.")

def mostrar_agendamentos_professor(nome):
    encontrados = [(k, v) for k, v in horarios_reservados.items() if v == nome]
    if encontrados:
        print("Seus agendamentos:")
        for k, _ in encontrados:
            print(k)
    else:
        print("Você não possui agendamentos.")

# Variáveis globais
numero_pc = random.randint(1, 25)
tentativa = 3
acesso_permitido = False

# Funções de login
def login_aluno(nome, senha):
    if nome in Alunos and senha == Alunos[nome]["senha"]:
        pc = random.randint(1, 25)  # Atribuir um PC aleatório ao aluno
        Alunos[nome]["pc"] = pc
        Alunos[nome]["entrada"] = datetime.now()  # Registrar hora de entrada
        print(f"🎯 O número do seu PC é {pc}")
        return True
    return False

def login_professor(nome, senha):
    if nome in Professor and senha == Professor[nome]["senha"]:
        return True
    return False

def login_coord(nome, senha):
    if nome in Coordenacao and senha == Coordenacao[nome]["senha"]:
        return True
    return False

# --- Conversões auxiliares e cálculo de tempo ---
def _normalize_datetime(dt):
    """
    Normaliza entradas (str ou datetime) para datetime completo (com data).
    - aceita strings 'HH:MM' ou 'HH:MM:SS' ou formatos com data.
    - se for datetime com year == 1900, assume data de hoje.
    - retorna None caso dt seja None.
    """
    if dt is None:
        return None
    if isinstance(dt, str):
        # tenta vários formatos
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%H:%M:%S", "%H:%M"):
            try:
                parsed = datetime.strptime(dt, fmt)
                if parsed.year == 1900:
                    # hora apenas -> juntar com data de hoje
                    return datetime.combine(datetime.today().date(), parsed.time())
                return parsed
            except ValueError:
                continue
        raise ValueError(f"Formato de data/hora não reconhecido: {dt}")
    if isinstance(dt, datetime):
        if dt.year == 1900:
            return datetime.combine(datetime.today().date(), dt.time())
        return dt
    raise TypeError("Tipo de data/hora inválido")

def tempo_permanencia(entrada, saida):
    """
    Recebe entrada e saída (podem ser str, datetime ou None).
    Retorna string HH:MM:SS ou None se não houver dados suficientes.
    """
    ent = _normalize_datetime(entrada)
    sai = _normalize_datetime(saida)
    if ent is None or sai is None:
        return None
    delta = sai - ent
    # Caso delta negativo (ex.: saída no dia seguinte), ajusta pegando valor absoluto
    if delta.total_seconds() < 0:
        delta = -delta
    return str(delta).split('.')[0]  # HH:MM:SS

# --- Função para salvar relatório ---
def save_relatorio(nome_aluno, info, base_folder="relatorios/alunos"):
    """
    Salva um relatório txt em relatorios/alunos/<nome_aluno>/timestamp_relatorio_<nome>.txt
    """
    folder = Path(base_folder) / nome_aluno
    folder.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ts}_relatorio_{nome_aluno}.txt"
    filepath = folder / filename

    entrada = info.get("entrada")
    saida = info.get("saida")
    tempo = tempo_permanencia(entrada, saida)

    entrada_str = entrada.strftime('%Y-%m-%d %H:%M:%S') if isinstance(entrada, datetime) else (str(entrada) if entrada else "N/A")
    saida_str = saida.strftime('%Y-%m-%d %H:%M:%S') if isinstance(saida, datetime) else (str(saida) if saida else "N/A")
    tempo_str = tempo if tempo else "N/A"

    content = (
        f"Relatório gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Aluno: {nome_aluno.capitalize()}\n"
        f"Turma: {info.get('turma', 'N/A')}\n"
        f"PC: {info.get('pc', 'N/A')}\n"
        f"Entrada: {entrada_str}\n"
        f"Saída: {saida_str}\n"
        f"Tempo de Permanência: {tempo_str}\n"
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Relatório salvo em: {filepath}")

# Loop de login
while tentativa > 0:
    print("\n--- Login ---")
    print("1 - Aluno")
    print("2 - Professor")
    print("3 - Coordenação")

    try:
        perfil = int(input("Qual o seu tipo de usuário: "))
    except ValueError:
        print("Entrada inválida! Digite um número de 1 a 3.")
        continue

    nome_digitado = input("Digite seu nome: ").strip().lower()
    senha_digitada = getpass.getpass("Digite a senha: ").strip()

    if perfil == 1 and login_aluno(nome_digitado, senha_digitada):
        print("✅ Login do Aluno bem-sucedido!")
        acesso_permitido = True
        usuario_tipo = 1
        usuario_nome = nome_digitado
        break
    elif perfil == 2 and login_professor(nome_digitado, senha_digitada):
        print("✅ Login de Professor bem-sucedido!")
        acesso_permitido = True
        usuario_tipo = 2
        usuario_nome = nome_digitado
        break
    elif perfil == 3 and login_coord(nome_digitado, senha_digitada):
        acesso_permitido = True
        usuario_tipo = 3
        usuario_nome = nome_digitado
        break
    else:
        tentativa -= 1
        print("❌ Senha incorreta ou perfil inválido!")
        print(f"Restam {tentativa} tentativa(s).\n")

if not acesso_permitido:
    print("🚫 Número de tentativas esgotado. Acesso bloqueado!")
    exit()

# Exemplo de como o tempo de saída pode ser registrado (aqui só para demo)
if usuario_tipo == 1:
    Alunos[usuario_nome]["saida"] = datetime.now()  # Simula a hora de saída do aluno

# MENU ALUNO (simples)
if usuario_tipo == 1:
    print("Fim do programa para alunos. Faça o login novamente para outras operações.")

# MENU PROFESSOR
elif usuario_tipo == 2:
    while True:
        print("\n--- Menu Professor ---")
        print("1 - Agendar sala de informática")
        print("2 - Cancelar agendamento")
        print("3 - Ver meus agendamentos")
        print("4 - Sair")

        escolha = input("Escolha uma opção: ").strip()
        if escolha == "1":
            if all(len(horarios) == 0 for horarios in horarios_disponiveis.values()):
                print("❌ Todos os horários já foram reservados.")
            else:
                print("\n📅 Dias da semana disponíveis para agendamento:")
                for i, dia in enumerate(horarios_disponiveis.keys(), start=1):
                    print(f"{i} - {dia}")
                # aqui manter a lógica original/implementar a reserva real
                print("Funcionalidade de agendamento não implementada nesta demo.")
        elif escolha == "2":
            cancelar_agendamento_professor(usuario_nome)
        elif escolha == "3":
            mostrar_agendamentos_professor(usuario_nome)
        elif escolha == "4":
            print("Saindo... Até logo!")
            break
        else:
            print("Opção inválida, tente novamente.")

# MENU COORDENAÇÃO
elif usuario_tipo == 3:
    print("✅ Login de Coordenação bem-sucedido!")
    while True:
        print("\n--- Menu Coordenação ---")
        print("1 - Ver todos os agendamentos")
        print("2 - Alterar senha")
        print("3 - Alterar senha de Alunos ou Professores")
        print("4 - Ver relatório de uso dos PCs de todos os alunos (salva arquivos)")
        print("5 - Ver relatório de uso de um aluno específico (salva arquivo)")
        print("6 - Sair")

        escolha = input("Escolha uma opção: ").strip()
        if escolha == "1":
            # Ver agendamentos (como já foi implementado)
            print("Visualização de agendamentos não implementada nesta demo.")
        elif escolha == "2":
            nova_senha = getpass.getpass("Digite a nova senha da coordenação: ").strip()
            if nova_senha:
                usuarios["Cordenação"]["senha"] = nova_senha
                print("🔐 Senha alterada com sucesso!")
            else:
                print("Senha inválida. Operação cancelada.")
        elif escolha == "3":
            print("🔑 Alterar senha de Alunos ou Professores")
            tipo_usuario = input("Digite o tipo de usuário (Aluno ou Professor): ").strip().lower()
            if tipo_usuario == "aluno":
                nome_aluno = input("Digite o nome do aluno: ").strip().lower()
                if nome_aluno in Alunos:
                    nova_senha_aluno = getpass.getpass(f"Digite a nova senha para o aluno {nome_aluno}: ").strip()
                    if nova_senha_aluno:
                        Alunos[nome_aluno]["senha"] = nova_senha_aluno
                        print(f"🔐 Senha do aluno {nome_aluno} alterada com sucesso!")
                    else:
                        print("Senha inválida. Operação cancelada.")
                else:
                    print("Aluno não encontrado.")
            elif tipo_usuario == "professor":
                nome_professor = input("Digite o nome do professor: ").strip().lower()
                if nome_professor in Professor:
                    nova_senha_professor = getpass.getpass(f"Digite a nova senha para o professor {nome_professor}: ").strip()
                    if nova_senha_professor:
                        Professor[nome_professor]["senha"] = nova_senha_professor
                        print(f"🔐 Senha do professor {nome_professor} alterada com sucesso!")
                    else:
                        print("Senha inválida. Operação cancelada.")
                else:
                    print("Professor não encontrado.")
            else:
                print("Tipo de usuário inválido. Escolha 'Aluno' ou 'Professor'.")
        elif escolha == "4":
            # Relatório de todos os PCs e salvar arquivos
            print("📋 Relatório de uso dos PCs de todos os alunos:")
            any_saved = False
            for aluno, info in Alunos.items():
                if info["entrada"] is not None and info["saida"] is not None:
                    tempo = tempo_permanencia(info["entrada"], info["saida"])
                    entrada_str = _normalize_datetime(info["entrada"]).strftime('%H:%M:%S')
                    saida_str = _normalize_datetime(info["saida"]).strftime('%H:%M:%S')
                    print(f"Aluno: {aluno.capitalize()}, PC: {info['pc']}, Tempo de Permanência: {tempo}, Entrada: {entrada_str}, Saída: {saida_str}")
                    # salva relatório
                    save_relatorio(aluno, info)
                    any_saved = True
            if not any_saved:
                print("Nenhum aluno com relatório completo (entrada e saída).")
        elif escolha == "5":
            # Relatório de um aluno específico e salvar
            nome_aluno = input("Digite o nome do aluno para o relatório: ").strip().lower()
            if nome_aluno in Alunos:
                info = Alunos[nome_aluno]
                if info["entrada"] is not None and info["saida"] is not None:
                    tempo = tempo_permanencia(info["entrada"], info["saida"])
                    print(f"\nRelatório do aluno {nome_aluno.capitalize()}:")
                    print(f"PC: {info['pc']}")
                    print(f"Entrada: {_normalize_datetime(info['entrada']).strftime('%H:%M:%S')}")
                    print(f"Saída: {_normalize_datetime(info['saida']).strftime('%H:%M:%S')}")
                    print(f"Tempo de Permanência: {tempo}")
                    save_relatorio(nome_aluno, info)
                else:
                    print("Este aluno ainda não tem um relatório de uso completo (falta hora de saída).")
            else:
                print(f"Aluno {nome_aluno} não encontrado.")
        elif escolha == "6":
            print("Saindo... Até logo!")
            break
        else:
            print("Opção inválida, tente novamente.")

