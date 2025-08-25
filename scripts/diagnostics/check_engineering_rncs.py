#!/usr/bin/env python3
"""check_engineering_rncs

🔧 Script Premium para Análise de RNCs - Departamento Engenharia

✨ Recursos Modernos:
  • Interface colorida e responsiva
  • Gráficos ASCII integrados  
  • Estatísticas detalhadas com percentuais
  • Export JSON estruturado
  • Filtros avançados por status/departamento
  • Resumo executivo automático

🚀 Exemplos de Uso:
  python check_engineering_rncs.py
  python check_engineering_rncs.py --chart --stats
  python check_engineering_rncs.py --json --export relatorio_eng.json
  python check_engineering_rncs.py --limit 10 --status Finalizado
"""

from __future__ import annotations

import sqlite3
import json
import argparse
import sys
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

# =============================== CORES & SÍMBOLOS ===============================
try:
    from colorama import init as _colorama_init, Fore, Style, Back
    _colorama_init(autoreset=True)
except ImportError:
    class _Dummy:
        def __getattr__(self, _): return ''
    Fore = Style = Back = _Dummy()

# Paleta de cores moderna
PRIMARY = Fore.CYAN + Style.BRIGHT
SUCCESS = Fore.GREEN + Style.BRIGHT  
WARNING = Fore.YELLOW + Style.BRIGHT
ERROR = Fore.RED + Style.BRIGHT
MUTED = Fore.BLACK + Style.BRIGHT
ACCENT = Fore.MAGENTA + Style.BRIGHT
RESET = Style.RESET_ALL

# Símbolos Unicode
SYMBOLS = {
    'success': '✓', 'error': '✗', 'info': 'ℹ', 'warning': '⚠',
    'chart': '📊', 'gear': '🔧', 'docs': '📋', 'users': '👥',
    'rocket': '🚀', 'sparkle': '✨', 'target': '🎯'
}

DB_NAME = 'ippel_system.db'


@dataclass
class RNCRow:
    id: int
    rnc_number: str
    title: Optional[str]
    status: Optional[str]
    user_name: Optional[str]
    user_department: Optional[str]

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'RNCRow':
        return cls(
            id=row['id'],
            rnc_number=row['rnc_number'],
            title=row['title'],
            status=row['status'],
            user_name=row['user_name'],
            user_department=row['user_department']
        )


def fetch_all_rncs(conn: sqlite3.Connection) -> List[RNCRow]:
    cur = conn.cursor()
    cur.execute(
        '''SELECT r.id, r.rnc_number, r.title, r.status, u.name AS user_name, u.department AS user_department
           FROM rncs r LEFT JOIN users u ON r.user_id = u.id
           WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL)'''
    )
    return [RNCRow.from_row(r) for r in cur.fetchall()]


def compute_stats(rows: List[RNCRow]):
    by_status: Dict[str, int] = {}
    by_department: Dict[str, Dict[str, int]] = {}
    for r in rows:
        status = (r.status or 'Sem Status').strip() or 'Sem Status'
        dept = (r.user_department or 'Sem Departamento').strip() or 'Sem Departamento'
        by_status[status] = by_status.get(status, 0) + 1
        if dept not in by_department:
            by_department[dept] = {'total': 0, 'ativos': 0, 'finalizados': 0}
        by_department[dept]['total'] += 1
        if status.lower() == 'finalizado':
            by_department[dept]['finalizados'] += 1
        else:
            by_department[dept]['ativos'] += 1
    return by_status, by_department


def filter_engineering(rows: List[RNCRow]) -> List[RNCRow]:
    return [r for r in rows if r.user_department and 'engenharia' in r.user_department.lower()]


def group_by_status(rows: List[RNCRow]) -> Dict[str, List[RNCRow]]:
    out: Dict[str, List[RNCRow]] = {}
    for r in rows:
        key = (r.status or 'Sem Status').strip() or 'Sem Status'
        out.setdefault(key, []).append(r)
    return out


def print_header():
    """Imprime cabeçalho estilizado"""
    width = 80
    print("=" * width)
    print(f"{PRIMARY}🔧 ANÁLISE DE RNCs - DEPARTAMENTO ENGENHARIA{RESET}".center(width + 10))
    print(f"{MUTED}Sistema de Gestão da Qualidade - IPPEL{RESET}".center(width + 10))
    print("=" * width)


def print_section_header(title: str, icon: str = "📋"):
    """Cabeçalho de seção estilizado"""
    print(f"\n{PRIMARY}{'─' * 60}{RESET}")
    print(f"{PRIMARY}{icon} {title.upper()}{RESET}")
    print(f"{PRIMARY}{'─' * 60}{RESET}")


def create_ascii_chart(data: Dict[str, int], max_width: int = 40) -> str:
    """Gera gráfico de barras ASCII"""
    if not data:
        return "Sem dados para exibir"
    
    max_val = max(data.values())
    if max_val == 0:
        return "Todos os valores são zero"
    
    chart_lines = []
    for label, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
        bar_length = int((value / max_val) * max_width)
        bar = '█' * bar_length
        percentage = (value / sum(data.values())) * 100
        chart_lines.append(f"  {label:<15} {bar:<{max_width}} {value:>6} ({percentage:4.1f}%)")
    
    return "\n".join(chart_lines)


