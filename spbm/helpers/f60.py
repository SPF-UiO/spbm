# -*- coding:utf-8 -*-
# kate: indent-width: 4;
"""Denne modulen lager en PDF-faktura etter norsk standard f60

PDF-filen kan skrives ut på f60-skjema (GIRO F60-1), eller sendes som en
elektronisk versjon av denne.

Den krever python-modulen `reportlab'; som heter python-reportlab i linux-
verdenen og kan lastes ned fra nettet for alle andre:

http://www.reportlab.org/


Her er et eksempel på hvordan man bruker modulen:

filnavn = '/tmp/testfaktura.pdf'
faktura = f60(filnavn, overskriv=True)
faktura.settFakturainfo(
  fakturanr=03,
  utstedtEpoch=1145542709,
  forfallEpoch=1146546709,
  fakturatekst=u"Produksjon i august",
  vilkaar=u"Takk for handelen, kom gjerne igjen.",
  kid='4466986711175280')
faktura.settFirmainfo({'firmanavn':'Firma Ein',
                        'kontaktperson':'Rattatta Hansen',
                        'adresse':u'Surdalsøyra',
                        'postnummer':8999,
                        'poststed':u'Fløya',
                        'kontonummer':99999999999,
                        'organisasjonsnummer':876876,
                        'telefon':23233322,
                        'epost':'ratata@ta.no'})

# kundeinfo er:
#   o Kundenummer
#   o Navn og fakturaadresse
faktura.settKundeinfo(06, "Topert\nRopertgata 33\n9022 Nissedal")

# ordrelinja er lister av lister, hvor hver liste har følgende elementer:
#   o Linjenavn (fri tekst)
#   o Antall
#   o Pris i kroner _for en vare_
#   o Mva-avgift for varen
faktura.settOrdrelinje([ ["Leder", 1, 300, 25], ['Reportasje', 1, 3000, 25], ])


if faktura.lagEpost():
    print "Kvittering laget i", filnavn

Se forøvrig http://code.google.com/p/finfaktura/wiki/PythonF60
"""
###########################################################################
#    Copyright (C) 2005-2009 Håvard Gulldahl
#    <havard@lurtgjort.no>
#
#    Lisens: GPL2
#
# $Id: f60.py 541 2009-04-12 19:20:55Z havard.gulldahl $
###########################################################################

import logging
import time

import locale
import os
import types
from io import StringIO


class f60Eksisterer(Exception): pass


class f60Feil(Exception): pass


class f60FeilKID(Exception): pass


class f60InstallasjonsFeil(Exception): pass


try:
    import reportlab
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm, inch
    from reportlab.lib.colors import yellow, pink, white
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen.pdfimages import PDFImage

    REPORTLAB = True
except ImportError:
    REPORTLAB = False
    raise f60InstallasjonsFeil("python-modulen `reportlab' mangler. Kan ikke lage PDF!")

__version__ = '0.18'
__license__ = 'GPLv2'
__author__ = 'H. Gulldahl (havard@gulldahl.no)'
__date__ = '$Date: 2015-08-16 20:49:16 +0200 (sø. 16. aug. 2015) $'

try:
    REPORTLAB2 = (reportlab.Version[0] >= '2')
except (AttributeError, IndexError):
    logging.warn('Reportlab-versjon kunne ikke leses. Dette er ikke versjon 2 eller nyere')
    REPORTLAB2 = False

# LOCALE = True
# LOCALE = False
# sett norsk tegngiving (bl.a. for ',' som desimal og 'kr')
# for x in ('norwegian', 'nb_NO.UTF8', 'nb_NO.ISO8859-1', 'nb_NO', 'nn_NO', 'no_NO', 'no'):
#    # har ulike navn på ulike plattformer... sukk...
#    try:
#        locale.setlocale(locale.LC_ALL, x)
#        logging.debug('satte locale : %s -> %s', x, locale.getlocale())
#        LOCALE = True
#        break
#    except locale.Error, e:
#        logging.debug('locale passet ikke på denne plattformen: %s', x)
#        continue
#
#logging.debug('setter locale : %s', locale.getdefaultlocale())
#locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())
#logging.debug('satte locale : %s', locale.getlocale())


