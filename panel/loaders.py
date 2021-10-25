from datetime import date, datetime, timedelta
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from panel.models import Duty


def change_duties(request):
    date_start = date(year=2017, month=9, day=1)

    for duty in Duty.objects.filter(date__gte = date_start):

        if duty.pdt:

            # zainicjowanie liczników
            fdp_time = block_time = timedelta(seconds=0)
            landings = 0

            # wyznaczenie posortowanej tableli zamkniętych operacji na PDT
            operation_set = []
            for operation in duty.pdt.operation_set.filter(status='closed').order_by('time_start'):
                off_block = datetime.combine(duty.pdt.date, operation.time_start)
                on_block = datetime.combine(duty.pdt.date, operation.time_end)
                if on_block < off_block:
                    on_block += timedelta(days=1)
                operation_set += [{'off_block': off_block, 'on_block': on_block, 'landings': operation.landings}]

            # bufory przed dla FDP w zależności od rodzaju lotu
            if duty.pdt.flight_type in ['03B', '03C', '03D', '03E']:
                pre_buffer = timedelta(seconds=30 * 60)
            elif duty.pdt.flight_type in ['02', '02H', '04', '05']:
                pre_buffer = timedelta(seconds=15 * 60)
            else:
                pre_buffer = timedelta(seconds=0)

            # bufory po dla FDP w zależności od rodzaju lotu
            if duty.pdt.flight_type in ['03B', '03C', '03D', '03E', '02', '02H', '04', '05']:
                post_buffer = timedelta(seconds=15 * 60)
            else:
                post_buffer = timedelta(seconds=0)

            # wyznaczenie FDP dla poszcególnych operacji
            for i in range(0, len(operation_set)):
                # jeśli poprzednia zakończyła się wcześniej niż post_buffer temu to start od początku operacji
                if i > 0 and (operation_set[i]['off_block'] - operation_set[i - 1]['on_block'] <= post_buffer):
                    start_fdp = operation_set[i]['off_block']
                # jeśli między operacjami nie ma czasu na post i pre_buffer to start po post_buffer poprzedniej
                elif i > 0 and (operation_set[i]['off_block'] - operation_set[i - 1]['on_block'] <= (
                    pre_buffer + post_buffer)):
                    start_fdp = operation_set[i - 1]['on_block'] + post_buffer
                # wystarczający odstęp albo pierwsza operacji
                else:
                    start_fdp = operation_set[i]['off_block'] - pre_buffer

                # jeśli nastęona rozpoczęła się wcześniej niż post_buffer po tej to koniec na początku następnej
                if i < len(operation_set) - 1 and (
                        operation_set[i + 1]['off_block'] - operation_set[i]['on_block'] <= post_buffer):
                    end_fdp = operation_set[i + 1]['off_block']
                # wystarczający odstęp lub ostatnia
                else:
                    end_fdp = operation_set[i]['on_block'] + post_buffer

                fdp_time += end_fdp - start_fdp
                block_time += operation_set[i]['on_block'] - operation_set[i]['off_block']
                landings += operation_set[i]['landings']

            start_duty = operation_set[0]['off_block'] - pre_buffer
            end_duty = operation_set[-1]['on_block'] + post_buffer
            duty_time = end_duty - start_duty

            duty.duty_time = duty_time
            duty.duty_time_from = start_duty.time()
            duty.duty_time_to = end_duty.time()
            duty.fdp_time = fdp_time
            duty.block_time = block_time
            duty.landings = landings
            duty.save()

    return HttpResponseRedirect(reverse('dispatcher'))