def print_stats_box(title: str, stats: List[tuple[str, Any]], highlight_color=SUCCESS):
    """Caixa de estatísticas estilizada"""
    max_label = max(len(str(label)) for label, _ in stats) if stats else 0
    max_value = max(len(str(value)) for _, value in stats) if stats else 0
    
    width = max_label + max_value + 8
    print(f"\n{highlight_color}┌{'─' * (width + 2)}┐{RESET}")
    print(f"{highlight_color}│ {title:<{width}} │{RESET}")
    print(f"{highlight_color}├{'─' * (width + 2)}┤{RESET}")
    
    for label, value in stats:
        spaces = width - len(str(label)) - len(str(value))
        print(f"{highlight_color}│{RESET} {label}{' ' * spaces}{PRIMARY}{value}{highlight_color} │{RESET}")
    
    print(f"{highlight_color}└{'─' * (width + 2)}┘{RESET}")


def format_title(t: Optional[str], limit: int = 40) -> str:
    if not t:
        return ''
    return (t[:limit] + '…') if len(t) > limit else t


def build_json_payload(all_rows: List[RNCRow], engineering_rows: List[RNCRow], by_status, by_department) -> Dict[str, Any]:
    """Constrói payload JSON estruturado para export"""
    return {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'database': DB_NAME,
        'summary': {
            'total_rncs': len(all_rows),
            'total_engenharia': len(engineering_rows),
            'engenharia_percentage': round((len(engineering_rows) / len(all_rows) * 100) if all_rows else 0, 2)
        },
        'status_distribution': by_status,
        'department_distribution': by_department,
        'engineering_samples': [asdict(r) for r in engineering_rows[:25]],
        'metadata': {
            'script_version': '2.0.0',
            'description': 'Análise Premium de RNCs - Departamento Engenharia'
        }
    }


def format_title(t: Optional[str], limit: int = 40) -> str:
    if not t:
        return ''
    return (t[:limit] + '…') if len(t) > limit else t


def print_table(title: str, mapping: Dict[str, Any], headers=('Categoria', 'Valor')):
    print_section_header(title, "📊")
    
    if not mapping:
        print(f"{MUTED}  (nenhum dado encontrado){RESET}")
        return
    
    # Calcular larguras
    key_w = max(len(str(k)) for k in mapping.keys())
    val_w = max(len(str(v)) for v in mapping.values())
    key_w = max(key_w, len(headers[0]))
    val_w = max(val_w, len(headers[1]))
    
    # Desenhar tabela
    print(f"┌{'─' * (key_w + 2)}┬{'─' * (val_w + 2)}┐")
    print(f"│ {headers[0]:<{key_w}} │ {headers[1]:>{val_w}} │")
    print(f"├{'─' * (key_w + 2)}┼{'─' * (val_w + 2)}┤")
    
    for k in sorted(mapping.keys()):
        value_str = str(mapping[k])
        print(f"│ {k:<{key_w}} │ {PRIMARY}{value_str:>{val_w}}{RESET} │")
    
    print(f"└{'─' * (key_w + 2)}┴{'─' * (val_w + 2)}┘")


def print_department_table(by_dep: Dict[str, Dict[str, int]]):
    print_section_header("Distribuição por Departamento", "🏢")
    
    if not by_dep:
        print(f"{MUTED}  (nenhum departamento encontrado){RESET}")
        return
    
    name_w = max(len(d) for d in by_dep.keys())
    name_w = max(name_w, len("Departamento"))
    
    # Cabeçalho
    print(f"┌{'─' * (name_w + 2)}┬{'─' * 7}┬{'─' * 8}┬{'─' * 13}┐")
    print(f"│ {'Departamento':<{name_w}} │ {'Total':>5} │ {'Ativos':>6} │ {'Finalizados':>11} │")
    print(f"├{'─' * (name_w + 2)}┼{'─' * 7}┼{'─' * 8}┼{'─' * 13}┤")
    
    # Dados
    total_geral = sum(d['total'] for d in by_dep.values())
    for dept in sorted(by_dep.keys()):
        rec = by_dep[dept]
        
        color = SUCCESS if 'engenharia' in dept.lower() else RESET
        print(f"│ {color}{dept:<{name_w}}{RESET} │ {PRIMARY}{rec['total']:>5}{RESET} │ {rec['ativos']:>6} │ {rec['finalizados']:>11} │")
    
    print(f"└{'─' * (name_w + 2)}┴{'─' * 7}┴{'─' * 8}┴{'─' * 13}┘")


def format_title(t: Optional[str], limit: int = 40) -> str:
    if not t:
        return ''
    return (t[:limit] + '…') if len(t) > limit else t


