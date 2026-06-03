from datetime import datetime, timedelta
from django.utils import timezone
import holidays

def calc_hrs_uteis_parado(data_inicio: datetime, data_fim: datetime):
    tz_atual = timezone.get_current_timezone()

    if timezone.is_naive(data_inicio):
        inicio = timezone.make_aware(data_inicio, tz_atual)
    else:
        inicio = data_inicio.astimezone(tz_atual)

    if timezone.is_naive(data_fim):
        fim = timezone.make_aware(data_fim, tz_atual)
    else:
        fim = data_fim.astimezone(tz_atual)

    if fim <= inicio:
        return 0.0
    feriados_br = holidays.country_holidays('BR', language='pt_BR')
    hrs_uteis_totais = 0.0

    dia_atual = inicio.date()
    dia_fim = fim.date()

    while dia_atual <= dia_fim:
        if dia_atual.weekday() < 5 and dia_atual not in feriados_br:
            exp_inicio = timezone.make_aware(datetime(dia_atual.year, dia_atual.month, dia_atual.day, 8, 0))
            exp_fim = timezone.make_aware(datetime(dia_atual.year, dia_atual.month, dia_atual.day, 20, 0))
            inicio_real = max(inicio, exp_inicio)
            fim_real = min(fim, exp_fim)

            if inicio_real < fim_real:
                diferenca = fim_real - inicio_real
                hrs_uteis_totais = diferenca.total_seconds() / 3600.0
            
        dia_atual += timedelta(days=1)
        
    return round(hrs_uteis_totais, 2)














            
