# Routing Streamlit

🔗 **Nasazená aplikace:** [ksi-routing-app.streamlit.app](https://ksi-routing-app.streamlit.app/)

Streamlit aplikace pro tvorbu matic vzdáleností na základě dat OpenStreetMap
a jejich využití při řešení úloh operačního výzkumu:

- **TSP** – problém obchodního cestujícího
- **SPP** – problém nejkratší cesty
- **CPP** – problém čínského listonoše

## Struktura projektu

```
app.py                              # úvodní stránka
pages/
  1_Read_me.py                      # popis aplikace + formulář pro zpětnou vazbu
  2_Matice_vzdalenosti.py           # zadání bodů/oblasti a výpočet matice vzdáleností
src/
  distance_matrix.py                # stažení silniční sítě z OSM (osmnx) a výpočet matice vzdáleností
  models.py                         # LP/grafové modely: TSP, SPP, CPP
  ui.py                             # sdílené UI prvky (hlavička, patička, sidebar)
data/cache/                         # lokální cache stažených OSM dat (negitované)
```

## Instalace

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Spuštění

```powershell
streamlit run app.py
```

## Zpětná vazba

Nápady, připomínky nebo nahlášení chyb lze zadat přes formulář:
[Formulář pro zpětnou vazbu](https://forms.cloud.microsoft/e/KjGdWCZhE4)

(stejný odkaz je i přímo v aplikaci, na stránce „Read me")

## Branch strategie

- **`main`** – deploy/produkční větev. Nasazuje se z ní na Streamlit Cloud.
  Obsahuje jen funkční, odzkoušené části aplikace.
- **`dev`** – pracovní větev, kde vzniká veškerý rozpracovaný kód (včetně
  nedokončených solver stránek pro TSP/SPP/CPP). Běžná práce probíhá zde.

Hotové části se z `dev` do `main` přenášejí po jednotlivých souborech
(`git checkout dev -- <soubor>`), ne celým sloučením větví – `main` tak
nikdy neobsahuje nedokončenou/neotestovanou funkčnost.
