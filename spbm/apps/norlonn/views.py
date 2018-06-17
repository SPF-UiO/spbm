from decimal import Decimal

from django.contrib import messages as msg
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction, IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _

from spbm.helpers.auth import user_society
from .models import NorlonnReport
from ..society.models import Shift


@login_required
def index(request):
    reports = NorlonnReport.objects.all().order_by('-date')
    errors = []

    queryset = Shift.objects.select_related().prefetch_related('event__invoice').filter(norlonn_report__isnull=True,
                                                                                        event__processed__isnull=False)

    if request.user.has_perm('norlonn.generate_report'):
        shifts = queryset
    else:
        shifts = queryset.filter(event__society=user_society(request.user.spfuser))

    for s in shifts:
        if s.worker.norlonn_number is None:
            errors.append(_("Worker %s (for %s) lacks norlonn number!" % (s.worker, s.event)))

        if not s.event.invoice.paid:
            errors.append(_("%s (for %s) --- Invoice not paid" % (s.worker, s.event)))

    return render(request, 'norlonn/index.jinja', {'reports': reports, 'errors': errors})


@login_required
@permission_required('norlonn.generate_report', raise_exception=True)
def generate_report(request):
    if request.method != "POST":
        return redirect(index)

    errors = []
    succ = []
    shifts = Shift.objects.filter(norlonn_report__isnull=True, event__processed__isnull=False)
    shifts_to_payroll = []

    if not shifts.exists():
        msg.error(request, _("No shifts to generate a payroll report for."))
        return redirect('wages')

    for s in shifts:
        if s.worker.norlonn_number is None:
            errors.append(_("ERR: %s - %s --- Lacks norlonn number" % (s.worker, s.event)))
            continue

        if not s.event.invoice.paid:
            errors.append(_("ERR: %s - %s --- Invoice not paid" % (s.worker, s.event)))
            continue

        succ.append(_("OK: %s - %s" % (s.worker, s.event)))
        shifts_to_payroll.append(s)

    if not shifts_to_payroll:
        msg.error(request, _("There are no valid shifts that can be added to the payroll report."))
        return redirect('wages')
    else:
        try:
            with transaction.atomic():
                report = NorlonnReport()
                report.save()
        except IntegrityError:
            msg.error(request, _("A payroll already exists for the given date."))
            return redirect('wages')
        except Exception as e:
            raise e
        else:
            for shift in shifts_to_payroll:
                with transaction.atomic():
                    shift.norlonn_report = report
                    shift.save()
            msg.success(request, _("Payroll successfully generated! You may now export it to the wage system."))

    return render(request, 'norlonn/report.jinja', {'errors': errors, 'success': succ})


@login_required
@permission_required('norlonn.export_report', raise_exception=True)
def export_report(request, date):
    nr = get_object_or_404(NorlonnReport, date=date)
    linjer = []
    personshift = {}

    shift = Shift.objects.filter(norlonn_report=nr)
    for s in shift:
        if s.worker.norlonn_number in personshift:
            personshift[s.worker.norlonn_number].append(s)
        else:
            personshift[s.worker.norlonn_number] = [s, ]

    for (nl, ss) in personshift.items():
        total = Decimal(0)

        for s in ss:
            total += s.hours * s.wage

        total = total * Decimal("100")
        total = total.quantize(Decimal("10"))
        linjer.append(";" + str(s.worker.norlonn_number) + ";H1;100;" + str(total) + ";")

    return HttpResponse("\n".join(linjer), content_type="text/plain; charset=utf-8")