class f60:
    "Lager en pdf etter malen til Giro F60-1, for utskrift eller elektronisk bruk"
    standardskrift = "Helvetica"
    standardstorrelse = 10
    kunde = {}
    firma = {'logo': None, }
    faktura = {}
    filnavn = ''
    datoformat = "%Y-%m-%d"

    def __init__(self, filnavn, overskriv=False):
        self.overskriv = overskriv
        if filnavn is None:  # lag tempfil
            self.filnavn = self.lagTempFilnavn()
        else:
            self.filnavn = self.sjekkFilnavn(filnavn)
        # lager en buffer for reportlab, siden den har problemer med utf8-stier
        self.buffer = open(self.filnavn, 'wb')
        self.canvas = canvas.Canvas(filename=self.buffer, pagesize=A4)

    def data(self):
        f = open(self.filnavn)
        d = f.read()
        f.close()
        return d

    # ============= MÅ FYLLES INN AV BRUKER =============== #

    def settFakturainfo(self, fakturanr, utstedtEpoch, forfallEpoch, fakturatekst, vilkaar='', kid=None,
                        levertEpoch=None):
        """Sett vital info om fakturaen. Bruk kid=True for å generere kid ut i fra kundenr og fakturanr."""
        self.faktura['nr'] = int(fakturanr)
        self.faktura['utstedt'] = time.strftime(self.datoformat, time.localtime(utstedtEpoch))
        if levertEpoch is None:
            levertEpoch = utstedtEpoch  # vi vet ikke leveringsdato
        self.faktura['levert'] = time.strftime(self.datoformat, time.localtime(levertEpoch))
        self.faktura['forfall'] = time.strftime(self.datoformat, time.localtime(forfallEpoch))
        self.faktura['tekst'] = self._s(fakturatekst)
        self.faktura['vilkaar'] = self._s(vilkaar)
        if kid:
            if isinstance(kid, bool): kid = self.lagKid()
            if not self.sjekkKid(kid): raise f60FeilKID(u'KID-nummeret er ikke riktig')
        self.faktura['kid'] = kid

    def settOrdrelinje(self, ordrelinje):
        """Sett fakturaens ordrelinjer. Kan være
        1. en list() hvor hver ordre er en
          sekvens: [tekst, kvantum, enhetspris, mva]

        2. en funksjon eller en metode som returnerer et objekt
          med følgende egenskaper: .tekst, .kvantum, .enhetspris, .mva
        """
        self.ordrelinje = ordrelinje

    def settLogo(self, logo):
        """Setter logoen som kommer oppe til venstre på fakturaen.
        Må være en str(), i et bildeformat som er lesbart av PIL."""
        if logo:
            self.firma['logo'] = logo
        else:
            raise f60Feil(u'Ugyldig logo: %s' % logo)

    def settFirmainfo(self, info):
        """info er en dictionary med følgende info:
            %(firmanavn)s
            %(kontaktperson)s
            %(adresse)s
            %(postnummer)04i %(poststed)s
            Telefon: %(telefon)s
            Bankkonto: %(kontonummer)011i
            Org.nr: %(organisasjonsnummer)s
            Epost: %(epost)s"""
        for k in info.keys():
            self.firma[k] = self._s(info[k])

    def settKundeinfo(self, kundenr, adresse):
        self.kunde['nr'] = int(kundenr)
        self.kunde['adresse'] = self._s(adresse)

    # ==================== OFFENTLIGE FUNKSJONER ================ #

    def settDatoformat(self, format):
        """Angir nytt format for alle datoer som skrives på fakturaen.
        Se http://www.python.org/doc/2.5.2/lib/module-time.html#l2h-2826
        for mulige verdier. Standardverdi er %Y-%m-%d."""
        logging.debug("Setter nytt datoformat: %s, f.eks. %s", format, time.strftime(format))
        self.datoformat = format

    def lagPost(self):
        "Ferdigstiller dokumentet for utskrift på papir (uten F60 skjemafelt)"
        self.fyll()
        return self._settSammen()

    def lagEpost(self):
        "Ferdigstiller dokumentet for elektronisk forsendelse (med F60 skjemafelt)"
        self.lagBakgrunn()
        self.fyll()
        return self._settSammen()

    def lagKvittering(self):
        "Ferdigstiller en kvittering for utskrift på papir (med F60 skjemafelt)"
        self.lagBakgrunn()
        self.fyll()
        self.lagKopimerke()
        return self._settSammen()

    def lagTempFilnavn(self):
        "Lager et temporært filnavn"
        from tempfile import mkstemp
        f, filnavn = mkstemp(".pdf", "faktura-")
        os.close(f)
        return filnavn

    def lagKid(self):
        "Lager kid av kundenummer og fakturanummer, med kontrollsiffer"
        if not self.kunde.has_key('nr'):
            raise f60Feil(u'Kundeinfo er ikke satt. Behøves for å lage KID (bruk .settKundeinfo())')
        tallrekke = "%06i%06i" % (self.kunde['nr'], self.faktura['nr'])
        return "%s%s" % (tallrekke, self.lagKontrollsifferMod10(tallrekke))

    def sjekkKid(self, kid):
        "Sjekk at kontrollsifferet i KID-en stemmer (alias for .sjekkKontrollsiffer())"
        return self.sjekkKontrollsiffer(kid)

    def sjekkKontrollsiffer(self, tallrekke):
        "Kontrollerer kontrollsifferet til en tallrekke etter mod10/luhn- og mod11-algoritmen. Returnerer True/False"
        logging.debug('Sjekker kontrollsiffer for tallrekka: %s' % tallrekke)
        _tallrekke = tallrekke[:-1]
        kontroll = tallrekke[-1]
        return self.lagKontrollsifferMod10(_tallrekke) == kontroll or \
               self.lagKontrollsifferMod11(_tallrekke) == kontroll

    def lagKontrollsifferMod10(self, tallrekke):
        "Lager mod10/luhn kontrollsiffer for en tallrekke. Returnerer en tekststreng"
        # http://no.wikipedia.org/wiki/KID
        # hvert andre siffer (bakfra) skal dobles og tverrsummene av alle produktene legges sammen
        # totalsummen skal så moduleres med 10, uten rest
        # sjekk eksempel i BBS' systemspek for OCR, side 14
        # (kopi på http://sourceforge.net/p/finfaktura/tickets/38/)
        # Takk til cbratli
        _sum = 0
        for i, j in enumerate(map(int, reversed(tallrekke))):
            if (i % 2) == 0:
                j *= 2
                if j > 9: j -= 9
            _sum += j
        r = 10 - (_sum % 10)
        if r == 10:
            return '0'
        else:
            return str(r)

    def lagKontrollsifferMod11(self, tallrekke):
        "Lager mod11 kontrollsiffer for en tallrekke. Returnerer en tekststreng"
        # sjekk eksempel i BBS' systemspek for OCR, side 14
        # (kopi på http://sourceforge.net/p/finfaktura/tickets/38/)
        # Takk til cbratli
        _sum = 0
        vekt = 0
        for i, j in enumerate(map(int, reversed(tallrekke))):
            _sum += j * (vekt + 2)
            vekt = (vekt + 1) % 5
        r = _sum % 11
        if r == 1:
            return '-'
        elif r == 0:
            return '0'
        else:
            return str(11 - r)

    def settBrukerbegrensning(self, passord='', utskrift=1, endringer=0, kopieringer=0, kommentarer=1):
        """Begrenser hva som kan gjøres med PDF-fakturaen. Krever versjon 2.3 eller høyere av reportlab.

        Uten argumenter lages det en PDF som kan skrives ut og kommenteres, men ikke endres eller kopieres fra.

        Du kan også sette et passord for åpning av dokumentet. Et tomt passord er det samme som ingen passord.
        """
        try:
            from reportlab.lib.pdfencrypt import StandardEncryption
        except ImportError:  # StandardEncryption kom i versjon 2.3 av reportlab
            logging.warn('Kunne ikke laste kryptering (reportlab-versjonen din er nok eldre enn 2.3).')
            return False
        e = StandardEncryption(userPassword=passord, canPrint=utskrift, canModify=endringer,
                               canCopy=kopieringer, canAnnotate=kommentarer, strength=128)
        return self.canvas.setEncrypt(e)

    # ==================== INTERNE FUNKSJONER ================ #

    def sjekkFilnavn(self, filnavn):
        (katalog, fil) = os.path.split(filnavn)
        if not os.path.exists(katalog):
            os.mkdir(katalog)
        filnavn = os.path.join(katalog, fil)
        if not self.overskriv and os.path.exists(filnavn):
            feil = f60Eksisterer("Stien finnes allerede")
            feil.filnavn = filnavn
            raise feil
        logging.debug('sjekkFilnavn: returnerer %s (%s)', repr(filnavn), type(filnavn))
        return filnavn

    def paragraf(self, t, par_bredde=80):
        """Bryter teksten med harde linjeskift på en gitt bredde, 80 tegn hvis ikke annet er oppgitt"""
        assert (isinstance(t, str))
        linjer = t.replace('\r\n', '\n').split('\n')
        ret = []
        for l in linjer:
            i = par_bredde
            while len(l) > par_bredde:
                if l[i] == " ":
                    ret += [l[:i], ]
                    l = l[i + 1:]
                else:
                    i -= 1
            ret += [l, ]
        return ret

    def kutt(self, t, lengde=200):
        """Kutter en tekst hvis den overstiger en gitt lengde"""
        if len(t) > lengde: t = "%s..." % t[:lengde - 3]
        return t

    def _s(self, t):
        """Sørger for at tekst er i riktig kodesett (encoding)"""
        return t

    def _kr(self, i):
        "Sørger for at et beløp skrives med riktig skilletegn og valuta. Returnerer tekst"
        #        try:
        #            if LOCALE:
        #                return locale.currency(i)
        #        except ValueError:
        #            pass
        return "kr %.02f" % i

    def lagKlammer(self, punktX, punktY, deltaX, deltaY, tekst=None):
        """En fullstendig giro har hjørneklammer rundt hvert tekstfelt.
           PunktX og punktY setter øverste venstre hjørne i "boksen".
           deltaX og deltaY angir relativ avstand til nederste høyre hjørne."""

        # Oppe i venstre  hjørne P(12,65)
        self.canvas.setLineWidth(0.2 * mm)
        self.canvas.lines([(punktX, punktY, punktX + 2 * mm, punktY), (punktX, punktY - 2 * mm, punktX, punktY)])
        # oppe i høyre hjørne P(98,65)
        self.canvas.lines([(punktX + deltaX - 2 * mm, punktY, punktX + deltaX, punktY),
                           (punktX + deltaX, punktY - 2 * mm, punktX + deltaX, punktY)])

        # Nede i venstre hjørne P(12,43)
        self.canvas.lines([(punktX, punktY + deltaY, punktX + 2 * mm, punktY + deltaY),
                           (punktX, punktY + deltaY, punktX, punktY + deltaY + 2 * mm)])
        # Nede i høyre hjørne P(98,43) # deltaX = 86, deltaY = -22
        self.canvas.lines([(punktX + deltaX - 2 * mm, punktY + deltaY, punktX + deltaX, punktY + deltaY),
                           (punktX + deltaX, punktY + deltaY, punktX + deltaX, punktY + deltaY + 2 * mm)])

        if isinstance(tekst, str):
            # skriv hjelpetekst til boksen
            self.canvas.setFont("Helvetica-Bold", 6)
            self.canvas.drawString(punktX + 3 * mm, punktY + 1 * mm, tekst)

    def lagBakgrunn(self):
        "Lager de gule skjemafeltene. Se .lagEpost() og .lagKvittering()"

        underkant = 5.0 / 6.0 * inch
        # a4 format spec:
        # http://www.cl.cam.ac.uk/~mgk25/iso-paper.html
        # 210 x 297
        # faktura spek:
        # Norsk Standard Skjema F60-1
        # url: http://sourceforge.net/p/finfaktura/tickets/38/
        self.canvas.saveState()
        self.canvas.setFillColor(yellow)
        # Lag de gule feltene
        self.canvas.rect(0 * mm, 101 * mm, 210 * mm, 21 * mm, stroke=0, fill=1)
        self.canvas.rect(0 * mm, 33 * mm, 210 * mm, 9 * mm, stroke=0, fill=1)
        self.canvas.rect(0 * mm, 14 * mm, 210 * mm, 2 * mm, stroke=0, fill=1)

        self.canvas.setFillColor(white)
        # Legg de hvite feltene oppå for "gjennomsiktighet"
        self.canvas.rect(80 * mm, 103 * mm, 36 * mm, 9 * mm, stroke=0, fill=1)  # beløp
        self.canvas.rect(126 * mm, 103 * mm, 40 * mm, 9 * mm, stroke=0, fill=1)  # betalerens kontonummer
        self.canvas.rect(170 * mm, 103 * mm, 31 * mm, 9 * mm, stroke=0, fill=1)  # blankettnummer
        self.canvas.restoreState()
        # skriv tekst på kvitteringen
        self.canvas.setFont("Helvetica-Bold", 14)
        self.canvas.drawString(15 * mm, 118 * mm, "KVITTERING")
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(15 * mm, 110 * mm, "Innbetalt til konto")
        # skillelinjer for KID
        self.canvas.lines([(9 * mm, 16 * mm, 9 * mm, 30 * mm), (80 * mm, 16 * mm, 80 * mm, 30 * mm)])
        # blankettnummer
        # TODO: tillate oppgitt blankettnummer
        self.canvas.setFont("Courier", 10)
        blankettnr = "xxxxxxx"
        self.canvas.drawString(173 * mm, 105 * mm, blankettnr)
        self.canvas.drawString(173 * mm, underkant, blankettnr)
        # Lag klammer for kontrollsiffer til sum.
        self.canvas.drawString(115 * mm, underkant, "<")
        self.canvas.drawString(125 * mm, underkant, ">")
        # Lag tekst som beskriver feltene.
        self.canvas.setFont("Helvetica-Bold", 6)
        self.canvas.drawString(10 * mm, 30 * mm, "Kundeidentifikasjon (KID)")
        self.canvas.drawString(82 * mm, 30 * mm, "Kroner")
        self.canvas.drawString(107 * mm, 30 * mm, "Øre")
        self.canvas.drawString(133 * mm, 30 * mm, "Til konto")
        self.canvas.drawString(172 * mm, 30 * mm, "Blankettnummer")
        self.canvas.drawString(150 * mm, 98 * mm, "Betalings-")
        self.canvas.drawString(150 * mm, 95 * mm, "frist")
        # Lag hjørneklammer rundt alle tekstfelt
        self.lagKlammer(12 * mm, 64 * mm, 86 * mm, -21 * mm, "Betalt av")
        self.lagKlammer(110 * mm, 64 * mm, 86 * mm, -21 * mm, "Betalt til")
        self.lagKlammer(110 * mm, 89 * mm, 86 * mm, -19 * mm, "Underskrift ved girering")
        self.lagKlammer(166 * mm, 99 * mm, 30 * mm, -6 * mm)  # Betalingsfrist.

    def lagKopimerke(self):
        """Lager teksten "Kvittering" på skrå over fakturaen"""
        self.canvas.saveState()  # lagrer gjeldende oppsett
        merke = self.canvas.beginText()
        self.canvas.rotate(45)
        merke.setFillGray(0.6)
        merke.setFont("Helvetica", 70)
        merke.setTextOrigin(90 * mm, 30 * mm)
        merke.textLines("KVITTERING\n\n\nKVITTERING")
        self.canvas.drawText(merke)
        self.canvas.restoreState()  # henter tilbake normalt oppsett

    def fyll(self):  # , firma, faktura):
        "Fyller fakturaen med data"

        # firma.sjekkData() # sjekker at ndvendig firmainfo er fylt ut

        # pdf-metadata
        self.canvas.setSubject("Faktura #%s til kunde #%s" % (self.faktura['nr'],
                                                              self.kunde['nr']))
        self.canvas.setTitle("Elektronisk faktura fra %s, utstedt den %s" % (self.firma['firmanavn'],
                                                                             self.faktura['utstedt']))

        logoForskyvning = 0
        if self.firma['logo']:
            logging.debug("Har logo!")
            try:
                import Image
            except ImportError:
                logging.warn('Kunne ikke importere PIL. Du kan få problemer hvis logoen ikke er i JPEG')
                logo = self.firma['logo']  # la reportlab ta seg av det, kanskje det går
                self.canvas.drawImage(logo, 10 * mm, 267 * mm, width=25 * mm, height=25 * mm)
            else:
                # PDFImage kan laste JPEG-data (i en str(), altså), et filnavn eller et PIL-objekt
                # De to siste tilfellene krever at PIL er installert
                logging.debug(len(self.firma['logo']))
                try:
                    # sjekk om det er et filnavn
                    # forutsetter at PATH_MAX=4096, sannsynligvis har ingen systemer har satt den større
                    enfil = len(self.firma['logo']) < 4096 and os.path.exists(self.firma['logo'])
                except:  # path.exists snubler på binær data
                    enfil = False
                if enfil:  # det er et filnavn, last det direkte
                    l = self.firma['logo']
                else:
                    l = StringIO.StringIO(self.firma['logo'])
                self._logo = Image.open(l)
                logo = PDFImage(self._logo, 10 * mm, 267 * mm, width=25 * mm, height=25 * mm)
                logo.drawInlineImage(self.canvas, preserveAspectRatio=True)
            logoForskyvning = 30

        # firmanavn: overskrift
        firmanavn = self.canvas.beginText()
        firmanavn.setTextOrigin((15 + logoForskyvning) * mm, 270 * mm)  # skyv til høyre dersom logo
        firmanavn.setFont("Helvetica-Bold", 16)
        firmanavn.textLine(self.firma['firmanavn'])
        self.canvas.drawText(firmanavn)

        # firmainfo: oppe til høyre i liten skrift
        firmainfo = self.canvas.beginText()
        firmainfo.setTextOrigin(160 * mm, 290 * mm)
        firmainfo.setFont("Helvetica", 8)
        firmainfo.setFillGray(0.3)
        # for z,y in self.firma.iteritems():
        # logging.debug("%s (%s): %s" % (z, type(y), y))
        print(type(self.firma['kontonummer']))
        firmainfo.textLines(("""%(kontaktperson)s
%(adresse)s
%(postnummer)04i %(poststed)s
Telefon: %(telefon)s
Bankkonto: %(kontonummer)011i
Org.nr: %(organisasjonsnummer)s
E-post: %(epost)s""" % self.firma).split('\n'))
        self.canvas.drawText(firmainfo)

        self.canvas.line(5 * mm, 265 * mm, 205 * mm, 265 * mm)
        self.canvas.setFont("Helvetica", 10)

        # informasjon om kunden
        kunde = self.canvas.beginText()
        kunde.setFillGray(0.0)
        kunde.setTextOrigin(20 * mm, 260 * mm)
        kunde.textLines(("Kunde# %03i\n%s" % (self.kunde['nr'], self.kunde['adresse'])).split('\n'))
        self.canvas.drawText(kunde)

        # detaljer om fakturaen # FIXME: løpe over flere sider
        sidenr = 1
        totalsider = 1
        fakturafakta = self.canvas.beginText()
        fakturafakta.setTextOrigin(150 * mm, 260 * mm)
        fakturafakta.textLines(("""FAKTURA
Fakturanr: %04i
Leveringsdato: %s
Fakturadato: %s
Forfallsdato: %s
Side: %i av %i
        """ % (self.faktura['nr'],
               self.faktura['levert'],
               self.faktura['utstedt'],
               self.faktura['forfall'],
               sidenr,  # FIXME: løpe over flere sider
               totalsider)).split('\n')
                               )
        self.canvas.drawText(fakturafakta)

        fakturatekst = self.canvas.beginText()
        fakturatekst.setTextOrigin(20 * mm, 230 * mm)
        fakturatekst.textLines(self.paragraf(self.faktura['tekst'], 100))
        fakturatekstNedreY = int(fakturatekst.getY() / mm)
        # logging.debug("fakturateksten strekker seg ned til Y: %i mm (%i PDF pt)" % (fakturatekstNedreY/mm, fakturatekstNedreY))
        # if fakturatekstNedreY > sikkerhetsgrense: tekst = self.kutt(faktura.tekst) ...
        self.canvas.drawText(fakturatekst)

        regnestykkeY = 215
        if fakturatekstNedreY < regnestykkeY: regnestykkeY = fakturatekstNedreY - 10
        self.canvas.drawString(20 * mm, regnestykkeY * mm, "Beskrivelse")
        self.canvas.drawRightString(140 * mm, regnestykkeY * mm, "Pris")
        self.canvas.drawRightString(160 * mm, regnestykkeY * mm, "Mva")
        self.canvas.drawRightString(180 * mm, regnestykkeY * mm, "SUM")
        self.canvas.setDash(1, 0)
        self.canvas.setLineWidth(0.2 * mm)
        self.canvas.line(15 * mm, (regnestykkeY - 2) * mm, 195 * mm, (regnestykkeY - 2) * mm)
        self.canvas.setFont("Helvetica", 8)

        tekstX = 20 * mm
        Y = (regnestykkeY - 10) * mm
        bruttoX = 140 * mm
        mvaX = 160 * mm
        prisX = 180 * mm

        totalBelop = 0
        totalMva = 0
        totalBrutto = 0

        mvagrunnlag = {}  # Holder en oppsummering av salg per mva-sats

        if type(self.ordrelinje) in (types.FunctionType, types.MethodType):
            for vare in self.ordrelinje():

                # regn ut alt som skal regnes
                brutto = vare.kvantum * vare.enhetspris
                mva = brutto * vare.mva / 100
                pris = brutto + mva
                totalBrutto += brutto
                totalMva += mva
                totalBelop += pris

                if not vare.mva in mvagrunnlag.keys():  # legg til i oppsummeringen av salg
                    mvagrunnlag[vare.mva] = []
                mvagrunnlag[vare.mva] += [brutto, ]

                self.canvas.drawString(tekstX, Y, self._s(vare.detaljertBeskrivelse()))
                self.canvas.drawRightString(bruttoX, Y, self._kr(brutto))
                self.canvas.drawRightString(mvaX, Y, self._kr(mva))
                self.canvas.drawRightString(prisX, Y, self._kr(pris))
                Y -= 3 * mm
        elif type(self.ordrelinje) is list:
            for vare in self.ordrelinje:
                # [tekst, kvantum, enhetspris, mva]

                # regn ut alt som skal regnes
                brutto = vare[1] * vare[2]
                mva = brutto * vare[3] / 100
                pris = brutto + mva
                totalBrutto += brutto
                totalMva += mva
                totalBelop += pris

                if not vare[3] in mvagrunnlag.keys():  # legg til i oppsummeringen av salg
                    mvagrunnlag[vare[3]] = []
                mvagrunnlag[vare[3]] += [brutto, ]

                self.canvas.drawString(tekstX, Y, "%s %s a kr %s" % (vare[1], vare[0], vare[2]))
                self.canvas.drawRightString(bruttoX, Y, self._kr(brutto))
                self.canvas.drawRightString(mvaX, Y, self._kr(mva))
                self.canvas.drawRightString(prisX, Y, self._kr(pris))
                Y -= 3 * mm

        # logging.debug("Nå har vi kommet til Y: %i (%i)" % (Y/mm, Y))
        # if Y < 140*mm: self.lagNySide() # vi har lagt inn for mange varer til at vi får plass på en side
        # FIXME: løpe over flere sider

        sumY = 141 * mm
        self.canvas.line(90 * mm, sumY, 190 * mm, sumY)

        # sum mvagrunnlag
        logging.debug("mvagrunnlag: %s", mvagrunnlag)
        mvaY = 150 * mm
        mvaX = 5 * mm
        self.canvas.drawString(mvaX, mvaY + 4 * mm, "MVA-grunnlag:")
        self.canvas.setFont("Helvetica", 7)
        for i, _mva in enumerate(mvagrunnlag.keys()):
            linjesum = sum(map(float, mvagrunnlag[_mva]))
            self.canvas.drawString(mvaX, mvaY - (i * 3 * mm), "%.1f%% av %s = %s" % (_mva,
                                                                                     self._kr(linjesum),
                                                                                     self._kr(linjesum * _mva / 100)))

        # legg sammen totalen
        self.canvas.setFont("Helvetica", 8)
        self.canvas.drawRightString(prisX - 70 * mm, sumY - 7 * mm, "Netto: %s" % self._kr(totalBrutto))
        self.canvas.drawRightString(prisX - 40 * mm, sumY - 7 * mm, "MVA: %s" % self._kr(totalMva))
        self.canvas.setFont("Helvetica-Bold", 10)
        self.canvas.drawRightString(prisX, sumY - 7 * mm, "TOTALT: %s" % self._kr(totalBelop))

        # standard betalingsvilkår
        if len(self.faktura['vilkaar']):  ## FIXME: krype oppover hvis teksten er mer enn en linje høy
            self.canvas.setFont("Helvetica", 10)
            vilkar = self.canvas.beginText()
            vilkar.setTextOrigin(9 * mm, 124 * mm)
            vilkar.textLines(self.paragraf(self.faktura['vilkaar'], 120))
            self.canvas.drawText(vilkar)

        # Nederste del av skjemaet
        # den gule betalingsslippen
        # skal skrives i courier 10 (se issue#38)
        self.canvas.setFont("Courier", 10)
        self.canvas.drawString(20 * mm, 105 * mm, "%011i" % self.firma['kontonummer'])

        self.canvas.drawString(88 * mm, 105 * mm, self._kr(totalBelop))

        # betalingsfrist
        self.canvas.drawString(170 * mm, 95 * mm, self.faktura['forfall'])

        # fakturainformasjon
        t = self.canvas.beginText()
        t.setTextOrigin(15 * mm, 90 * mm)
        t.textLines("Fakturanr: %05i\nKundenr: %04i\nFakturadato: %s" % \
                    (self.faktura['nr'], self.kunde['nr'], self.faktura['utstedt']))
        self.canvas.drawText(t)

        adresseboksY = 58 * mm  # øverste punkt i adressefelter
        # mottakerfelt
        kundeinfo = self.canvas.beginText()
        ki = self.kunde['adresse'].split('\n')
        kiY = adresseboksY + (3 * mm * int(len(ki) > 4))
        kundeinfo.setTextOrigin(15 * mm, kiY)
        kundeinfo.textLines(ki)
        self.canvas.drawText(kundeinfo)

        # avsenderfelt
        firmaadresse = self.canvas.beginText()
        fa = ("%(firmanavn)s\n%(kontaktperson)s\n%(adresse)s\n%(postnummer)04i %(poststed)s" % (self.firma)).split('\n')
        faY = adresseboksY + (3 * mm * int(len(fa) > 4))
        firmaadresse.setTextOrigin(115 * mm, faY)
        firmaadresse.textLines(fa)
        self.canvas.drawText(firmaadresse)

        # Blankettens underkant
        # (se http://sourceforge.net/p/finfaktura/tickets/38/, punkt A)
        underkant = 5.0 / 6.0 * inch

        # Den fortrykte H -- innstillingsmerke
        # (se http://sourceforge.net/p/finfaktura/tickets/38/)
        self.canvas.drawString(2 * mm, underkant, 'H')

        # KID
        if self.faktura['kid'] and self.sjekkKid(self.faktura['kid']):
            self.canvas.drawRightString(72 * mm, underkant, str(self.faktura['kid']))
        else:
            logging.warn('Ugyldig kid, hopper over: %s', self.faktura['kid'])

        # SUM
        kr = int(totalBelop)
        ore = int((totalBelop - kr) * 100)
        self.canvas.drawString(90 * mm, underkant, str(kr))
        self.canvas.drawString(108 * mm, underkant, "%02d" % ore)
        self.canvas.drawString(135 * mm, underkant, "%011i" % self.firma['kontonummer'])

        # KONTROLLSIFFER FOR SUM
        # BBS' brukerhåndbok sier at kontrollsiffer skal utregnes for 'beløp'
        # tolker 'beløp' som kr+ore.. er dette korrekt?
        # Håndboka sier også at mod10 skal brukes, testing viser at mange
        # fakturaer som er i omløp bruker mod11
        siffer = self.lagKontrollsifferMod10("%d%02d" % (kr, ore))
        self.canvas.drawString(120 * mm, underkant, siffer)

    def _settSammen(self):
        "Setter sammen fakturaen. Ikke for eksternt bruk. Bruk .lag*()-metodene"
        self.canvas.showPage()
        self.canvas.save()
        self.buffer.close()
        return True
