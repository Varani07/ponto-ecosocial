from rich.table import Table
from rich.text import Text
from rich.console import Console
from rich.live import Live
from rich import box

import os, sys, termios, tty, select

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time

console = Console()

class Interface():
    def __init__(self):
        pass
    
    @classmethod
    def inicio(cls):
        os.system("clear")

        opcoes = Table(box=box.DOUBLE_EDGE)
        opcoes.add_column("Opcoes", justify="center", style="bold white")
        opcoes.add_column("Descricao", justify="center", style="bold white")

        opcoes.add_row("1", "Iniciar!")
        opcoes.add_row("2", "Gerenciar Horarios")
        opcoes.add_row("3", "Ver Detalhes (Credito) ")
        opcoes.add_row("4", "Horas Trabalhadas")
        opcoes.add_row("*", "Sair")

        while True:
           console.print(opcoes)
           escolha = console.input("varani: ")
           os.system("clear")
           try:
               num_escolhido = int(escolha)
  
               match num_escolhido:
                   case 1:
                       cls.passando_tempo()
                   case 2:
                       pass
                   case 3:
                       pass
                   case 4:
                       pass
                   case _:
                       cls.caixa_erro("Numero Invalido")
           except ValueError:
               if escolha == "*":
                   break
               else:
                   cls.caixa_erro("Caracter Invalido")

    @classmethod
    def passando_tempo(cls):
        os.system("clear")

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)

        mensagem_ativa = ""
        data_inicio = datetime.now(ZoneInfo("America/Sao_Paulo"))
        pausado = False
        ciclo = 0
        tempo_pausado = timedelta(hours=0, minutes=0, seconds=0)
        inicio_tempo_pausado = datetime.now(ZoneInfo("America/Sao_Paulo"))

        try:
            with Live(console=console, refresh_per_second=4) as live:
                while True:
                    if pausado:
                        pass
                    else:
                        data_inicio_completa = data_inicio + tempo_pausado
                        hora_atual = datetime.now(ZoneInfo("America/Sao_Paulo"))
                        tempo_corrido = datetime.strftime(datetime.strptime(str(hora_atual - data_inicio_completa).split(".")[0], "%H:%M:%S"), "%H:%M:%S")

                    conteudo = Text(f"""
                        {mensagem_ativa}

                        {tempo_corrido}

                        [p] pausar/play | [z] zerar | [w] salvar e sair | [q] sair
                    """)

                    live.update(conteudo)
                    key = cls.pegar_chave_sem_bloquear()

                    try:
                        if key == "p":
                            if ciclo == 0:
                                inicio_tempo_pausado = datetime.now(ZoneInfo("America/Sao_Paulo"))
                                ciclo += 1
                            else:
                                fim_tempo_pausado = datetime.now(ZoneInfo("America/Sao_Paulo"))
                                ciclo = 0
                                tempo_pausado += fim_tempo_pausado - inicio_tempo_pausado
                            pausado = not pausado
                        elif key == "z":
                            data_inicio = datetime.now(ZoneInfo("America/Sao_Paulo"))
                        elif key == "w":
                            pass
                        elif key == "q":
                            break
                    except TypeError:
                        pass
                    time.sleep(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            os.system("clear")

    @staticmethod
    def caixa_erro(mensagem):
        info_erro = Table(box=box.DOUBLE_EDGE)
        info_erro.add_column("Alerta", justify="center", style="red")
        info_erro.add_row(f"[red] {mensagem} [/]")
        console.print(info_erro)

    @staticmethod
    def pegar_chave_sem_bloquear():
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            return sys.stdin.read(1)
        return None
