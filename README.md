# Routing Streamlit

Streamlit aplikace pro tvorbu matic vzdáleností na základě dat OpenStreetMap
a jejich využití při řešení úloh operačního výzkumu:

- **TSP** – problém obchodního cestujícího
- **SPP** – problém nejkratší cesty
- **CPP** – problém čínského listonoše

## Struktura projektu

```
app.py                          # úvodní stránka
pages/                          # jednotlivé kroky aplikace (multipage Streamlit)
src/
  distance_matrix.py            # stažení silniční sítě z OSM (osmnx) a výpočet matice vzdáleností
  models.py                     # LP/grafové modely: TSP, SPP, CPP
data/cache/                     # lokální cache stažených OSM dat (negitované)
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
