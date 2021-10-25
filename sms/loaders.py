import csv
from sms.models import SMSHazard, SMSHazardRev, SMSRisk, SMSEvent, SMSFailure
from panel.models import PDT

def make_rev():
    for hazard in SMSHazard.objects.all():
        revision = SMSHazardRev(hazard=hazard, rev_num = 1, rev_date = hazard.hazard_date, rev_last = True,
                                company_area = hazard.company_area, name = hazard.name, due_date = hazard.due_date,
                                responsible = hazard.responsible, control = hazard.control, remarks = hazard.remarks)
        revision.save()
    return


def risk_rev():
    for risk in SMSRisk.objects.all():
        risk.risk_ref = risk.smshazard.hazard_ref+'/01'
        risk.rev_date = risk.smshazard.hazard_date
        risk.save()
    return

def events():
    wb = Workbook()
    ws = wb.active
    row = 1
    code, name, short, desc = '', '', '', ''
    with open('c:/mierzwik/salt/1000000.txt', 'r') as f:
        for line in f:
            line = line.replace('\n', '').strip()
            try:
                new_code = int(line)
                if code != '':
                    ws['A%d' % row] = code
                    ws['B%d' % row] = name
                    ws['C%d' % row] = desc
                    row += 1
                code = new_code
                name, short, desc = '', '', ''
            except:
                if line != '':
                    if name != '' and short != '':
                        if desc == '':
                            desc = line
                        else:
                            desc += ' ' + line
                    elif name != '':
                        short = line
                    else:
                        name = line
    wb.save('ecccairs.xlsx')
    return True


def load_hazards():
    with open('C:\Mierzwik\salt\hazards2.csv') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
           hazard, created = SMSHazard.objects.get_or_create(
           hazard_type=row[0],
           hazard_ref=row[1],
           hazard_date=row[2],
           company_area=row[3],
           name=row[4],
           due_date=(None if row[5]=='' else row[5]),
           responsible=row[6],
           control=row[7],
           remarks=row[8]
           )
           risk, created = SMSRisk.objects.get_or_create(
           smshazard=hazard,
           description=row[9],
           init_probability=row[10],
           init_impact=row[11].upper(),
           mitigation=row[12],
           res_probability=row[13],
           res_impact=row[14].upper()
           )
    return True

def load_events():
    with open('C:\Mierzwik\salt\events1.csv') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            event, created = SMSEvent.objects.get_or_create(
            aircraft=row[0],
            pic=row[1],
            event_date=row[2],
            oper_type=row[3],
            event_type=row[4],
            pkbwl_ref=row[5],
            pkbwl_date=row[6],
            examiner=row[7],
            description=row[8],
            scrutiny=row[9],
            findings=row[11],
            closure=row[12],
            remarks=row[13]
           )
    return True

def load_failures():
    with open('C:\Mierzwik\salt\\failures1.csv') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            failure, created = SMSFailure.objects.get_or_create(
            aircraft=row[0],
            person=row[1],
            failure_date=row[2],
            description=row[3],
            repair_date=row[5],
            repair_desc=row[6],
            crs=row[7]
           )
    return True