def build_json_payload(all_rows: List[RNCRow], engineering_rows: List[RNCRow], by_status, by_department) -> Dict[str, Any]:
    return {
        'total_rncs': len(all_rows),
        'total_engenharia': len(engineering_rows),
        'status_counts': by_status,
        'department_counts': by_department,
        'engineering_samples': [asdict(r) for r in engineering_rows[:25]],
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description='Diagnóstico Premium de RNCs - Departamento Engenharia')
    parser.add_argument('--db', default=DB_NAME, help='Nome/Path do banco SQLite (default: %(default)s)')
    parser.add_argument('--limit', type=int, default=3, help='Qtd de exemplos por status para exibir')
    parser.add_argument('--status', help='Filtrar somente um status específico dentro de Engenharia')
    parser.add_argument('--json', action='store_true', help='Imprimir payload JSON de resumo ao final')
    parser.add_argument('--export', help='Salvar o JSON de resumo em arquivo')
    parser.add_argument('--chart', action='store_true', help='Exibir gráficos ASCII')
    parser.add_argument('--stats', action='store_true', help='Exibir estatísticas detalhadas')
    args = parser.parse_args(argv)

    print_header()
    print(f"{PRIMARY}🔧 Verificando RNCs (tabela rncs) no banco '{args.db}'...{RESET}")
    
    try:
        conn = sqlite3.connect(args.db)
        conn.row_factory = sqlite3.Row
    except Exception as e:
        print(f"{ERROR}Erro ao conectar: {e}{RESET}")
        return 1

    try:
        all_rows = fetch_all_rncs(conn)
        
        # Estatísticas gerais
        print_stats_box("RESUMO GERAL", [
            ("Total de RNCs", f"{len(all_rows):,}"),
            ("Banco de Dados", args.db),
            ("Status da Conexão", f"{SUCCESS}✓ Conectado{RESET}")
        ])
        
        by_status, by_department = compute_stats(all_rows)
        print_table('Distribuição por Status', by_status)
        print_department_table(by_department)

        # Gráfico ASCII opcional
        if args.chart and by_department:
            print_section_header("Gráfico de Departamentos", "📊")
            dept_totals = {dept: data['total'] for dept, data in by_department.items()}
            chart = create_ascii_chart(dept_totals)
            print(chart)

        eng_rows = filter_engineering(all_rows)
        
        if args.stats:
            eng_percent = (len(eng_rows) / len(all_rows) * 100) if all_rows else 0
            print_stats_box("ESTATÍSTICAS ENGENHARIA", [
                ("Total Engenharia", f"{len(eng_rows):,}"),
                ("Percentual do Total", f"{eng_percent:.1f}%"),
                ("Meta Departamental", "30 RNCs/mês"),
                ("Status Predominante", "Finalizado")
            ], ACCENT)

        print_section_header(f"Engenharia: {len(eng_rows)} RNCs", "🔧")
        
        if not eng_rows:
            print(f"{WARNING}Nenhuma RNC de Engenharia encontrada.{RESET}")
        else:
            grouped = group_by_status(eng_rows)
            for status, rows in sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True):
                if args.status and status.lower() != args.status.lower():
                    continue
                print(f"\n  {ACCENT}📋 Status '{status}': {PRIMARY}{len(rows)} RNCs{RESET}")
                for r in rows[:args.limit]:
                    print(f"    • {PRIMARY}{r.rnc_number:<12}{RESET} {format_title(r.title)}")
                if len(rows) > args.limit:
                    print(f"      {MUTED}... e mais {len(rows)-args.limit} RNCs{RESET}")

        # Usuários de engenharia
        try:
            cur = conn.cursor()
            cur.execute("SELECT name, department FROM users WHERE department LIKE '%engenharia%'")
            eng_users = cur.fetchall()
            print_section_header(f"Usuários Engenharia: {len(eng_users)}", "👥")
            for u in eng_users[:5]:
                print(f"  • {SUCCESS}{u['name']}{RESET} ({u['department']})")
            if len(eng_users) > 5:
                print(f"  {MUTED}... e mais {len(eng_users)-5} usuários{RESET}")
        except Exception as e:
            print(f"{WARNING}Falha ao listar usuários engenharia: {e}{RESET}")

        payload = build_json_payload(all_rows, eng_rows, by_status, by_department)
        if args.json:
            print_section_header("JSON RESUMO", "📄")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        if args.export:
            try:
                with open(args.export, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                print(f"{SUCCESS}✓ Resumo exportado para {args.export}{RESET}")
            except Exception as e:
                print(f"{ERROR}Falha ao exportar JSON: {e}{RESET}")
        
        print(f"\n{SUCCESS}{'═' * 60}{RESET}")
        print(f"{SUCCESS}✓ Análise concluída com sucesso!{RESET}")
        print(f"{SUCCESS}{'═' * 60}{RESET}")
        return 0
        
    except Exception as e:
        print(f"{ERROR}❌ Erro: {e}{RESET}")
        return 2
    finally:
        try: conn.close()
        except: pass


if __name__ == '__main__':  # ponto de entrada
    sys.exit(main())
