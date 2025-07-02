import streamlit as st
import pandas as pd

# ===== DEMO_LISTINGS with already parsed AI fields =====
DEMO_LISTINGS = [
    {
        "title": "Cozy 2-room apartment near Porta Romana",
        "price": "€1400/month",
        "url": "https://www.idealista.it/immobile/32498907/",
        "district": "Porta Romana",
        "floor": 4,
        "description": "Modern, furnished apartment with balcony. Pets allowed. New kitchen, close to metro.",
        "furnished": True,
        "pets_allowed": True,
        "renovation": "modern",
        "amenities": ["balcony", "kitchen", "metro"]
    },
    {
        "title": "Charming 2-room apartment in the heart of the Movida",
        "price": "€1,150/month",
        "url": "https://www.idealista.it/immobile/32864389/",
        "district": "Navigli",
        "floor": 1,
        "description": "Cozy apartment with rustic style and custom furniture. Furnished, pets allowed. Well connected both for public and private transport.",
        "furnished": True,
        "pets_allowed": True,
        "renovation": "basic",
        "amenities": ["public transport", "private transport", "city center"]
    },
    {
        "title": "Unfurnished 2-room apartment near Piazza Velasques",
        "price": "€820/month",
        "url": "https://www.idealista.it/immobile/32469487/",
        "district": "Zone 7 of Milan",
        "floor": 1,
        "description": "Unfurnished, pets allowed, modern renovation. Quiet street, close to park and public transport.",
        "furnished": False,
        "pets_allowed": True,
        "renovation": "modern",
        "amenities": ["park", "public transport", "quiet street"]
    },
    {
        "title": "Bright two-room apartment with renovated kitchen, fully furnished, allows small pets.",
        "price": "€1,200/month",
        "url": "https://www.idealista.it/immobile/10486516/",
        "district": "Montalbino",
        "floor": 1,
        "description": "Fully furnished cozy apartment, pets allowed. Modern renovation, well connected to public transport and supermarkets.",
        "furnished": True,
        "pets_allowed": True,
        "renovation": "modern",
        "amenities": ["public transport", "supermarket"]
    },
    {
        "title": "Two-room apartment in via Gonin 9",
        "price": "€800/month",
        "url": "https://www.idealista.it/immobile/32307276/",
        "district": "Giambellino",
        "floor": 1,
        "description": "Charming 2-room apartment, pets allowed. Designed renovation. Good view, near to all amenities.",
        "furnished": False,
        "pets_allowed": True,
        "renovation": "modern",
        "amenities": ["good view", "amenities nearby"]
    }
]

# ===== Language mapping =====
LANGUAGES = {
    "English": {
        "title": "🏠 Rental Assistant Bot – Milan Demo with LLM Parsing 🇮🇹",
        "district": "Preferred district/area (optional):",
        "price": "Price range? (e.g., 800–1500)",
        "furnished": "Do you need it furnished?",
        "pets": "Do you need pet-friendly?",
        "infrastructure": "What amenities should be nearby? (e.g., park, metro, supermarket)",
        "search": "🔍 Search listings",
        "restart": "🔄 Restart",
        "found": "Found {n} listings matching your filters.",
        "no_matches": "🚫 No matches found for your filters.",
        "save": "💾 Save as CSV",
        "saved": "Results saved as results.csv (current folder)",
        "invalid_price": "⚠️ Invalid price format. Use e.g. 800–1500"
    },
    "Italiano": {
        "title": "🏠 Assistente Affitti – Demo Milano con LLM Parsing 🇮🇹",
        "district": "Quartiere/area preferita (opzionale):",
        "price": "Fascia di prezzo? (es: 800–1500)",
        "furnished": "Deve essere arredato?",
        "pets": "Animali ammessi?",
        "infrastructure": "Cosa deve esserci vicino? (es: parco, metro, supermercato)",
        "search": "🔍 Cerca annunci",
        "restart": "🔄 Ricomincia",
        "found": "Trovati {n} annunci che corrispondono ai tuoi filtri.",
        "no_matches": "🚫 Nessun annuncio trovato con questi filtri.",
        "save": "💾 Salva come CSV",
        "saved": "Risultati salvati come results.csv (cartella corrente)",
        "invalid_price": "⚠️ Formato prezzo не valido. Es: 800–1500"
    }
}

st.set_page_config(page_title="Rental Assistant Bot 🇮🇹", layout="centered")

# ===== Language selection =====
language = st.radio("🌍 Language / Lingua", ["English", "Italiano"])
L = LANGUAGES[language]
st.title(L["title"])

