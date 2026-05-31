#!/usr/bin/env python3
"""Generate the Challenge NextDev presentation PPTX."""

import zipfile
import os
import shutil
from xml.sax.saxutils import escape

OUTPUT = "/home/akaletekoffilevis/Bureau/Challenge/presentation.pptx"

TEMPLATE_SLIDE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld name="">
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      {content}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr>
    <a:masterClrMapping/>
  </p:clrMapOvr>
</p:sld>"""

def rect_shape(shape_id, name, left, top, width, height, fill_color=None, border_color=None):
    """Generate XML for a rectangle shape."""
    xml = f"""
    <p:sp>
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="{escape(name)}"/>
        <p:cNvSpPr txBox="1"/>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm>
          <a:off x="{left}" y="{top}"/>
          <a:ext cx="{width}" cy="{height}"/>
        </a:xfrm>
        <a:prstGeom prst="rect">
          <a:avLst/>
        </a:prstGeom>"""
    if fill_color:
        xml += f"""
        <a:solidFill>
          <a:srgbClr val="{fill_color}"/>
        </a:solidFill>"""
    if border_color:
        xml += f"""
        <a:ln w="12700">
          <a:solidFill>
            <a:srgbClr val="{border_color}"/>
          </a:solidFill>
        </a:ln>"""
    else:
        xml += '<a:ln w="0"/>'
    xml += """
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" rtlCol="0"/>
        <a:lstStyle/>
        <a:p>
          <a:endParaRPr lang="fr-FR" sz="1400"/>
        </a:p>
      </p:txBody>
    </p:sp>"""
    return xml

def text_shape(shape_id, name, left, top, width, height, text, font_size="1800", bold=False, color="FFFFFF", align="l", font="Calibri"):
    """Generate XML for a text box."""
    bold_attr = ' 1' if bold else '0'
    align_map = {"l": "l", "c": "ctr", "r": "r"}
    return f"""
    <p:sp>
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="{escape(name)}"/>
        <p:cNvSpPr txBox="1"/>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm>
          <a:off x="{left}" y="{top}"/>
          <a:ext cx="{width}" cy="{height}"/>
        </a:xfrm>
        <a:prstGeom prst="rect">
          <a:avLst/>
        </a:prstGeom>
        <a:noFill/>
        <a:ln w="0"/>
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" rtlCol="0"/>
        <a:lstStyle/>
        <a:p>
          <a:pPr algn="{align_map[align]}"/>
          <a:r>
            <a:rPr lang="fr-FR" sz="{font_size}" b="{bold_attr}" dirty="0" spc="-50">
              <a:solidFill>
                <a:srgbClr val="{color}"/>
              </a:solidFill>
              <a:latin typeface="{font}"/>
            </a:rPr>
            <a:t>{escape(text)}</a:t>
          </a:r>
        </a:p>
      </p:txBody>
    </p:sp>"""

def bullet_shape(shape_id, name, left, top, width, height, items, font_size="1600", color="FFFFFF"):
    """Generate XML for a bulleted text box."""
    parts = []
    parts.append(f"""
    <p:sp>
      <p:nvSpPr>
        <p:cNvPr id="{shape_id}" name="{escape(name)}"/>
        <p:cNvSpPr txBox="1"/>
        <p:nvPr/>
      </p:nvSpPr>
      <p:spPr>
        <a:xfrm>
          <a:off x="{left}" y="{top}"/>
          <a:ext cx="{width}" cy="{height}"/>
        </a:xfrm>
        <a:prstGeom prst="rect">
          <a:avLst/>
        </a:prstGeom>
        <a:noFill/>
        <a:ln w="0"/>
      </p:spPr>
      <p:txBody>
        <a:bodyPr wrap="square" rtlCol="0"/>
        <a:lstStyle/>""")

    for i, item in enumerate(items):
        is_first = (i == 0)
        parts.append("""
        <a:p>
          <a:pPr marL="457200" indent="-457200"">")
            <a:buChar char="●" />""")
        parts.append("""
          </a:pPr>
          <a:r>
            <a:rPr lang="fr-FR" sz="{font_size}" dirty="0">
              <a:solidFill>
                <a:srgbClr val="{color}"/>
              </a:solidFill>
              <a:latin typeface="Calibri"/>
            </a:rPr>
            <a:t>{text}</a:t>
          </a:r>
        </a:p>""".format(font_size=font_size, color=color, text=escape(item)))

    parts.append("""
      </p:txBody>
    </p:sp>""")
    return "\n".join(parts)

def title_slide_content(title, subtitle):
    """Generate a title slide."""
    sid = 2
    parts = []
    # Background
    parts.append(rect_shape(sid, "Bg", 0, 0, 12192000, 6858000, fill_color="1B3A5C"))
    sid += 1
    # Accent bar
    parts.append(rect_shape(sid, "Accent", 0, 0, 12192000, 914400, fill_color="00A4EF"))
    sid += 1
    # Title
    parts.append(text_shape(sid, "Title", 914400, 1828800, 10400000, 1200000, title,
                            font_size="4400", bold=True, color="FFFFFF", align="c"))
    sid += 1
    # Subtitle
    parts.append(text_shape(sid, "Subtitle", 914400, 3200000, 10400000, 800000, subtitle,
                            font_size="2200", bold=False, color="A0C4E8", align="c"))
    sid += 1
    # Bottom bar
    parts.append(rect_shape(sid, "Bar", 0, 5943600, 12192000, 914400, fill_color="0D2B4A"))
    sid += 1
    return "\n".join(parts)

def section_slide(title, items, accent_color="00A4EF"):
    """Generate a content slide with title and bullet points."""
    sid = 10
    parts = []
    # Background
    parts.append(rect_shape(sid, "Bg", 0, 0, 12192000, 6858000, fill_color="1B3A5C"))
    sid += 1
    # Top bar
    parts.append(rect_shape(sid, "TopBar", 0, 0, 12192000, 914400, fill_color=accent_color))
    sid += 1
    # Title
    parts.append(text_shape(sid, "Title", 457200, 200000, 11200000, 700000, title,
                            font_size="2800", bold=True, color="FFFFFF", align="l"))
    sid += 1
    # Divider line
    parts.append(rect_shape(sid, "Line", 457200, 850000, 3000000, 36000, fill_color=accent_color))
    sid += 1
    # Bullets
    y = 1050000
    for item in items:
        parts.append(text_shape(sid, f"Item", 685800, y, 10800000, 450000, f"● {item}",
                                font_size="1800", bold=False, color="FFFFFF", align="l"))
        sid += 1
        y += 480000
    return "\n".join(parts)

def two_col_slide(title, left_items, right_items, accent_color="00A4EF"):
    """Generate a two-column content slide."""
    sid = 20
    parts = []
    parts.append(rect_shape(sid, "Bg", 0, 0, 12192000, 6858000, fill_color="1B3A5C"))
    sid += 1
    parts.append(rect_shape(sid, "TopBar", 0, 0, 12192000, 914400, fill_color=accent_color))
    sid += 1
    parts.append(text_shape(sid, "Title", 457200, 200000, 11200000, 700000, title,
                            font_size="2800", bold=True, color="FFFFFF", align="l"))
    sid += 1
    parts.append(rect_shape(sid, "Line", 457200, 850000, 3000000, 36000, fill_color=accent_color))
    sid += 1

    y = 1100000
    # Left column header
    if left_items:
        parts.append(text_shape(sid, "LHead", 457200, y, 5400000, 400000, left_items[0][0],
                                font_size="2000", bold=True, color=accent_color, align="l"))
        sid += 1
        y += 400000
        for item in left_items[1:]:
            parts.append(text_shape(sid, f"LItem", 685800, y, 5200000, 400000, f"● {item}",
                                    font_size="1600", bold=False, color="FFFFFF", align="l"))
            sid += 1
            y += 400000

    y = 1100000
    # Right column header
    if right_items:
        parts.append(text_shape(sid, "RHead", 6400000, y, 5400000, 400000, right_items[0][0],
                                font_size="2000", bold=True, color=accent_color, align="l"))
        sid += 1
        y += 400000
        for item in right_items[1:]:
            parts.append(text_shape(sid, f"RItem", 6658000, y, 5200000, 400000, f"● {item}",
                                    font_size="1600", bold=False, color="FFFFFF", align="l"))
            sid += 1
            y += 400000

    return "\n".join(parts)

def arch_slide(title, accent_color="00A4EF"):
    """Architecture slide with box diagram."""
    sid = 30
    parts = []
    parts.append(rect_shape(sid, "Bg", 0, 0, 12192000, 6858000, fill_color="1B3A5C"))
    sid += 1
    parts.append(rect_shape(sid, "TopBar", 0, 0, 12192000, 914400, fill_color=accent_color))
    sid += 1
    parts.append(text_shape(sid, "Title", 457200, 200000, 11200000, 700000, title,
                            font_size="2800", bold=True, color="FFFFFF", align="l"))
    sid += 1

    # Center boxes for architecture
    # Client box
    parts.append(rect_shape(sid, "Client", 914400, 1500000, 2200000, 800000, fill_color="2E75B6"))
    sid += 1
    parts.append(text_shape(sid, "ClientTxt", 914400, 1650000, 2200000, 500000, "🌐 Client\n(Navigateur / curl)",
                            font_size="1400", bold=True, color="FFFFFF", align="c"))
    sid += 1

    # Arrow right → Apache
    parts.append(rect_shape(sid, "Apache", 4200000, 1500000, 2800000, 800000, fill_color="00A4EF"))
    sid += 1
    parts.append(text_shape(sid, "ApacheTxt", 4200000, 1600000, 2800000, 600000, "🖥️ Apache 2\nReverse Proxy\n(80/443)",
                            font_size="1400", bold=True, color="FFFFFF", align="c"))
    sid += 1

    # Kestrel Web
    parts.append(rect_shape(sid, "KestrelWeb", 8000000, 1100000, 3200000, 700000, fill_color="28A745"))
    sid += 1
    parts.append(text_shape(sid, "KestrelWebTxt", 8000000, 1200000, 3200000, 500000, "🔄 Kestrel :5000\nRazor Pages\nwww.nextdev.ne",
                            font_size="1300", bold=True, color="FFFFFF", align="c"))
    sid += 1

    # Kestrel API
    parts.append(rect_shape(sid, "KestrelApi", 8000000, 2100000, 3200000, 700000, fill_color="DC3545"))
    sid += 1
    parts.append(text_shape(sid, "KestrelApiTxt", 8000000, 2200000, 3200000, 500000, "🔄 Kestrel :5001\nMinimal API\napi.nextdev.ne",
                            font_size="1300", bold=True, color="FFFFFF", align="c"))
    sid += 1

    # SQLite
    parts.append(rect_shape(sid, "SQLite", 8000000, 3100000, 3200000, 600000, fill_color="FFC107"))
    sid += 1
    parts.append(text_shape(sid, "SQLiteTxt", 8000000, 3200000, 3200000, 400000, "🗄️ SQLite\n(nextdev.db)",
                            font_size="1300", bold=True, color="333333", align="c"))
    sid += 1

    # DNS box
    parts.append(rect_shape(sid, "DNS", 4200000, 2700000, 2800000, 600000, fill_color="6F42C1"))
    sid += 1
    parts.append(text_shape(sid, "DNSTxt", 4200000, 2800000, 2800000, 400000, "📡 BIND9\nDNS :53",
                            font_size="1300", bold=True, color="FFFFFF", align="c"))
    sid += 1

    # DHCP box
    parts.append(rect_shape(sid, "DHCP", 4200000, 3600000, 2800000, 600000, fill_color="E83E8C"))
    sid += 1
    parts.append(text_shape(sid, "DHPCTxt", 4200000, 3700000, 2800000, 400000, "🌐 ISC DHCP\n:67",
                            font_size="1300", bold=True, color="FFFFFF", align="c"))
    sid += 1

    # Debian box bottom
    parts.append(rect_shape(sid, "Debian", 914400, 4300000, 11000000, 600000, fill_color="0D2B4A"))
    sid += 1
    parts.append(text_shape(sid, "DebianTxt", 914400, 4400000, 11000000, 400000, "🐧 Ubuntu 26.04 LTS - 10.0.0.68",
                            font_size="1600", bold=True, color="FFFFFF", align="c"))
    sid += 1

    return "\n".join(parts)

def centered_title_slide(title, subtitle, items=None, accent_color="00A4EF"):
    """Slide with centered big text."""
    sid = 40
    parts = []
    parts.append(rect_shape(sid, "Bg", 0, 0, 12192000, 6858000, fill_color="1B3A5C"))
    sid += 1
    parts.append(rect_shape(sid, "Accent", 0, 0, 12192000, 914400, fill_color=accent_color))
    sid += 1
    parts.append(text_shape(sid, "Title", 914400, 1200000, 10400000, 900000, title,
                            font_size="3600", bold=True, color="FFFFFF", align="c"))
    sid += 1
    parts.append(text_shape(sid, "Sub", 914400, 2100000, 10400000, 600000, subtitle,
                            font_size="2000", bold=False, color="A0C4E8", align="c"))
    sid += 1
    if items:
        y = 3000000
        for item in items:
            parts.append(text_shape(sid, f"I", 1828800, y, 8500000, 400000, f"✅ {item}",
                                    font_size="1600", bold=False, color="FFFFFF", align="l"))
            sid += 1
            y += 450000
    return "\n".join(parts)


# ==============================
# BUILD SLIDES
# ==============================

slides_content = []

# Slide 1: Title
slides_content.append(title_slide_content(
    "Challenge NextDev",
    "Hébergement .NET 9\nConfiguration d'infrastructure Open Source\net déploiement applicatif Full-Stack en 48 heures"
))

# Slide 2: Contexte
slides_content.append(section_slide(
    "Contexte & Périmètre du Projet",
    [
        "Deux domaines isolés : www.nextdev.ne (site) et api.nextdev.ne (API)",
        "ASP.NET Core 9 : Razor Pages pour le site vitrine",
        "Minimal API pour le backend REST",
        "Base de données SQLite (portable, zéro config)",
        "Infrastructure : DNS (BIND9), DHCP (ISC), Apache 2",
        "OS : Debian 12 (Bookworm)"
    ],
    accent_color="00A4EF"
))

# Slide 3: Architecture
slides_content.append(arch_slide(
    "Architecture Globale",
    accent_color="00A4EF"
))

# Slide 4: Infrastructure
slides_content.append(two_col_slide(
    "Infrastructure Réseau & Serveur",
    [
        "🌐 DNS (BIND9)",
        "Zone nextdev.ne configurée",
        "www → 10.0.0.68",
        "api → 10.0.0.68",
        "",
        "🛡️ Sécurité",
        "Pare-feu UFW actif",
        "Ports 22, 80, 443, 53, 67",
    ],
    [
        "📡 DHCP (ISC-DHCP)",
        "Plage : 10.0.0.50-200",
        "Bail : 600-7200 secondes",
        "Option routeur & DNS",
        "",
        "🔧 Apache 2",
        "mod_proxy + mod_proxy_http",
        "VirtualHosts configurés",
    ],
    accent_color="6F42C1"
))

# Slide 5: Développement .NET
slides_content.append(two_col_slide(
    "Développement .NET 9",
    [
        "🖥️ Site Vitrine (Razor Pages)",
        "ASP.NET Core 9 Razor Pages",
        "Port interne : 5000",
        "Pages : Accueil, Confidentalité",
        "Thème Bootstrap responsive",
        "Layout personnalisé",
    ],
    [
        "⚙️ API REST (Minimal API)",
        "ASP.NET Core 9 Minimal API",
        "Port interne : 5001",
        "GET / → Infos API",
        "GET /trainee → Liste stagiaires",
        "POST /trainee → Ajout (optionnel)",
        "📖 Swagger UI → /swagger",
    ],
    accent_color="28A745"
))

# Slide 6: Base de données
slides_content.append(two_col_slide(
    "Base de Données SQLite",
    [
        "🗄️ Modèle Trainee",
        "Id (int, PK)",
        "Nom (string, required)",
        "Prénom (string, required)",
        "Email (string, unique)",
        "DateNaissance (Date)",
        "DateInscription (DateTime)",
    ],
    [
        "📊 Entity Framework Core",
        "ORM Microsoft performant",
        "Migrations automatiques",
        "EnsureCreated() au démarrage",
        "",
        "🌱 Données de démonstration",
        "5 stagiaires préchargés",
        "(Diop, Koné, Traoré, etc.)",
    ],
    accent_color="FFC107"
))

# Slide 7: Reverse Proxy
slides_content.append(two_col_slide(
    "Configuration Reverse Proxy (Apache)",
    [
        "🔄 Principe",
        "Apache reçoit les requêtes (80/443)",
        "ProxyPass vers Kestrel (5000/5001)",
        "Client ne voit que Apache",
        "",
        "📦 Modules Apache",
        "mod_proxy, mod_proxy_http",
        "mod_rewrite, mod_ssl",
        "mod_headers, mod_deflate",
    ],
    [
        "🔒 Sécurité & SSL",
        "Let's Encrypt (Certbot)",
        "HTTPS automatique",
        "Redirection HTTP → HTTPS",
        "",
        "⚡ Optimisations",
        "Compression Gzip",
        "Cache fichiers statiques",
        "Timeouts configurés (300s)",
    ],
    accent_color="DC3545"
))

# Slide 8: Tests
slides_content.append(section_slide(
    "Tests & Résultats",
    [
        "✅ Résolution DNS fonctionnelle (dig/nslookup)",
        "✅ DHCP attribue les IPs dans la plage configurée",
        "✅ Apache Reverse Proxy opérationnel sur les 2 domaines",
        "✅ Site vitrine accessible : www.nextdev.ne",
        "✅ API REST fonctionnelle : api.nextdev.ne",
        "✅ Endpoint /trainee retourne la liste JSON des stagiaires",
        "✅ Swagger UI disponible : /swagger",
        "✅ Test direct (Kestrel) et via Apache fonctionnels",
    ],
    accent_color="28A745"
))

# Slide 9: Difficultés et Solutions
slides_content.append(two_col_slide(
    "Difficultés Rencontrées & Solutions",
    [
        "⚠️ Difficultés",
        "Configuration BIND9 (syntaxe stricte)",
        "Communication Apache ↔ Kestrel",
        "Forwarded Headers manquants",
        "Gestion des ports sous Linux",
        "Coordination sur 48h",
    ],
    [
        "💡 Solutions",
        "named-checkconf + logs détaillés",
        "Forwarded Headers middleware",
        "Configuration X-Forwarded-*",
        "Netstat + UFW pour le diagnostic",
        "Scripts automatisés + réunions",
    ],
    accent_color="E83E8C"
))

# Slide 10: Teamwork
slides_content.append(section_slide(
    "Travail d'Équipe & Communication",
    [
        "👥 4 rôles distincts : Infrastructure, Web, API, Intégration",
        "🔄 Réunions régulières toutes les 4 heures",
        "📋 Partage via documentation commune",
        "🤝 Entraide sur les modules critiques (Reverse Proxy)",
        "🎯 Objectif commun : livrer un projet complet et fonctionnel",
        "📢 Communication claire et continue",
    ],
    accent_color="00A4EF"
))

# Slide 11: Conclusion
slides_content.append(centered_title_slide(
    "Merci pour votre attention !",
    "NextDev Challenge | 48 Heures | .NET 9",
    items=[
        "Projet fonctionnel de bout en bout",
        "Architecture scalable et sécurisée",
        "Stack technique maîtrisée : Linux + Apache + .NET",
        "Collaboration d'équipe efficace",
    ],
    accent_color="00A4EF"
))

SLIDE_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""

SLIDE_LAYOUT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             type="blank">
  <p:cSld name="Blank">
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
    </p:spTree>
  </p:cSld>
</p:sldLayout>"""


