#!/usr/bin/env python3
"""Gera seeds PT-BR: NBR ISO/IEC 27002:2022 (93) e NBR ISO/IEC 27701:2026 Anexos A1/A2 (49)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from control_descriptions import DESCRIPTIONS_27002, DESCRIPTIONS_27701

OUT = Path(__file__).resolve().parent.parent / "data" / "seeds"

# NBR ISO/IEC 27002:2022 — titulos resumidos em PT-BR
ORG = [
    ("5.1", "Politicas de seguranca da informacao"),
    ("5.2", "Funcoes e responsabilidades de seguranca da informacao"),
    ("5.3", "Segregacao de funcoes"),
    ("5.4", "Responsabilidades da direcao"),
    ("5.5", "Contato com autoridades"),
    ("5.6", "Contato com grupos de interesse especifico"),
    ("5.7", "Inteligencia de ameacas"),
    ("5.8", "Seguranca da informacao no gerenciamento de projetos"),
    ("5.9", "Inventario de informacoes e outros ativos associados"),
    ("5.10", "Uso aceitavel de informacoes e outros ativos associados"),
    ("5.11", "Devolucao de ativos"),
    ("5.12", "Classificacao da informacao"),
    ("5.13", "Rotulagem da informacao"),
    ("5.14", "Transferencia de informacao"),
    ("5.15", "Controle de acesso"),
    ("5.16", "Gestao de identidades"),
    ("5.17", "Informacao de autenticacao"),
    ("5.18", "Direitos de acesso"),
    ("5.19", "Seguranca da informacao em relacionamentos com fornecedores"),
    ("5.20", "Abordagem de seguranca da informacao em acordos com fornecedores"),
    ("5.21", "Gestao da seguranca da informacao na cadeia de fornecimento de TIC"),
    ("5.22", "Monitoramento, analise critica e gestao de mudancas de servicos de fornecedores"),
    ("5.23", "Seguranca da informacao para uso de servicos em nuvem"),
    ("5.24", "Planejamento e preparacao da gestao de incidentes de seguranca da informacao"),
    ("5.25", "Avaliacao e decisao sobre eventos de seguranca da informacao"),
    ("5.26", "Resposta a incidentes de seguranca da informacao"),
    ("5.27", "Aprendizado com incidentes de seguranca da informacao"),
    ("5.28", "Coleta de evidencias"),
    ("5.29", "Seguranca da informacao durante a interrupcao"),
    ("5.30", "Prontidao de TIC para continuidade de negocios"),
    ("5.31", "Requisitos legais, estatutarios, regulatorios e contratuais"),
    ("5.32", "Direitos de propriedade intelectual"),
    ("5.33", "Protecao de registros"),
    ("5.34", "Privacidade e protecao de PII"),
    ("5.35", "Analise critica independente da seguranca da informacao"),
    ("5.36", "Conformidade com politicas, regras e normas de seguranca da informacao"),
    ("5.37", "Procedimentos operacionais documentados"),
]
PEOPLE = [
    ("6.1", "Selecao de pessoal"),
    ("6.2", "Termos e condicoes de contratacao"),
    ("6.3", "Conscientizacao, educacao e treinamento em seguranca da informacao"),
    ("6.4", "Processo disciplinar"),
    ("6.5", "Responsabilidades apos encerramento ou mudanca de emprego"),
    ("6.6", "Acordos de confidencialidade"),
    ("6.7", "Trabalho remoto"),
    ("6.8", "Relato de eventos de seguranca da informacao"),
]
PHYSICAL = [
    ("7.1", "Perimetros de seguranca fisica"),
    ("7.2", "Entrada fisica"),
    ("7.3", "Seguranca de escritorios, salas e instalacoes"),
    ("7.4", "Monitoramento de seguranca fisica"),
    ("7.5", "Protecao contra ameacas fisicas e ambientais"),
    ("7.6", "Trabalho em areas seguras"),
    ("7.7", "Mesa limpa e tela limpa"),
    ("7.8", "Localizacao e protecao de equipamentos"),
    ("7.9", "Seguranca de ativos fora das instalacoes"),
    ("7.10", "Midias de armazenamento"),
    ("7.11", "Servicos de suporte"),
    ("7.12", "Seguranca do cabeamento"),
    ("7.13", "Manutencao de equipamentos"),
    ("7.14", "Descarte seguro ou reutilizacao de equipamentos"),
]
TECH = [
    ("8.1", "Dispositivos finais de usuarios"),
    ("8.2", "Direitos de acesso privilegiado"),
    ("8.3", "Restricao de acesso a informacao"),
    ("8.4", "Acesso ao codigo-fonte"),
    ("8.5", "Autenticacao segura"),
    ("8.6", "Gestao de capacidade"),
    ("8.7", "Protecao contra malware"),
    ("8.8", "Gestao de vulnerabilidades tecnicas"),
    ("8.9", "Gestao de configuracao"),
    ("8.10", "Exclusao de informacao"),
    ("8.11", "Mascaramento de dados"),
    ("8.12", "Prevencao de vazamento de dados"),
    ("8.13", "Backup de informacao"),
    ("8.14", "Redundancia de instalacoes de processamento de informacao"),
    ("8.15", "Registro de eventos (logging)"),
    ("8.16", "Atividades de monitoramento"),
    ("8.17", "Sincronizacao de relogios"),
    ("8.18", "Uso de programas utilitarios privilegiados"),
    ("8.19", "Instalacao de software em sistemas operacionais"),
    ("8.20", "Seguranca de redes"),
    ("8.21", "Seguranca de servicos de rede"),
    ("8.22", "Segregacao de redes"),
    ("8.23", "Filtragem web"),
    ("8.24", "Uso de criptografia"),
    ("8.25", "Ciclo de vida de desenvolvimento seguro"),
    ("8.26", "Requisitos de seguranca de aplicacoes"),
    ("8.27", "Arquitetura e engenharia de sistemas seguros"),
    ("8.28", "Codificacao segura"),
    ("8.29", "Testes de seguranca em desenvolvimento e aceitacao"),
    ("8.30", "Desenvolvimento terceirizado"),
    ("8.31", "Separacao de ambientes de desenvolvimento, teste e producao"),
    ("8.32", "Gestao de mudancas"),
    ("8.33", "Informacao de teste"),
    ("8.34", "Protecao de sistemas de informacao durante testes de auditoria"),
]

# NBR ISO/IEC 27701:2026 — 49 controles Anexo A1 (controlador) e A2 (operador)
A1 = [
    ("A1.1", "Politica de privacidade e protecao de PII"),
    ("A1.2", "Papéis e responsabilidades de privacidade"),
    ("A1.3", "Privacidade desde a concepcao e por padrao"),
    ("A1.4", "Inventario de processamento de PII"),
    ("A1.5", "Base legal e gestao de consentimento"),
    ("A1.6", "Limitacao de finalidade do tratamento"),
    ("A1.7", "Minimizacao de dados"),
    ("A1.8", "Exatidao e atualizacao de PII"),
    ("A1.9", "Retencao e descarte de PII"),
    ("A1.10", "Direitos dos titulares de dados"),
    ("A1.11", "Avaliacao de impacto a protecao de dados (AIPD/RIPD)"),
    ("A1.12", "Contratos e gestao de operadores de PII"),
    ("A1.13", "Transferencia internacional de PII"),
    ("A1.14", "Notificacao de incidentes envolvendo PII"),
    ("A1.15", "Conscientizacao em privacidade"),
    ("A1.16", "Documentacao de obrigacoes do controlador"),
    ("A1.17", "Arranjos entre controladores conjuntos"),
    ("A1.18", "Limitacao da coleta de PII"),
    ("A1.19", "Aviso de privacidade ao titular"),
    ("A1.20", "Criterios de selecao de operadores"),
    ("A1.21", "Gestao de suboperadores"),
    ("A1.22", "Registro das atividades de tratamento"),
    ("A1.23", "Decisoes automatizadas e perfilamento"),
    ("A1.24", "Marketing e comunicacoes"),
    ("A1.25", "Uso de cookies e tecnologias similares"),
]
A2 = [
    ("A2.1", "Instrucoes documentadas do controlador ao operador"),
    ("A2.2", "Confidencialidade das pessoas que tratam PII"),
    ("A2.3", "Seguranca do tratamento pelo operador"),
    ("A2.4", "Autorizacao para subcontratacao de tratamento"),
    ("A2.5", "Assistencia ao controlador em direitos dos titulares"),
    ("A2.6", "Exclusao ou devolucao de PII ao termino"),
    ("A2.7", "Disponibilizacao de informacoes de conformidade"),
    ("A2.8", "Auditoria e inspecao pelo controlador"),
    ("A2.9", "Notificacao de incidentes ao controlador"),
    ("A2.10", "Localizacao e transferencia de PII pelo operador"),
    ("A2.11", "Gestao de acessos ao PII pelo operador"),
    ("A2.12", "Segregacao de PII entre clientes"),
    ("A2.13", "Monitoramento de conformidade contratual"),
    ("A2.14", "Retencao limitada pelo operador"),
    ("A2.15", "Restricao de uso para finalidades do controlador"),
    ("A2.16", "Gestao de mudancas no tratamento"),
    ("A2.17", "Continuidade do tratamento de PII"),
    ("A2.18", "Treinamento de privacidade para operadores"),
    ("A2.19", "Gestao de solicitacoes de titulares recebidas"),
    ("A2.20", "Registro de operacoes de tratamento pelo operador"),
    ("A2.21", "Criptografia e pseudonimizacao no tratamento"),
    ("A2.22", "Testes e avaliacoes periodicas de seguranca"),
    ("A2.23", "Encerramento seguro de contratos de tratamento"),
    ("A2.24", "Cooperacao com autoridades de protecao de dados"),
]


def build_27002():
    items = []
    for code, title in ORG:
        items.append({
            "code": code, "title": title, "category": "organizational",
            "module": "ISO27001", "catalog_version": "NBR ISO/IEC 27002:2022",
            "guidance_ref": f"NBR ISO/IEC 27002:2022 - {code}",
            "description": DESCRIPTIONS_27002[code],
        })
    for code, title in PEOPLE:
        items.append({
            "code": code, "title": title, "category": "people",
            "module": "ISO27001", "catalog_version": "NBR ISO/IEC 27002:2022",
            "guidance_ref": f"NBR ISO/IEC 27002:2022 - {code}",
            "description": DESCRIPTIONS_27002[code],
        })
    for code, title in PHYSICAL:
        items.append({
            "code": code, "title": title, "category": "physical",
            "module": "ISO27001", "catalog_version": "NBR ISO/IEC 27002:2022",
            "guidance_ref": f"NBR ISO/IEC 27002:2022 - {code}",
            "description": DESCRIPTIONS_27002[code],
        })
    for code, title in TECH:
        items.append({
            "code": code, "title": title, "category": "technological",
            "module": "ISO27001", "catalog_version": "NBR ISO/IEC 27002:2022",
            "guidance_ref": f"NBR ISO/IEC 27002:2022 - {code}",
            "description": DESCRIPTIONS_27002[code],
        })
    return items


def build_27701():
    items = []
    for code, title in A1:
        items.append({
            "code": code, "title": title, "category": "annex_a1",
            "module": "ISO27701", "catalog_version": "NBR ISO/IEC 27701:2026",
            "guidance_ref": f"NBR ISO/IEC 27701:2026 Anexo {code}",
            "description": DESCRIPTIONS_27701[code],
        })
    for code, title in A2:
        items.append({
            "code": code, "title": title, "category": "annex_a2",
            "module": "ISO27701", "catalog_version": "NBR ISO/IEC 27701:2026",
            "guidance_ref": f"NBR ISO/IEC 27701:2026 Anexo {code}",
            "description": DESCRIPTIONS_27701[code],
        })
    return items


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    c27002 = build_27002()
    c27701 = build_27701()
    (OUT / "iso27002_2022.json").write_text(json.dumps(c27002, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "iso27701.json").write_text(json.dumps(c27701, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"27002: {len(c27002)} | 27701: {len(c27701)} (A1={len(A1)}, A2={len(A2)})")
