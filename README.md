# Abschlussprojekt_Mechanismus

1. Einleitung
Das Ziel dieses Projekts ist die Entwicklung einer interaktiven Mechanismus-Simulation, die die Bewegung von Gelenken und Stäben in einem mechanischen System berechnet und visualisiert.
Diese Anwendung richtet sich insbesondere an Ingenieure, Studierende und Technikbegeisterte, die Kinematik und Mechanismen analysieren möchten.

Funktionalitäten der Simulation:
- Berechnung der Gelenkpositionen in Echtzeit
- Optimierung der Stablängen für eine präzise Bewegung
- Dynamische Visualisierung der Mechanik in einer grafischen Oberfläche (GUI)
- Möglichkeit, Mechanismen zu speichern und erneut zu laden
- Export der Simulation als GIF für Präsentationen oder Analysen

2. Projektstruktur
Das Projekt ist modular aufgebaut und besteht aus vier Hauptkomponenten, die jeweils eine spezifische Aufgabe übernehmen:
´
main.py (Hauptdatei inklusive UI)
mechanism.py: (Mechansimus Logik)
animation.py: (Animation und Visualisierung)
point.py (gelenk logik)

4. Funktionsweise – Umsetzung der Mindestanforderungen
Das Programm bietet eine vollständige Mechanismussimulation, die in folgenden Schritten funktioniert:

Bestehenden Mechanismus laden oder neuen Mechanismus erstellen:
Der Nutzer erstellt in der grafischen Benutzeroberfläche einen Mechanismus, indem er Gelenke und Stäbe selbst anordnet und definiert.

Berechnung der Gelenkpositionen:
Die Mechanism-Klasse führt eine kinematische Analyse durch und berechnet optimale Stablängen sowie die Bewegungsabläufe der Gelenke.

Simulation der Bewegung:
Die Simulation-Klasse nutzt die Berechnungen und führt eine Echtzeit-Simulation der Mechanik durch. 

Stückliste lässt sich nach laden der Gelenke nd Verbindungen direkt herrunterladen.
Gif Speicherung und Animation erfolgt nach einer kompleetten Kurbelbewegung.
CSV-Datei der Bankurve läasst sich nach stoppen der animation herrunterladen.

5. Erweiterungen
Neben den Kernfunktionen wurden einige Erweiterungen implementiert oder sind in Planung:

- GIF-Erstellung: Die 'Simulation'-Klasse kann ein animiertes GIF der Mechanismusbewegung generieren und speichern.
- Dynamische Anpassung der Mechanismusparameter: Änderung von Längen, Gelenkpositionen und Verbindungen während der Simulation.
- einstellbare Geschwindigkeit
- Stücklisten der benötigetn Gleider inklusive speicherung.
- Verbesserte Speicherfunktion: Möglichkeit, verschiedene Simulationsstände zu speichern und zwischen ihnen zu wechseln.


6. Fazit
Dieses Projekt demonstriert, wie kinematische Mechanismen interaktiv simuliert, analysiert und optimiert werden können. Die Software bietet nicht nur eine realitätsnahe Bewegungssimulation, sondern auch eine benutzerfreundliche Oberfläche zur dynamischen Anpassung mechanischer Systeme.

7. Persönliche Meinung
Sinnvolles Projekt mit bezug zum Studium. Zeitintensiv aber viel gelernt und Spaß gehabt.