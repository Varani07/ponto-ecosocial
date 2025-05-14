from rich.table import Table
from rich.text import Text
from rich.console import Console
from rich.live import Live
from rich import box

import os, sys, termios, tty, select

from decimal import Decimal, ROUND_DOWN

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time

from ..conexao_banco import DAO as dao

from dotenv import load_dotenv

load_dotenv()
VALOR_POR_HORA = Decimal(str(os.getenv('VALOR_POR_HORA')))

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
        tempo_corrido = datetime.now(ZoneInfo("America/Sao_Paulo"))

        try:
            with Live(console=console, refresh_per_second=4) as live:
                while True:
                    if pausado:
                        pass
                    else:
                        data_inicio_completa = data_inicio + tempo_pausado
                        hora_atual = datetime.now(ZoneInfo("America/Sao_Paulo"))
                        tempo_corrido = datetime.strftime(datetime.strptime(str(hora_atual - data_inicio_completa).split(".")[0], "%H:%M:%S"), "%H:%M:%S")

                    tempo_repartido = str(tempo_corrido).split(":")
                    horas_para_calcular = Decimal(tempo_repartido[0])
                    minutos_para_calcular = Decimal(tempo_repartido[1])
                    segundos_para_calcular = Decimal(tempo_repartido[2])

                    ganhos = Decimal('0')

                    if horas_para_calcular > 0:
                        ganhos += VALOR_POR_HORA * horas_para_calcular
                    if minutos_para_calcular > 0:
                        ganhos += (VALOR_POR_HORA / Decimal(60)) * minutos_para_calcular
                    if segundos_para_calcular > 0:
                        ganhos += (VALOR_POR_HORA / Decimal(3600)) * segundos_para_calcular

                    conteudo = Text(f"""
                        {tempo_corrido}

                        [p] pausar/play | [z] zerar | [w] salvar e sair | [q] sair


        Ganhos: R${ganhos.quantize(Decimal("0.01"), rounding=ROUND_DOWN)}                   {mensagem_ativa}
                    """)

                    live.update(conteudo)
                    key = cls.pegar_chave_sem_bloquear()

                    try:
                        if key == "p":
                            if ciclo == 0:
                                inicio_tempo_pausado = datetime.now(ZoneInfo("America/Sao_Paulo"))
                                ciclo += 1
                                mensagem_ativa = "Horario Pausado"
                            else:
                                fim_tempo_pausado = datetime.now(ZoneInfo("America/Sao_Paulo"))
                                ciclo = 0
                                tempo_pausado += fim_tempo_pausado - inicio_tempo_pausado
                                mensagem_ativa = ""
                                if tempo_corrido == "00:00:00":
                                    tempo_pausado = timedelta(hours=0, minutes=0, seconds=0)
                                    data_inicio = datetime.now(ZoneInfo("America/Sao_Paulo"))
                            pausado = not pausado
                        elif key == "z":
                            data_inicio = datetime.now(ZoneInfo("America/Sao_Paulo"))
                            tempo_pausado = timedelta(hours=0, minutes=0, seconds=0)
                            tempo_corrido = datetime.strftime(datetime.strptime(str(timedelta(hours=0, minutes=0, seconds=0)).split(".")[0], "%H:%M:%S"), "%H:%M:%S") 
                            mensagem_ativa = "Horario Resetado"
                        elif key == "w":
                            live.stop()
                            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

                            if not pausado:
                                inicio_tempo_pausado = datetime.now(ZoneInfo("America/Sao_Paulo"))

                            data_final = datetime.now(ZoneInfo("America/Sao_Paulo"))
                            mensagem = cls.definir_mensagem()
                            mensagem_aviso = ""
                            while True:
                                mensagem_confirmacao = Text(f"""
                                INFORMAÇÃO CARGA HORARIA

                        Data de inicio: {datetime.strftime(data_inicio, "%d/%m/%Y - %H:%M:%S")}
                        Data final: {datetime.strftime(data_final, "%d/%m/%Y - %H:%M:%S")}

                        Tempo trabalhado: {tempo_corrido}
                        Lucro: {ganhos.quantize(Decimal("0.01"), rounding=ROUND_DOWN)}

                        R${VALOR_POR_HORA} por hora

                        Mensagem: {mensagem}


                                        {mensagem_aviso}
                                                        """)
                                console.print(mensagem_confirmacao)
                                confirmacao = console.input(Text("""            varani | [c] confirmar | [q] sair: """))
                                os.system("clear")
                                if confirmacao == "c":
                                    try:
                                        inserir_carga_horaria_dao = dao()
                                        inserir_carga_horaria_dao.inserir("carga_horaria", "horario_inicio, horario_final, tempo, valor_hora, valor_total, pago, mensagem", "%s, %s, %s, %s, %s, %s, %s", (datetime.strftime(data_inicio, "%d/%m/%Y - %H:%M:%S"), datetime.strftime(data_final, "%d/%m/%Y - %H:%M:%S"), tempo_corrido, VALOR_POR_HORA, ganhos, False, mensagem))
                                        break
                                    except Exception as e:
                                        mensagem_aviso = e
                                elif confirmacao == "q":
                                    break
                                else:
                                    mensagem_aviso = "Escolha Inválida"
                            if confirmacao == "c":
                                break
                            else:
                                if not pausado:
                                    fim_tempo_pausado = datetime.now(ZoneInfo("America/Sao_Paulo"))
                                    tempo_pausado += fim_tempo_pausado - inicio_tempo_pausado
                                    if tempo_corrido == "00:00:00":
                                        tempo_pausado = timedelta(hours=0, minutes=0, seconds=0)
                                        data_inicio = datetime.now(ZoneInfo("America/Sao_Paulo"))
                                tty.setcbreak(fd)
                                live.start()
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

    @staticmethod
    def definir_mensagem():
        os.system("clear")
        mensagem = console.input("Digite o que foi feito nesse tempo: ")
        os.system("clear")
        return mensagem
