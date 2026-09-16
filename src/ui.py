import streamlit as st

def render_header():
    """Zobrazí hlavičku appky – logo fakulty a název aplikace."""
    st.image("assets/CZU_PEF_barva_RGB.png", width=250)   
    st.title("ξ PEF Routing app")


def render_steps_sidebar():
    """Zobrazí v postranním panelu stručný přehled kroků aplikace."""
    st.sidebar.markdown(
        """
        **Postup práce s aplikací:**

        1. Zadejte body zájmu (souřadnice)
        2. Zvolte oblast mapy a typ sítě
        3. Vygenerujte matici vzdáleností
        4. Vyřešte vybraný model (SPP / TSP / CPP)
        """
    )


def render_footer():
    """Zobrazí patičku appky – logo fakulty a název katedry."""
    st.divider()
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("assets/CZU_PEF_barva_RGB.png", width=150)
    with col2:
        st.write("Katedra systémového inženýrství, Provozně ekonomická fakulta ČZU v Praze")
    st.caption("© Tereza Sedlářová Nehézová 2026")