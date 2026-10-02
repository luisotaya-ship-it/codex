#!/usr/bin/env python3
"""
buscar_y_descargar.py — busca imágenes reales en bancos abiertos, verifica su
licencia y las descarga a disco. Esto es lo que reemplaza a "búscala tú
mismo en tal banco": la skill ejecuta este script y obtiene archivos reales
con su licencia ya verificada, no una sugerencia de dónde mirar.

Bancos soportados:

  commons   Wikimedia Commons. Búsqueda + licencia + descarga totalmente
            automatizadas vía la API oficial (action=query). Es el banco
            por defecto para categoría 2 (escena/contexto) y sirve también
            para categoría 1 (hallazgo clínico real) cuando la imagen
            proviene de un atlas/artículo con licencia abierta ya indicada
            en Commons.

  openi     NLM Open-i (biomedical image search, PubMed Central Open Access).
            Ideal para categoría 1 (hallazgo clínico real con cita de
            artículo). La API de búsqueda de Open-i no expone la licencia
            por imagen directamente, así que `openi-descargar` la verifica
            por su cuenta contra el servicio de acceso abierto de NCBI
            (oa.fcgi por PMCID) antes de traer el archivo — sin necesidad de
            abrir la página del artículo (que además suele bloquear el
            acceso automatizado con un reCAPTCHA). Si el artículo no está en
            el subconjunto de acceso abierto de PMC, el script rehúsa
            descargar en vez de asumir que es seguro usarlo.

REGLA DE ORO QUE ESTE SCRIPT NO PUEDE APLICAR POR TI:
La licencia abierta autoriza el uso legal de la imagen, pero NO garantiza
que sea apropiada. Antes de aceptar un candidato de categoría 2 (escena con
persona), ábrelo con la herramienta de lectura de imágenes y revisa si
muestra un rostro identificable de un paciente real — si lo muestra,
DESCÁRTALO aunque la licencia sea abierta (public domain o CC no implica
que el sujeto haya dado su consentimiento para este uso específico). Preferir
siempre composiciones sin rostro identificable (manos, equipo, espalda,
plano general) para escenas de "paciente genérico".

Uso:
    # 1) Buscar candidatos en Wikimedia Commons (con o sin filtro a imagen)
    python3 buscar_y_descargar.py commons-buscar "COPD oxygen therapy" --limite 8

    # 2) Ver licencia/metadata de un candidato puntual antes de decidir
    python3 buscar_y_descargar.py commons-info "File:Oxygen therapy.jpg"

    # 3) Descargar (solo si la licencia es abierta; el script la revalida)
    python3 buscar_y_descargar.py commons-descargar "File:Oxygen therapy.jpg" \
        --destino ./imagenes_descargadas/oxigenoterapia.jpg

    # Open-i (categoría 1 — hallazgo clínico real con cita)
    python3 buscar_y_descargar.py openi-buscar "chest radiograph COPD hyperinflation" --limite 8
    # -> tomar el "uid" (PMCID) del candidato elegido y descargar (verifica licencia sola):
    python3 buscar_y_descargar.py openi-descargar --pmcid PMC5077736 \
        --url "<img_large del candidato elegido>" \
        --destino ./imagenes_descargadas/hallazgo.png

Requiere `requests` (ya disponible en el entorno). Hace peticiones reales a
commons.wikimedia.org, openi.nlm.nih.gov y ncbi.nlm.nih.gov — necesita red.
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests

USER_AGENT = "ClaudeSkillImagenesContextuales/1.0 (uso educativo; material academico de residencia medica)"

LICENCIAS_ABIERTAS_SIN_RESTRICCION = (
    "public domain", "cc0", "cc by 2.0", "cc by 3.0", "cc by 4.0",
    "cc by-sa 2.0", "cc by-sa 3.0", "cc by-sa 4.0", "cc by", "cc by-sa",
)
LICENCIAS_ABIERTAS_NO_COMERCIAL = (
    "cc by-nc", "cc by-nc-sa", "cc by-nc-nd",
)


def _session():
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def _get_con_reintento(session, url, params, intentos=4, espera_inicial=6, timeout=25):
    espera = espera_inicial
    ultimo_error = None
    for _ in range(intentos):
        try:
            r = session.get(url, params=params, timeout=timeout)
        except requests.exceptions.RequestException as e:
            ultimo_error = e
            time.sleep(espera)
            espera *= 2
            continue
        if r.status_code in (429, 503):
            time.sleep(espera)
            espera *= 2
            continue
        r.raise_for_status()
        return r
    raise RuntimeError(f"No se pudo consultar {url} tras {intentos} intentos ({ultimo_error or 'ver códigos 429/503 repetidos'})")


def clasificar_licencia(nombre_licencia):
    """Devuelve (permitida: bool, nota: str) para un LicenseShortName de Commons."""
    if not nombre_licencia:
        return False, "sin licencia declarada — descartar"
    n = nombre_licencia.strip().lower()
    if n in LICENCIAS_ABIERTAS_SIN_RESTRICCION or n.startswith("cc by") and "nc" not in n:
        return True, "uso abierto, atribuir autor si se conoce"
    if any(n.startswith(x) for x in LICENCIAS_ABIERTAS_NO_COMERCIAL):
        return True, "SOLO uso no comercial/académico (esta presentación de residencia califica) — atribuir autor y dejarlo anotado en el registro de fuentes"
    return False, f"licencia '{nombre_licencia}' no reconocida como abierta — descartar salvo verificación manual"


# ---------- Wikimedia Commons ----------

def commons_buscar(query, limite=8, solo_bitmap=True):
    s = _session()
    q = f"{query} filetype:bitmap" if solo_bitmap else query
    r = _get_con_reintento(s, "https://commons.wikimedia.org/w/api.php", {
        "action": "query", "list": "search", "srsearch": q,
        "srnamespace": 6, "srlimit": limite, "format": "json",
    })
    return [x["title"] for x in r.json()["query"]["search"]]


def commons_info(titulo):
    s = _session()
    r = _get_con_reintento(s, "https://commons.wikimedia.org/w/api.php", {
        "action": "query", "titles": titulo, "prop": "imageinfo",
        "iiprop": "url|mime|extmetadata|size", "format": "json",
    })
    pages = r.json()["query"]["pages"]
    for _, p in pages.items():
        if "imageinfo" not in p:
            return {"titulo": titulo, "error": "sin imageinfo (¿título mal escrito?)"}
        ii = p["imageinfo"][0]
        meta = ii.get("extmetadata", {})
        licencia = meta.get("LicenseShortName", {}).get("value")
        permitida, nota = clasificar_licencia(licencia)
        return {
            "titulo": p.get("title"),
            "url": ii.get("url"),
            "mime": ii.get("mime"),
            "ancho": ii.get("width"), "alto": ii.get("height"),
            "licencia": licencia,
            "licencia_permitida": permitida,
            "nota_licencia": nota,
            "artista": (meta.get("Artist", {}).get("value", "") or "")[:150],
        }
    return {"titulo": titulo, "error": "no encontrado"}


def commons_descargar(titulo, destino):
    info = commons_info(titulo)
    if info.get("error"):
        print(json.dumps({"ok": False, "motivo": info["error"]}, ensure_ascii=False))
        sys.exit(1)
    if not info["licencia_permitida"]:
        print(json.dumps({"ok": False, "motivo": f"licencia no abierta: {info['licencia']}"}, ensure_ascii=False))
        sys.exit(1)
    s = _session()
    r = s.get(info["url"], timeout=30)
    r.raise_for_status()
    if not r.headers.get("Content-Type", "").startswith("image/"):
        print(json.dumps({"ok": False, "motivo": f"Content-Type inesperado: {r.headers.get('Content-Type')}"}, ensure_ascii=False))
        sys.exit(1)
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(r.content)
    print(json.dumps({
        "ok": True, "archivo": str(destino), "bytes": len(r.content),
        "licencia": info["licencia"], "nota_licencia": info["nota_licencia"],
        "artista": info["artista"], "fuente": info["url"],
        "recordatorio": "Antes de usarla en categoría 2, ábrela y confirma que no muestra un rostro identificable de un paciente real.",
    }, ensure_ascii=False, indent=2))


# ---------- NLM Open-i ----------

def openi_buscar(query, limite=8):
    s = _session()
    r = _get_con_reintento(s, "https://openi.nlm.nih.gov/api/search", {
        "query": query, "it": "x,c", "m": 1, "n": limite,
    }, intentos=3, espera_inicial=8)
    data = r.json()
    candidatos = []
    for item in data.get("list", []):
        candidatos.append({
            "uid": item.get("uid"),  # esto ES el PMCID, pásalo tal cual a openi-descargar --pmcid
            "titulo_articulo": item.get("title"),
            "caption": (item.get("image") or {}).get("caption"),
            "img_large": f"https://openi.nlm.nih.gov{item.get('imgLarge', '')}" if item.get("imgLarge") else None,
            "pmid": item.get("pmid"),
            "journal": item.get("journal_title"),
            "autores": item.get("authors"),
        })
    print(json.dumps({
        "total_disponible": data.get("total"),
        "candidatos": candidatos,
        "siguiente_paso": "Elige un candidato por su 'caption' (debe describir el hallazgo que necesitas) y "
                           "descárgalo con: openi-descargar --pmcid <uid> --url <img_large> --destino <ruta>. "
                           "La licencia se verifica sola contra el servicio de acceso abierto de PMC.",
    }, ensure_ascii=False, indent=2))
    return candidatos


def openi_licencia_pmc(pmcid):
    """Consulta el servicio de acceso abierto de NCBI por PMCID. Devuelve el
    string de licencia (p.ej. 'CC BY', 'CC BY-NC-ND') o None si el artículo
    no está en el subconjunto de acceso abierto de PMC (= no verificable
    automáticamente)."""
    s = _session()
    r = _get_con_reintento(s, "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi",
                            {"id": pmcid}, intentos=3, espera_inicial=5)
    m = re.search(r'license="([^"]+)"', r.text)
    return m.group(1) if m else None


def clasificar_licencia_pmc(license_str):
    """Devuelve (permitida, editable, nota). 'editable' = False si la licencia
    tiene cláusula ND (No Derivatives): en ese caso no se debe recortar ni
    tratar la imagen con tratar_imagen.py, solo insertarla tal cual o
    descartarla."""
    if not license_str:
        return False, False, ("no está en el subconjunto de acceso abierto de PMC — no se puede verificar "
                               "automáticamente; no descargar sin revisión manual del artículo")
    n = license_str.strip().upper()
    editable = "ND" not in n
    nota = f"licencia PMC: {license_str}"
    if "NC" in n:
        nota += " — uso no comercial/académico únicamente (esta presentación de residencia califica)"
    if not editable:
        nota += " — cláusula ND: NO recortar ni aplicar tratamiento de imagen, insertar sin modificar"
    return True, editable, nota


def openi_descargar(url, destino, pmcid):
    licencia = openi_licencia_pmc(pmcid)
    permitida, editable, nota = clasificar_licencia_pmc(licencia)
    if not permitida:
        print(json.dumps({"ok": False, "motivo": nota, "pmcid": pmcid}, ensure_ascii=False, indent=2))
        sys.exit(1)
    s = _session()
    r = s.get(url, timeout=30)
    r.raise_for_status()
    if not r.headers.get("Content-Type", "").startswith("image/"):
        print(json.dumps({"ok": False, "motivo": f"Content-Type inesperado: {r.headers.get('Content-Type')}"}, ensure_ascii=False))
        sys.exit(1)
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(r.content)
    print(json.dumps({
        "ok": True, "archivo": str(destino), "bytes": len(r.content), "fuente": url,
        "pmcid": pmcid, "licencia": licencia, "editable": editable, "nota_licencia": nota,
        "recordatorio": "Deja registrada la cita del artículo (PMCID/PMID) como fuente en el registro de imágenes.",
    }, ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comando", required=True)

    sp = sub.add_parser("commons-buscar")
    sp.add_argument("query")
    sp.add_argument("--limite", type=int, default=8)
    sp.add_argument("--sin-filtro-bitmap", action="store_true")

    sp = sub.add_parser("commons-info")
    sp.add_argument("titulo")

    sp = sub.add_parser("commons-descargar")
    sp.add_argument("titulo")
    sp.add_argument("--destino", required=True)

    sp = sub.add_parser("openi-buscar")
    sp.add_argument("query")
    sp.add_argument("--limite", type=int, default=8)

    sp = sub.add_parser("openi-descargar")
    sp.add_argument("--url", required=True, help="img_large del candidato (de openi-buscar)")
    sp.add_argument("--pmcid", required=True, help="uid del candidato (de openi-buscar), p.ej. PMC5077736")
    sp.add_argument("--destino", required=True)

    args = p.parse_args()

    try:
        if args.comando == "commons-buscar":
            titulos = commons_buscar(args.query, args.limite, solo_bitmap=not args.sin_filtro_bitmap)
            print(json.dumps({"query": args.query, "resultados": titulos}, ensure_ascii=False, indent=2))
        elif args.comando == "commons-info":
            print(json.dumps(commons_info(args.titulo), ensure_ascii=False, indent=2))
        elif args.comando == "commons-descargar":
            commons_descargar(args.titulo, args.destino)
        elif args.comando == "openi-buscar":
            openi_buscar(args.query, args.limite)
        elif args.comando == "openi-descargar":
            openi_descargar(args.url, args.destino, args.pmcid)
    except (requests.exceptions.RequestException, RuntimeError) as e:
        print(json.dumps({
            "ok": False,
            "motivo": f"Error de red consultando el banco: {e}",
            "sugerencia": "Reintentar en unos segundos, o probar con el otro banco (commons/openi) si sigue fallando.",
        }, ensure_ascii=False, indent=2))
        sys.exit(2)


if __name__ == "__main__":
    main()
