import os
import requests

# Optionally, load .env here or in main file

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

def call_gemini_api(prompt, parse_function=None):
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "safetySettings": [{"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]
    }
    try:
        response = requests.post(GEMINI_URL, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            content = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            return parse_function(content) if parse_function else content
        else:
            raise Exception(f"Gemini returned status code: {response.status_code}")
    except Exception as e:
        raise e


def parse_ai_response(content):
    parts = {
        "seo_title": "",
        "seo_description": "",
        "description": "",
        "keywords": "",
        "item_number": "",
        "item_number_supplier": "",
        "ean": ""
    }
    key_map = {
        "[SEO_TITLE]": "seo_title",
        "[SEO_DESCRIPTION]": "seo_description",
        "[DESCRIPTION]": "description",
        "[KEYWORDS]": "keywords",
        "[ITEM_NUMBER]": "item_number",
        "[ITEM_NUMBER_SUPPLIER]": "item_number_supplier",
        "[EAN]": "ean"
    }

    current_key = None
    for line in content.splitlines():
        line = line.strip()
        if line in key_map:
            current_key = key_map[line]
        elif line and current_key:
            parts[current_key] += line + " "

    # Cleanup
    for key in parts:
        parts[key] = parts[key].strip()

    # Format keywords
    parts["keywords"] = parts["keywords"].replace(" ", "").rstrip(",")

    # Fallbacks
    defaults = {
        "seo_title": "SEO Title Not Generated",
        "seo_description": "SEO Description Not Generated",
        "description": "Detailed description not available.",
        "keywords": "keyword1,keyword2,keyword3",
        "item_number": "Not found",
        "item_number_supplier": "Not found",
        "ean": "Not found"
    }
    for key, fallback in defaults.items():
        if not parts[key]:
            parts[key] = fallback

    return parts


def generate_seo_with_ai(title):
    if not title:
        raise ValueError("Title is required")

    prompt = f"""
    Du er en erfaren SEO-tekstforfatter for webshoppen https://ink-house.dk/.
    Din opgave er at generere SEO-optimeret, seniorvenligt og prisvenligt indhold baseret på produktets titel: '{title}'.
    Omskriv titel, beskrivelse og SEO-tekster, så de bliver engagerende, klare og optimerede til webshoppen.

    Før du skriver teksten:
    - Søg først på internettet efter følgende informationer:
      1. **EAN-nummer** (13-cifret stregkode) for dette produkt
      2. **Varenummer** (item number)
      3. **Leverandørens varenummer** (supplier item number)
    Hvis du ikke kan finde dem online, så gæt bedst muligt ud fra kendte mønstre og lignende produkter.

    Giv dit output i dette præcise format – uden ekstra kommentarer:

    [SEO_TITLE]
    En kort SEO-titel på under 60 tegn, tilpasset webshoppen

    [SEO_DESCRIPTION]
    En SEO-beskrivelse på under 160 tegn, med nøgleinformation og prisvenligt sprog

    [DESCRIPTION]
    Min. 150 ord – en detaljeret og omskrevet produktbeskrivelse, målrettet seniorer og prisbevidste kunder

    [KEYWORDS]
    Mindst 20 danske SEO-søgeord, kommasepareret uden mellemrum

    [ITEM_NUMBER]
    Varenummer – gættes hvis nødvendigt

    [ITEM_NUMBER_SUPPLIER]
    Leverandørens varenummer – gættes hvis nødvendigt

    [EAN]
    Et gyldigt 13-cifret EAN-nummer – gæt hvis nødvendigt
    """

    parts = call_gemini_api(prompt, parse_function=parse_ai_response)


    # Optional validation
    missing = [k for k, v in parts.items() if not v]
    if missing:
        raise ValueError(f"Missing AI generated parts: {missing}")

    return parts


def generate_seo_with_ai_for_category(title):
    if not title:
        raise ValueError("Title is required")

    prompt = f"""
    Du er en professionel SEO-tekstforfatter med erfaring fra webshoppen https://ink-house.dk/.
    Din opgave er at generere SEO-optimeret, seniorvenligt og prisvenligt indhold baseret på kategorititlen: '{title}'.
    Omskriv titel, beskrivelse og SEO-tekster, så de bliver engagerende, klare og optimeret til webshop-format.

    Formatér dit svar præcist som nedenfor – uden ekstra forklaring:

    [SEO_TITLE]
    Kort og fængende SEO-titel på under 60 tegn

    [SEO_DESCRIPTION]
    SEO-beskrivelse på maks. 160 tegn med prisvenligt sprog

    [DESCRIPTION]
    Min. 150 ord – produktbeskrivelse velegnet til seniorer og prisbevidste kunder

    [DESCRIPTION_BOTTOM]
    Min. 50 ord – ekstra tekst til sidens bund

    [KEYWORDS]
    Min. 20 danske SEO-søgeord, kommasepareret uden mellemrum

    [SEO_LINK]
    Et unikt SEO-link i URL-format (f.eks. /deskjet-3949) – gæt hvis nødvendigt
    """

    return call_gemini_api(prompt, parse_function=parse_category_response)


def parse_category_response(content):
    parts = {
        "seo_title": "",
        "seo_description": "",
        "description": "",
        "description_bottom": "",
        "keywords": "",
        "seo_link": ""
    }
    key_map = {
        "[SEO_TITLE]": "seo_title",
        "[SEO_DESCRIPTION]": "seo_description",
        "[DESCRIPTION]": "description",
        "[DESCRIPTION_BOTTOM]": "description_bottom",
        "[KEYWORDS]": "keywords",
        "[SEO_LINK]": "seo_link"
    }

    current_key = None
    for line in content.splitlines():
        line = line.strip()
        if line in key_map:
            current_key = key_map[line]
        elif line and current_key:
            parts[current_key] += line + " "

    # Cleanup
    for key in parts:
        parts[key] = parts[key].strip()

    # Format keywords
    parts["keywords"] = parts["keywords"].replace(" ", "").rstrip(",")

    # Fallbacks
    defaults = {
        "seo_title": "SEO Title Not Generated",
        "seo_description": "SEO Description Not Generated",
        "description": "Detailed description not available.",
        "description_bottom": "Additional description not available.",
        "keywords": "keyword1,keyword2,keyword3",
        "seo_link": "Not found"
    }
    for key, fallback in defaults.items():
        if not parts[key]:
            parts[key] = fallback

    return parts