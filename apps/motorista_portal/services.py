"""
Serviços para o quadro de avisos do portal do motorista.
- Previsão do tempo via Open-Meteo (gratuito, sem API key)
- Notícias de política/Brasil via RSS do G1
"""

import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from html import unescape
from urllib.error import URLError
from urllib.request import Request, urlopen

from django.core.cache import cache

logger = logging.getLogger(__name__)

# Costa do Dendê – Valença / BA
LATITUDE = -13.38
LONGITUDE = -39.07

WEATHER_CODES = {
    0: ("☀️", "Céu limpo"),
    1: ("🌤️", "Poucas nuvens"),
    2: ("⛅", "Parcialmente nublado"),
    3: ("☁️", "Nublado"),
    45: ("🌫️", "Neblina"),
    48: ("🌫️", "Neblina com geada"),
    51: ("🌦️", "Chuvisco leve"),
    53: ("🌦️", "Chuvisco"),
    55: ("🌦️", "Chuvisco forte"),
    61: ("🌧️", "Chuva leve"),
    63: ("🌧️", "Chuva moderada"),
    65: ("🌧️", "Chuva forte"),
    80: ("🌧️", "Pancadas leves"),
    81: ("🌧️", "Pancadas moderadas"),
    82: ("🌧️", "Pancadas fortes"),
    95: ("⛈️", "Tempestade"),
    96: ("⛈️", "Tempestade com granizo"),
    99: ("⛈️", "Tempestade severa"),
}

DIAS_SEMANA = [
    "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo",
]


def _http_get(url, timeout=10):
    """GET simples com User-Agent adequado."""
    req = Request(url, headers={"User-Agent": "CostadoDende/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def obter_previsao_tempo():
    """Retorna previsão do tempo (cache de 1 h)."""
    cache_key = "quadro_avisos_tempo"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={LATITUDE}&longitude={LONGITUDE}"
        f"&current_weather=true"
        f"&daily=temperature_2m_max,temperature_2m_min,weathercode"
        f"&timezone=America/Bahia&forecast_days=4"
    )
    try:
        data = json.loads(_http_get(url))
    except (URLError, json.JSONDecodeError, OSError) as exc:
        logger.warning("Erro ao buscar previsão: %s", exc)
        return None

    current = data.get("current_weather", {})
    code = current.get("weathercode", 0)
    icone, descricao = WEATHER_CODES.get(code, ("🌡️", "Desconhecido"))

    daily = data.get("daily", {})
    previsao_dias = []
    for i, dt_str in enumerate(daily.get("time", [])):
        dt = datetime.strptime(dt_str, "%Y-%m-%d")
        dia_code = daily["weathercode"][i]
        d_icone, d_desc = WEATHER_CODES.get(dia_code, ("🌡️", "—"))
        previsao_dias.append({
            "dia_semana": DIAS_SEMANA[dt.weekday()],
            "data": dt.strftime("%d/%m"),
            "icone": d_icone,
            "descricao": d_desc,
            "max": round(daily["temperature_2m_max"][i]),
            "min": round(daily["temperature_2m_min"][i]),
        })

    resultado = {
        "temperatura": round(current.get("temperature", 0)),
        "icone": icone,
        "descricao": descricao,
        "vento": round(current.get("windspeed", 0)),
        "proximos_dias": previsao_dias,
    }
    cache.set(cache_key, resultado, 3600)  # 1 hora
    return resultado


def _limpar_html(text):
    """Remove tags HTML básicas de um texto."""
    import re
    clean = re.sub(r"<[^>]+>", "", text)
    return unescape(clean).strip()


def obter_noticias():
    """Retorna notícias de política/Brasil via RSS (cache de 2 h)."""
    cache_key = "quadro_avisos_noticias"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    feeds = [
        "https://g1.globo.com/rss/g1/politica/",
        "https://g1.globo.com/rss/g1/brasil/",
    ]
    noticias = []

    for feed_url in feeds:
        try:
            raw = _http_get(feed_url, timeout=15)
            root = ET.fromstring(raw)
            for item in root.iter("item"):
                titulo = item.findtext("title", "")
                link = item.findtext("link", "")
                descricao = _limpar_html(item.findtext("description", ""))
                pub_date = item.findtext("pubDate", "")
                if titulo:
                    noticias.append({
                        "titulo": titulo,
                        "link": link,
                        "resumo": descricao[:200] if descricao else "",
                        "data": pub_date,
                    })
        except (URLError, ET.ParseError, OSError) as exc:
            logger.warning("Erro ao buscar RSS %s: %s", feed_url, exc)

    # Limitar a 10 notícias, remover duplicatas por título
    vistos = set()
    unicas = []
    for n in noticias:
        if n["titulo"] not in vistos:
            vistos.add(n["titulo"])
            unicas.append(n)
        if len(unicas) >= 10:
            break

    cache.set(cache_key, unicas, 7200)  # 2 horas
    return unicas
