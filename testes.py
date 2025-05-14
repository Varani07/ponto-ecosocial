from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time

data_inicio = datetime.now(ZoneInfo("America/Sao_Paulo"))

time.sleep(2)

data_fim = datetime.now(ZoneInfo("America/Sao_Paulo"))
resultado = data_fim - data_inicio
print(resultado, type(resultado))

string_delta = str(resultado)
string_tempo = string_delta.split(".")[0]
date_tempo = datetime.strptime(string_tempo, "%H:%M:%S")
print(date_tempo)

teste = datetime(1, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))
print(teste, "aqui")

from decimal import Decimal
valor_a_receber = Decimal("0")
valor_por_hora = Decimal("100")
hora = Decimal("1")
minuto = Decimal("10")
segundos = Decimal("30")
print("-"*40)
print(valor_por_hora*hora)