def build_pptx():
    """Build the PPTX file."""
    files = {}

    # [Content_Types].xml
    slide_cts = "".join(
        f'\n  <Override PartName="/ppt/slides/slide{i+1}.xml" '
        f'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(len(slides_content))
    )
    files["[Content_Types].xml"] = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>
  <Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>
  <Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  {slide_cts}
</Types>
"""

    for i in range(len(slides_content)):
        files[f"ppt/slides/slide{i+1}.xml"] = TEMPLATE_SLIDE.format(content=slides_content[i])
        files[f"ppt/slides/_rels/slide{i+1}.xml.rels"] = SLIDE_RELS

    # _rels/.rels
    files["_rels/.rels"] = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail" Target="docProps/thumbnail.jpeg"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>"""

    # ppt/presentation.xml
    slide_ids = "".join(f'<p:sldId id="{256+i}" r:id="rId{i+2}"/>' for i in range(len(slides_content)))
    files["ppt/presentation.xml"] = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst>
    <p:sldMasterId id="2147483648" r:id="rId1"/>
  </p:sldMasterIdLst>
  <p:sldIdLst>
    {slide_ids}
  </p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""

    # ppt/_rels/presentation.xml.rels
    slide_rels = "".join(f'<Relationship Id="rId{i+2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i+1}.xml"/>' for i in range(len(slides_content)))
    files["ppt/_rels/presentation.xml.rels"] = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  {slide_rels}