# ===== Restart button with FULL reset =====
if st.button(L["restart"]):
    # Удаляем все ключи из session_state для полного сброса формы
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ===== Session state init =====
if "answers" not in st.session_state:
    st.session_state.answers = {}

with st.form("filter_form"):
    st.session_state.answers["district"] = st.text_input(
        L["district"], value=st.session_state.answers.get("district", "")
    )
    st.session_state.answers["price"] = st.text_input(
        L["price"], value=st.session_state.answers.get("price", "")
    )
    st.session_state.answers["furnished"] = st.text_input(
        L["furnished"], value=st.session_state.answers.get("furnished", "")
    )
    st.session_state.answers["pets"] = st.text_input(
        L["pets"], value=st.session_state.answers.get("pets", "")
    )
    st.session_state.answers["infrastructure"] = st.text_input(
        L["infrastructure"], value=st.session_state.answers.get("infrastructure", "")
    )
    submit = st.form_submit_button(L["search"])

if submit:
    price_input = st.session_state.answers.get("price", "800-1500").replace("€", "").replace(" ", "")
    try:
        if "–" in price_input:
            price_min, price_max = [int(x) for x in price_input.split("–")]
        else:
            price_min, price_max = [int(x) for x in price_input.split("-")]
    except Exception as e:
        st.error(L["invalid_price"])
        price_min, price_max = 0, 99999

    user_district = st.session_state.answers.get("district", "").strip().lower()
    user_furnished = st.session_state.answers.get("furnished", "").strip().lower()
    user_pets = st.session_state.answers.get("pets", "").strip().lower()
    user_infra = st.session_state.answers.get("infrastructure", "").strip().lower()

    filtered = []
    for res in DEMO_LISTINGS:
        # --- No AI call here! Data already in fields ---
        # Price filter
        try:
            res_price = int(res["price"].replace("€", "").replace("/month", "").replace(",", ""))
        except Exception:
            res_price = 0
        if not (price_min <= res_price <= price_max):
            continue
        # District filter
        if user_district and user_district not in ["-", "skip", "not important", "any","no", ""]:
            if user_district not in res["district"].lower():
                continue
        # Furnished filter
        if user_furnished and user_furnished not in ["-", "skip", "not important", "any","no", ""]:
            furnished_positive = ["yes", "si", "arredato", "furnished", "oui"]
            furnished_negative = ["no", "non", "unfurnished", "senza arredo"]
            if any(word in user_furnished for word in furnished_positive):
                if res["furnished"] is not True:
                    continue
            elif any(word in user_furnished for word in furnished_negative):
                if res["furnished"] is True:
                    continue
        # Pets filter
        if user_pets and user_pets not in ["-", "skip", "not important", "any", "no", ""]:
            pets_positive = ["yes", "si", "ammessi", "pet", "animali",]
            pets_negative = ["no", "non", "not allowed", "vietato"]
            if any(word in user_pets for word in pets_positive):
                if res["pets_allowed"] is not True:
                    continue
            elif any(word in user_pets for word in pets_negative):
                if res["pets_allowed"] is True:
                    continue
        # Infrastructure/amenities filter
        if user_infra and user_infra not in ["-", "skip", "not important", "any","no", "yes", ""]:
            keywords = [x.strip() for x in user_infra.replace(",", " ").split()]
            if len(keywords) > 0:
                amenities = [a.lower() for a in res.get("amenities", [])]
                if not all(any(kw in a for a in amenities) for kw in keywords):
                    continue
        filtered.append(res)

    if filtered:
        st.info(L["found"].format(n=len(filtered)))
        for r in filtered:
            st.markdown(
                f"""
**{r['title']} | {r['price']} | [Link]({r['url']})**

**District:** {r['district']} | **Floor:** {r['floor']}  
**Description:** {r['description']}  
**Furnished:** {'Yes' if r['furnished'] else 'No'}, **Pets allowed:** {'Yes' if r['pets_allowed'] else 'No'}, **Renovation:** {r['renovation'].capitalize()}  
**Amenities:** {", ".join(r.get('amenities', [])) if r.get('amenities') else '—'}
""")
        if st.button(L["save"]):
            df = pd.DataFrame(filtered)
            df.to_csv("results.csv", index=False)
            st.success(L["saved"])
    else:
        st.warning(L["no_matches"])

st.caption("Created for portfolio: Shows real LLM field extraction on rental listings. In production, parsing would be done live (see commented-out ai_parse_description function).")
