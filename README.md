# pine-v6-forward-validation

## Projektzweck

Dieses Repository dient als Grundlage zur Umsetzung und Validierung von Handelsstrategien, die ursprünglich in *Pine Script v6* geschrieben wurden. Die Logik der Strategien und Indikatoren wird in Python reproduziert, damit sowohl Paritätstests als auch robuste Walk‑Forward‑Analysen möglich sind. Ziel ist es, künftige Strategiemodule wie **AMLR‑X**, **IAX**, **IVSF** und **ELC** reproduzierbar zu testen, ohne auf die TradingView‑Plattform angewiesen zu sein. Neben der Signalberechnung stellt das Projekt eine Infrastruktur für Datenbeschaffung, Resampling, Kostenmodelle, Walk‑Forward‑Splits und Reporting bereit.

## Installationsanleitung

1. Repository auschecken:

   ```bash
   git clone <REPOSITORY-URL> pine-v6-forward-validation
   cd pine-v6-forward-validation
   ```

2. Virtuelle Umgebung erstellen und aktivieren (Beispiel für Unix‑Shell):

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   Unter Windows PowerShell:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Abhängigkeiten installieren. Für die Entwicklung wird der `dev`‑Extrasatz empfohlen:

   ```bash
   python -m pip install --upgrade pip
   pip install -e ".[dev]"
   ```

4. Tests ausführen, um sicherzustellen, dass alles korrekt installiert ist:

   ```bash
   pytest
   ```

## Datenformat

Die Module dieses Projekts erwarten Rohdaten im CSV‑Format mit folgenden Spalten (in genau dieser Reihenfolge):

```
timestamp,open,high,low,close,volume
```

Der Zeitstempel (`timestamp`) muss entweder als Unix‑Epoch (in Millisekunden) oder als ISO‑8601‑String angegeben werden. Alle Zeitangaben werden intern nach UTC normalisiert. Es dürfen keine fehlenden Werte vorkommen; High/Low müssen jeweils die höchsten bzw. niedrigsten Werte innerhalb der Periode sein.

## CLI‑Beispiele

Mit dem Skript `run_walk_forward.py` können einfache Walk‑Forward‑Analysen erstellt werden. Es kombiniert Datenladung, Signalerzeugung, Forward‑Return‑Berechnung und Berichterstellung. Ein Beispielaufruf:

```bash
python scripts/run_walk_forward.py \
  --data data/raw/BTCUSDT_5m.csv \
  --strategy amlrx \
  --config configs/amlrx_v0_1.yaml \
  --out reports/walk_forward/BTCUSDT_amlrx.md \
  --horizons 3 5 10
```

In diesem Beispiel wird die Konfigurationsdatei `configs/amlrx_v0_1.yaml` geladen, die Daten werden aus der angegebenen CSV gelesen und auf Grundlage der ausgewählten Strategie verarbeitet. Der Report wird als Markdown unter dem angegebenen Pfad gespeichert. Die Parameter `--horizons` legen fest, für welche Anzahl an Balken die Forward‑Returns berechnet werden (hier 3, 5 und 10).

## Validierungsregeln

Um sicherzustellen, dass Pine‑Script‑Logik korrekt übertragen wird und keine späteren Balken zur Berechnung herangezogen werden (Future‑Leak), gelten folgende Regeln:

1. **Rolling‑Funktionen:** Nur rückwärtsgerichtete Fenster. Es dürfen keine centered windows verwendet werden.
2. **HTF‑Daten:** Höherfrequente Daten dürfen erst als bestätigt gelten, wenn die Bar abgeschlossen ist (`confirmed_only=True`).
3. **Zeitstempel:** Pine‑Export‑Zeitstempel müssen auf UTC normalisiert werden, damit Vergleichbarkeit gewährleistet ist.
4. **Signal/Score/State:** Unterschiede zwischen Pine und Python müssen explizit ausgewiesen werden.
5. **Unsafe‑Modus:** Darf nur zu Debug‑Zwecken aktiviert werden und muss klar gekennzeichnet sein.

## Verzeichnisstruktur

Die wichtigsten Verzeichnisse und Dateien:

```
configs/        # YAML‑Konfigurationen für Strategien und Symbolsets
data/
  raw/          # Rohdaten (z. B. heruntergeladene Bybit‑CSV)
  processed/    # Vorverarbeitete Daten
  pine_exports/ # Pine‑CSV‑Exporte zum Paritätstest
src/
  data/         # Loader und Resampler
  engine/       # Signal‑ und Trade‑Engine
  pine_parity/  # Paritätstests und MTF‑Logik
  reports/      # Report‑Writer
  strategies/   # Strategiemodule (AMLX, IAX, IVSF, ELC)
scripts/        # CLI‑Skripte
tests/          # Unittests
reports/        # Generierte Auswertungen
```

## Minimaler Testlauf

Nach erfolgreicher Installation kann mit folgendem Befehl ein Basistest durchgeführt werden:

```bash
pytest
```

Alle Tests sollten ohne Fehler durchlaufen. Dies prüft u. a. den YAML‑Konfig‑Loader, die Signal‑ und Trade‑Engines sowie den Report‑Generator.

## Roadmap‑Versionen

Dieses Projekt wird iterativ erweitert. Die wichtigsten Meilensteine sind:

| Version | Inhalt |
|--------:|:-------|
| **v0.1.0** | Core‑CLI, YAML‑Konfig‑Loader, CSV‑Loader, Forward‑Returns, Summary‑Report |
| **v0.2.0** | Pine‑Parity‑Basis (Rolling/MTF) |
| **v0.3.0** | AMLR‑X/IAX Strategiemodule |
| **v0.4.0** | Trade‑Engine inkl. Kostenmodell |
| **v0.5.0** | Walk‑Forward‑Engine |
| **v0.6.0** | Robustness & Negative Controls |
| **v0.7.0** | Optimizer |
| **v0.8.0** | Forward Shadow Mode |
| **v0.9.0** | Backtrader Replay |
| **v1.0.0** | Stabler Release‑Gate |

## Anti‑Future‑Leak‑Grundsätze

Eine zentrale Anforderung an dieses Projekt ist, dass keine Informationen aus zukünftigen Balken für die Signalberechnung oder Parameteroptimierung verwendet werden. Dies betrifft insbesondere:

- **Lookahead:** Es dürfen keine Preisdaten aus der Zukunft in die Berechnung einfließen. MTF‑Daten müssen um eine Bar verschoben werden, um nur bestätigte Informationen zu nutzen.
- **Centered Windows:** Rolling‑Fenster müssen rückwärtsgerichtet sein und dürfen nicht mittig um den aktuellen Punkt liegen.
- **Walk‑Forward:** Parameteroptimierung muss strikt vom Testfenster getrennt sein. Es dürfen keine Testdaten zur Optimierung verwendet werden.

Durch konsequente Anwendung dieser Grundsätze soll sichergestellt werden, dass die Ergebnisse reproduzierbar sind und nicht durch Leckagen verfälscht werden.