</Relationships>"""

    # ppt/slideMasters/slideMaster1.xml
    files["ppt/slideMasters/slideMaster1.xml"] = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="2" name="Background"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="0" y="0"/>
            <a:ext cx="12192000" cy="6858000"/>
          </a:xfrm>
          <a:prstGeom prst="rect"/>
          <a:solidFill>
            <a:srgbClr val="FFFFFF"/>
          </a:solidFill>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          <a:p><a:endParaRPr lang="fr-FR"/></a:p>
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
  <p:clrMap>
    <a:masterClrMapping/>
  </p:clrMap>
</p:sldMaster>"""

    files["ppt/slideLayouts/slideLayout1.xml"] = SLIDE_LAYOUT

    # ppt/theme/theme1.xml
    files["ppt/theme/theme1.xml"] = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="NextDev">
  <a:themeElements>
    <a:clrScheme name="NextDev">
      <a:dk1><a:srgbClr val="1B3A5C"/></a:dk1>
      <a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="00A4EF"/></a:dk2>
      <a:lt2><a:srgbClr val="A0C4E8"/></a:lt2>
      <a:accent1><a:srgbClr val="00A4EF"/></a:accent1>
      <a:accent2><a:srgbClr val="28A745"/></a:accent2>
      <a:accent3><a:srgbClr val="DC3545"/></a:accent3>
      <a:accent4><a:srgbClr val="FFC107"/></a:accent4>
      <a:accent5><a:srgbClr val="6F42C1"/></a:accent5>
      <a:accent6><a:srgbClr val="E83E8C"/></a:accent6>
      <a:hlink><a:srgbClr val="00A4EF"/></a:hlink>
      <a:folHlink><a:srgbClr val="00A4EF"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="NextDev">
      <a:majorFont><a:latin typeface="Calibri"/></a:majorFont>
      <a:minorFont><a:latin typeface="Calibri"/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="NextDev">
      <a:fillStyleLst/>
      <a:lnStyleLst/>
      <a:effectStyleLst/>
      <a:bgFillStyleLst/>
    </a:fmtScheme>
  </a:themeElements>
</a:theme>"""

    files["ppt/presProps.xml"] = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presProps xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>"""

    files["ppt/viewProps.xml"] = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:viewProps xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:normalViewPr><p:restoredLeft cx="0"/><p:restoredTop cy="0"/></p:normalViewPr>
</p:viewProps>"""

    files["ppt/tableStyles.xml"] = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>"""

    files["docProps/core.xml"] = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:title>Challenge NextDev - Hébergement .NET 9</dc:title>
  <dc:subject>Présentation du Challenge</dc:subject>
  <dc:creator>NextDev Team</dc:creator>
</cp:coreProperties>"""

    files["docProps/app.xml"] = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
  <Application>NextDev Challenge</Application>
  <PresentationFormat>Widescreen</PresentationFormat>
  <SlideCount>""" + str(len(slides_content)) + """</SlideCount>
</Properties>"""

    # Write ZIP
    with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)

    print(f"✓ PPTX created: {OUTPUT}")
    print(f"  Slides: {len(slides_content)}")

if __name__ == "__main__":
    build_pptx()
