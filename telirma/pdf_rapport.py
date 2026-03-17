import io
import os
from django.http import FileResponse
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas as pdfcanvas

# ── Palette couleurs TELIRMA ───────────────────────────────────────────────
NAVY       = colors.HexColor('#0D2B5E')
ROYAL      = colors.HexColor('#1558B0')
STEEL      = colors.HexColor('#2575D0')
SKY        = colors.HexColor('#4A9FE8')
ICE        = colors.HexColor('#E8F2FC')
WHITE      = colors.white
BLACK      = colors.black
LIGHT_GREY = colors.HexColor('#F5F7FA')
MID_GREY   = colors.HexColor('#DEE4EE')
MUTED      = colors.HexColor('#5A7399')

# Couleurs statut
C_CONFORME = colors.HexColor('#27ae60')
C_HORS     = colors.HexColor('#e74c3c')
C_VIDE     = colors.HexColor('#f39c12')
C_PERIME   = colors.HexColor('#8e44ad')

BG_CONFORME = colors.HexColor('#d4efdf')
BG_HORS     = colors.HexColor('#fadbd8')
BG_VIDE     = colors.HexColor('#fef9e7')
BG_PERIME   = colors.HexColor('#e8daef')


def statut_colors(statut):
    """Retourne (couleur_texte, couleur_fond) selon le statut."""
    s = statut.lower()
    if 'conforme' in s:
        return C_CONFORME, BG_CONFORME
    elif 'hors' in s:
        return C_HORS, BG_HORS
    elif 'vide' in s:
        return C_VIDE, BG_VIDE
    else:
        return C_PERIME, BG_PERIME


