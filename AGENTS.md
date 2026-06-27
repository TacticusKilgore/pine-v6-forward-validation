# Richtlinien für Agenten

Dieses Dokument definiert die Arbeitsgrundsätze für Entwickler und Automatisierungstools (Agents), die an diesem Repository arbeiten. Ziel ist es, konsistente, nachvollziehbare und reproduzierbare Änderungen sicherzustellen, ohne die Stabilität der Hauptentwicklungslinie zu gefährden.

## Diagnose vor Patch

Bevor Änderungen implementiert werden, muss der Agent das Problem oder die Anforderung nachvollziehbar identifizieren. Dazu gehört das Reproduzieren des Fehlers (sofern vorhanden), das Lesen der relevanten Konfigurationen und das Prüfen bestehender Tests. Änderungen ohne vorherige Diagnose führen oft zu Nebenwirkungen und sollten vermieden werden.

## Tests vor Abschluss

Jede neue Funktionalität oder Fehlerbehebung muss von entsprechenden Unit‑Tests begleitet werden. Diese Tests sollen sowohl den erwarteten Erfolgspfad als auch relevante Fehlerszenarien abdecken. Erst wenn alle Tests bestehen und keine Regressionen auftreten, dürfen Änderungen als abgeschlossen gelten.

## Keine Future‑Leaks

Ein zentrales Ziel dieses Projekts ist es, **keine** zukünftigen Informationen zu verwenden, um Signale oder Parameter zu berechnen. Dazu zählen z. B. Lookahead‑Fenster, unverschobene MTF‑Daten oder Optimierungen, die Testdaten einbeziehen. Agenten müssen sicherstellen, dass die Implementierung diesem Prinzip strikt folgt.

## Trennung von Pine‑Parity und Trade‑Engine

Die logische Abbildung von Pine‑Indikatoren (**Parity**) sollte strikt von der Ausführung der Trades (Trade‑Engine) getrennt sein. Parity‑Module dürfen nur numerische Gleichheit und Signalkonsistenz prüfen, während die Trade‑Engine Entry/Exit‑Regeln, Stops, Take Profits und das Kostenmodell behandelt. Eine Vermischung erschwert das Testen und führt zu schwer nachverfolgbaren Fehlern.

## Strategie‑Module separat von Optimierung

Strategien (wie AMLR‑X oder IAX) definieren Logik für Signale und Scores. Die Optimierung dieser Parameter darf erst in nachgelagerten Modulen (Optimizer) stattfinden. Agenten dürfen keine Parameteroptimierung in Strategiemodulen oder Signalerzeugung verstecken.

## Reproduzierbare Reports

Reports müssen so erzeugt werden, dass sie jederzeit aus denselben Eingaben reproduzierbar sind. Dazu gehört die Speicherung aller relevanten Parameter, die Datumsangaben des Trainings- und Testzeitraums sowie die exakte Konfiguration der verwendeten Strategie. Reports dürfen weder von zufälligen Variablen abhängen noch heimlich auf andere Datenquellen zugreifen.

## CI muss grün bleiben

Der Hauptbranch (`main`) muss jederzeit fehlerfrei baubar und testbar sein. Alle Pull Requests müssen den CI‑Status auf Grün halten, bevor sie zusammengeführt werden. Schlägt der CI fehl, so sind die entsprechenden Probleme zeitnah zu beheben. Langfristige Arbeitszweige sollten die CI‑Konfiguration spiegeln, um böse Überraschungen bei der Integration zu vermeiden.

## Branching und Commits

* **Stabilität:** Die `main`‑Branch bleibt stabil und enthält nur getesteten Code.
* **Entwicklung:** Neue Features oder Korrekturen werden in separaten Branches entwickelt (z. B. `dev/feature-name`).
* **Atomare Commits:** Jeder Commit sollte eine logisch zusammenhängende Änderung enthalten und ausreichend beschreibend sein. Nutze Commit‑Nachrichten, um Kontext zu geben.

Durch das Einhalten dieser Regeln wird sichergestellt, dass Arbeiten an diesem Projekt konsistent und nachvollziehbar bleiben und gleichzeitig die langfristigen Ziele von Parität und Forward‑Validation gewahrt werden.