# ── Canvas avec en-tête et pied de page sur chaque page ───────────────────
class TelirmaCanvas(pdfcanvas.Canvas):
    """Canvas personnalisé : ajoute en-tête + pied de page sur chaque page."""

    def __init__(self, *args, rapport=None, logo_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.rapport    = rapport
        self.logo_path  = logo_path

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_header_footer(total)
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def _draw_header_footer(self, total_pages):
        w, h = A4
        page = self._pageNumber

        # ── EN-TÊTE ────────────────────────────────────────────────────────
        # Bande bleue navy
        self.setFillColor(NAVY)
        self.rect(0, h - 28*mm, w, 28*mm, fill=1, stroke=0)

        # Logo (si disponible)
        logo_x = 12*mm
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                self.drawImage(self.logo_path, logo_x, h - 24*mm,
                               width=18*mm, height=18*mm,
                               preserveAspectRatio=True, mask='auto')
                logo_x = 34*mm
            except Exception:
                pass

        # Nom société
        self.setFillColor(WHITE)
        self.setFont('Helvetica-Bold', 16)
        self.drawString(logo_x, h - 11*mm, 'TELIRMA')

        self.setFont('Helvetica', 8)
        self.setFillColor(SKY)
        self.drawString(logo_x, h - 17*mm,
                        'TELECOM & INDUSTRIAL RISK MANAGEMENT')

        # Ligne verticale séparatrice
        self.setStrokeColor(STEEL)
        self.setLineWidth(0.8)
        self.line(logo_x + 55*mm, h - 24*mm, logo_x + 55*mm, h - 8*mm)

        # Infos rapport à droite de la ligne
        if self.rapport:
            self.setFillColor(WHITE)
            self.setFont('Helvetica-Bold', 9)
            self.drawString(logo_x + 58*mm, h - 12*mm,
                            f'Rapport N° {self.rapport.rapport_number}')
            self.setFont('Helvetica', 8)
            self.setFillColor(ICE)
            self.drawString(logo_x + 58*mm, h - 17*mm,
                            f'Client : {self.rapport.client.name if self.rapport.client else "—"}')

        # Numéro de page (coin droit)
        self.setFillColor(SKY)
        self.setFont('Helvetica', 8)
        self.drawRightString(w - 12*mm, h - 12*mm,
                             f'Page {page} / {total_pages}')

        # ── PIED DE PAGE ────────────────────────────────────────────────────
        # Ligne bleue
        self.setStrokeColor(STEEL)
        self.setLineWidth(1.5)
        self.line(10*mm, 16*mm, w - 10*mm, 16*mm)

        self.setFillColor(NAVY)
        self.setFont('Helvetica-Bold', 8)
        self.drawCentredString(
            w / 2, 11*mm,
            'Tél. : +237 6 75 87 43 29  /  +237 696 19 99 97  |  WhatsApp : +237 6 75 87 43 29'
        )
        self.setFont('Helvetica', 7.5)
        self.setFillColor(MUTED)
        self.drawCentredString(
            w / 2, 7*mm,
            'www.telirma.com  |  telirma@telirma.com  /  info@telirma.com'
        )
        self.drawCentredString(
            w / 2, 3.5*mm,
            'Bafoussam, Cameroun'
        )


# ── Styles ─────────────────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()
    s = {}

    s['titre_doc'] = ParagraphStyle('titre_doc',
        fontSize=15, fontName='Helvetica-Bold',
        textColor=NAVY, alignment=TA_LEFT,
        spaceAfter=4, leading=20)

    s['section'] = ParagraphStyle('section',
        fontSize=11, fontName='Helvetica-Bold',
        textColor=WHITE, alignment=TA_LEFT,
        spaceAfter=0, leading=15)

    s['h3'] = ParagraphStyle('h3',
        fontSize=10, fontName='Helvetica-Bold',
        textColor=NAVY, spaceAfter=4, leading=14)

    s['body'] = ParagraphStyle('body',
        fontSize=9, fontName='Helvetica',
        textColor=BLACK, leading=13,
        alignment=TA_JUSTIFY, spaceAfter=3)

    s['body_bold'] = ParagraphStyle('body_bold',
        fontSize=9, fontName='Helvetica-Bold',
        textColor=NAVY, leading=13, spaceAfter=2)

    s['label'] = ParagraphStyle('label',
        fontSize=7.5, fontName='Helvetica-Bold',
        textColor=MUTED, leading=10, spaceAfter=1,
        spaceBefore=2)

    s['cell'] = ParagraphStyle('cell',
        fontSize=8.5, fontName='Helvetica',
        textColor=BLACK, leading=12)

    s['cell_bold'] = ParagraphStyle('cell_bold',
        fontSize=8.5, fontName='Helvetica-Bold',
        textColor=NAVY, leading=12)

    s['statut'] = ParagraphStyle('statut',
        fontSize=8, fontName='Helvetica-Bold',
        alignment=TA_CENTER, leading=11)

    s['reco'] = ParagraphStyle('reco',
        fontSize=9, fontName='Helvetica',
        textColor=BLACK, leading=13, leftIndent=10,
        spaceAfter=3)

    s['small'] = ParagraphStyle('small',
        fontSize=8, fontName='Helvetica',
        textColor=MUTED, leading=11)

    s['sign_name'] = ParagraphStyle('sign_name',
        fontSize=9, fontName='Helvetica-Bold',
        textColor=NAVY, alignment=TA_CENTER, leading=12)

    s['sign_label'] = ParagraphStyle('sign_label',
        fontSize=8, fontName='Helvetica',
        textColor=MUTED, alignment=TA_CENTER, leading=11)

    return s


# ── Helper : bandeau de section ────────────────────────────────────────────
def section_header(title, styles, color=NAVY):
    tbl = Table([[Paragraph(title, styles['section'])]], colWidths=['100%'])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), color),
        ('TOPPADDING',    (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
    ]))
    return tbl


# ── Fonction principale ────────────────────────────────────────────────────
def generer_rapport_pdf(request, rapport_number):
    """
    Génère un PDF professionnel du rapport d'inspection TELIRMA.
    Structure :
        Page 1 — En-tête + Informations rapport + Résumé statuts
        Page 2+ — Tableau des items inspectés
        Dernière section — Recommandations + Signatures
    """
    from .models import Rapport as RapportModel, RapportItem

    # ── Récupération des données ──────────────────────────────────────────
    rapport = RapportModel.objects.get(rapport_number=rapport_number)
    items   = RapportItem.objects.filter(rapport=rapport).order_by('id')
    client  = rapport.client

    # Statistiques statuts
    total     = items.count()
    conformes = sum(1 for i in items if 'conforme' in i.statut_appareil.lower())
    hors_svc  = sum(1 for i in items if 'hors' in i.statut_appareil.lower())
    vides     = sum(1 for i in items if 'vide' in i.statut_appareil.lower())
    autres    = total - conformes - hors_svc - vides

    # Chemin logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo_telirma2.jpg')

    # ── Préparation du buffer ─────────────────────────────────────────────
    buffer = io.BytesIO()
    w, h   = A4
    MARGIN = 15*mm
    USABLE = w - 2 * MARGIN

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=35*mm,    # espace pour l'en-tête
        bottomMargin=22*mm, # espace pour le pied de page
        title=f'Rapport {rapport_number}',
        author='TELIRMA',
    )

    styles = build_styles()
    story  = []

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 1 — TITRE ET INFORMATIONS GÉNÉRALES
    # ════════════════════════════════════════════════════════════════════════
    story.append(section_header('1.  INFORMATIONS GÉNÉRALES DU RAPPORT', styles))
    story.append(Spacer(1, 4*mm))

    # Titre du rapport
    story.append(Paragraph(rapport.titre, styles['titre_doc']))
    story.append(HRFlowable(width=USABLE, thickness=2,
                            color=STEEL, spaceAfter=6))

    # Grille informations (2 colonnes)
    col_w = USABLE / 2 - 5*mm

    def info_row(label, value):
        return [
            Paragraph(label, styles['label']),
            Paragraph(str(value) if value else '—', styles['body_bold']),
        ]

    info_data = [
        info_row('N° RAPPORT',          rapport.rapport_number),
        info_row('DATE DE CRÉATION',    str(rapport.create_at)),
        info_row('DATE DE VÉRIFICATION', str(rapport.date_verification)),
        info_row('RÉALISÉ PAR',
                 rapport.verification_realiser_par.get_full_name()
                 if rapport.verification_realiser_par else '—'),
    ]
    client_data = [
        info_row('CLIENT',     client.name if client else '—'),
        info_row('ADRESSE',    client.address if client else '—'),
        info_row('EMAIL',      client.email if client else '—'),
        info_row('TÉLÉPHONE',  client.phone_number if client else '—'),
    ]

    # Tableau côte à côte : infos rapport | infos client
    combined = []
    for i in range(max(len(info_data), len(client_data))):
        left  = info_data[i]  if i < len(info_data)  else ['', '']
        right = client_data[i] if i < len(client_data) else ['', '']
        combined.append(left + [''] + right)

    info_tbl = Table(combined,
                     colWidths=[38*mm, col_w - 38*mm, 4*mm, 38*mm, col_w - 38*mm])
    info_tbl.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 0), (1, -1), [WHITE, LIGHT_GREY]),
        ('ROWBACKGROUNDS', (3, 0), (4, -1), [WHITE, LIGHT_GREY]),
        ('BOX',   (0, 0), (1, -1), 0.5, MID_GREY),
        ('BOX',   (3, 0), (4, -1), 0.5, MID_GREY),
        ('INNERGRID', (0, 0), (1, -1), 0.3, MID_GREY),
        ('INNERGRID', (3, 0), (4, -1), 0.3, MID_GREY),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 6*mm))

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 2 — RÉSUMÉ DES STATUTS (barre de stats)
    # ════════════════════════════════════════════════════════════════════════
    story.append(section_header('2.  RÉSUMÉ DE L\'INSPECTION', styles))
    story.append(Spacer(1, 4*mm))

    stats_data = [
        ['TOTAL', 'CONFORMES', 'HORS SERVICE', 'VIDES', 'AUTRES'],
        [
            Paragraph(f'<b>{total}</b>',     ParagraphStyle('s', fontSize=22, fontName='Helvetica-Bold', textColor=NAVY,    alignment=TA_CENTER, leading=26)),
            Paragraph(f'<b>{conformes}</b>', ParagraphStyle('s', fontSize=22, fontName='Helvetica-Bold', textColor=C_CONFORME, alignment=TA_CENTER, leading=26)),
            Paragraph(f'<b>{hors_svc}</b>',  ParagraphStyle('s', fontSize=22, fontName='Helvetica-Bold', textColor=C_HORS,  alignment=TA_CENTER, leading=26)),
            Paragraph(f'<b>{vides}</b>',     ParagraphStyle('s', fontSize=22, fontName='Helvetica-Bold', textColor=C_VIDE,  alignment=TA_CENTER, leading=26)),
            Paragraph(f'<b>{autres}</b>',    ParagraphStyle('s', fontSize=22, fontName='Helvetica-Bold', textColor=C_PERIME, alignment=TA_CENTER, leading=26)),
        ],
    ]
    stats_tbl = Table(stats_data, colWidths=[USABLE / 5] * 5)
    stats_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR',     (0, 0), (-1, 0), WHITE),
        ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0), 8),
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',    (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING',    (0, 1), (-1, 1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 8),
        ('BACKGROUND',    (0, 1), (-1, 1), WHITE),
        ('BOX',           (0, 0), (-1, -1), 0.5, MID_GREY),
        ('INNERGRID',     (0, 0), (-1, -1), 0.3, MID_GREY),
        # couleur de fond sous chaque chiffre
        ('BACKGROUND',    (1, 1), (1, 1), BG_CONFORME),
        ('BACKGROUND',    (2, 1), (2, 1), BG_HORS),
        ('BACKGROUND',    (3, 1), (3, 1), BG_VIDE),
        ('BACKGROUND',    (4, 1), (4, 1), BG_PERIME),
    ]))
    story.append(stats_tbl)
    story.append(Spacer(1, 6*mm))

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 3 — TABLEAU DES ITEMS
    # ════════════════════════════════════════════════════════════════════════
    story.append(section_header('3.  DÉTAIL DES ÉQUIPEMENTS INSPECTÉS', styles))
    story.append(Spacer(1, 3*mm))

    if items.exists():
        # En-têtes du tableau
        headers = ['#', 'Emplacement', 'Type d\'appareil', 'Statut', 'Observation']
        col_widths = [10*mm, 42*mm, 38*mm, 32*mm, USABLE - 10*mm - 42*mm - 38*mm - 32*mm]

        table_data = [headers]
        table_styles = [
            # En-tête
            ('BACKGROUND',    (0, 0), (-1, 0), ROYAL),
            ('TEXTCOLOR',     (0, 0), (-1, 0), WHITE),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, 0), 8),
            ('ALIGN',         (0, 0), (-1, 0), 'CENTER'),
            ('TOPPADDING',    (0, 0), (-1, 0), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 7),
            # Corps
            ('FONTSIZE',      (0, 1), (-1, -1), 8.5),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN',         (0, 1), (0, -1), 'CENTER'),
            ('ALIGN',         (3, 1), (3, -1), 'CENTER'),
            ('TOPPADDING',    (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('LEFTPADDING',   (0, 0), (-1, -1), 5),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 5),
            ('INNERGRID',     (0, 0), (-1, -1), 0.3, MID_GREY),
            ('BOX',           (0, 0), (-1, -1), 0.5, MID_GREY),
        ]

        for idx, item in enumerate(items, start=1):
            row_num = idx + 1  # +1 pour l'en-tête
            txt_col, bg_col = statut_colors(item.statut_appareil)

            # Icône statut
            icone = '✅' if 'conforme' in item.statut_appareil.lower() \
               else '❌' if 'hors'     in item.statut_appareil.lower() \
               else '⚠️' if 'vide'    in item.statut_appareil.lower() \
               else '🔴'

            statut_para = Paragraph(
                f'{icone} {item.statut_appareil}',
                ParagraphStyle('st', fontSize=8, fontName='Helvetica-Bold',
                               textColor=txt_col, alignment=TA_CENTER, leading=12)
            )

            table_data.append([
                Paragraph(str(idx), styles['cell']),
                Paragraph(item.emplacement, styles['cell']),
                Paragraph(item.type_appareil, styles['cell_bold']),
                statut_para,
                Paragraph(item.observation or '—', styles['cell']),
            ])

            # Fond alternant + fond coloré si hors service ou vide
            if 'conforme' not in item.statut_appareil.lower():
                table_styles.append(('BACKGROUND', (3, row_num), (3, row_num), bg_col))
            else:
                bg = LIGHT_GREY if idx % 2 == 0 else WHITE
                table_styles.append(('BACKGROUND', (0, row_num), (-1, row_num), bg))

        items_tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
        items_tbl.setStyle(TableStyle(table_styles))
        story.append(items_tbl)
    else:
        story.append(Paragraph('Aucun item enregistré pour ce rapport.', styles['body']))

    story.append(Spacer(1, 8*mm))

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 4 — RECOMMANDATIONS
    # ════════════════════════════════════════════════════════════════════════
    story.append(KeepTogether([
        section_header('4.  RECOMMANDATIONS ET ACTIONS À MENER', styles, color=STEEL),
        Spacer(1, 4*mm),
    ]))

    # Générer les recommandations automatiquement selon les statuts
    recos = []

    if hors_svc > 0:
        recos.append((
            '❌ Équipements hors service',
            f'{hors_svc} appareil(s) sont hors service. '
            'Procéder au remplacement ou à la réparation immédiate '
            'conformément aux normes de sécurité incendie en vigueur.',
            C_HORS, BG_HORS
        ))

    if vides > 0:
        recos.append((
            '⚠️ Équipements vides',
            f'{vides} appareil(s) sont vides. '
            'Recharger les extincteurs concernés dans les meilleurs délais '
            'et vérifier l\'absence de fuites.',
            C_VIDE, BG_VIDE
        ))

    if autres > 0:
        recos.append((
            '🔴 Équipements périmés / autres anomalies',
            f'{autres} appareil(s) présentent d\'autres anomalies (périmés, '
            'endommagés...). Faire appel à un technicien agréé pour inspection '
            'et remise en conformité.',
            C_PERIME, BG_PERIME
        ))

    if conformes == total and total > 0:
        recos.append((
            '✅ Tous les équipements sont conformes',
            'L\'ensemble des équipements inspectés est en bon état de '
            'fonctionnement. Prévoir la prochaine visite de contrôle '
            'selon le calendrier de maintenance préventive.',
            C_CONFORME, BG_CONFORME
        ))

    # Recommandation générale toujours présente
    recos.append((
        '📋 Recommandation générale',
        'Sensibiliser régulièrement le personnel à l\'utilisation des '
        'équipements de sécurité incendie et afficher les consignes '
        'd\'évacuation dans les zones accessibles. '
        'Planifier la prochaine inspection dans 6 à 12 mois.',
        ROYAL, ICE
    ))

    for titre_reco, texte_reco, txt_color, bg_color in recos:
        reco_bloc = Table([
            [Paragraph(titre_reco,
                       ParagraphStyle('rt', fontSize=9, fontName='Helvetica-Bold',
                                      textColor=txt_color, leading=13))],
            [Paragraph(texte_reco, styles['reco'])],
        ], colWidths=[USABLE])
        reco_bloc.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), bg_color),
            ('BACKGROUND',    (0, 1), (-1, 1), WHITE),
            ('TOPPADDING',    (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING',   (0, 0), (-1, -1), 10),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
            ('BOX',           (0, 0), (-1, -1), 0.8, txt_color),
        ]))
        story.append(reco_bloc)
        story.append(Spacer(1, 3*mm))

    story.append(Spacer(1, 8*mm))

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 5 — SIGNATURES
    # ════════════════════════════════════════════════════════════════════════
    story.append(KeepTogether([
        section_header('5.  CERTIFICATION ET SIGNATURES', styles),
        Spacer(1, 4*mm),
        Paragraph(
            'Je soussigné certifie que les informations contenues dans ce rapport '
            'sont exactes et reflètent fidèlement l\'état des équipements constatés '
            'lors de la visite d\'inspection.',
            styles['body']
        ),
        Spacer(1, 8*mm),
    ]))

    # Date et lieu
    from datetime import date
    story.append(Paragraph(
        f'Fait à Bafoussam, le {date.today().strftime("%d/%m/%Y")}',
        ParagraphStyle('lieu', fontSize=9, fontName='Helvetica',
                       textColor=MUTED, alignment=TA_RIGHT, leading=13)
    ))
    story.append(Spacer(1, 10*mm))

    inspecteur_name = (rapport.verification_realiser_par.get_full_name()
                       or rapport.verification_realiser_par.username
                       if rapport.verification_realiser_par else 'Inspecteur TELIRMA')
    client_name = client.name if client else 'Représentant client'

    sig_data = [[
        # Signature inspecteur
        [
            Paragraph('L\'Inspecteur TELIRMA', styles['sign_label']),
            Spacer(1, 20*mm),   # espace pour signer
            HRFlowable(width=60*mm, thickness=1, color=NAVY),
            Spacer(1, 2*mm),
            Paragraph(inspecteur_name, styles['sign_name']),
            Paragraph('Technicien certifié TELIRMA', styles['sign_label']),
        ],
        '',   # colonne espace
        # Signature client
        [
            Paragraph('Le Représentant Client', styles['sign_label']),
            Spacer(1, 20*mm),
            HRFlowable(width=60*mm, thickness=1, color=NAVY),
            Spacer(1, 2*mm),
            Paragraph(client_name, styles['sign_name']),
            Paragraph('Cachet et signature', styles['sign_label']),
        ],
    ]]

    sig_tbl = Table(sig_data, colWidths=[USABLE * 0.45, USABLE * 0.1, USABLE * 0.45])
    sig_tbl.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BOX',           (0, 0), (0, 0), 0.5, MID_GREY),
        ('BOX',           (2, 0), (2, 0), 0.5, MID_GREY),
        ('BACKGROUND',    (0, 0), (0, 0), LIGHT_GREY),
        ('BACKGROUND',    (2, 0), (2, 0), LIGHT_GREY),
    ]))
    story.append(sig_tbl)

    # ── Génération ────────────────────────────────────────────────────────
    def make_canvas(*args, **kwargs):
        return TelirmaCanvas(*args, rapport=rapport, logo_path=logo_path, **kwargs)

    doc.build(story, canvasmaker=make_canvas)

    buffer.seek(0)
    filename = f'TELIRMA_{rapport_number}_{client.name if client else "rapport"}.pdf'
    return FileResponse(buffer, as_attachment=True, filename=filename)
