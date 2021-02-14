**Reality scraper**

Aplikace pro získávání informací o jednotlivých inzerátech z portálu bezrealitky.cz. Výstupem aplikace je vyrenderovaný report s grafy obsahující základní přehled - průměrnou cenu za m², strukturu a počet nabídek v jednotlivých regionech. Data se následně uloží do sqlite pro sledování historických vývojů cen. 


Struktura repositáře:
- config: obsahuje základní konfiguraci a sql dotazy pro práci s daty
- output: vyrenderovaný html report, sqlite db a složka tmp pro uložení png pro report
- python: obsahuje scraper a testy
- templates: html šablona pro generování reportu


Aplikace se spouští přes python/scraper/main.py.

Ukázka vyrenderovaného reportu: [report](http://htmlpreview.github.io/?https://github.com/peturami/realty_scraper/blob/master/output/report.html)
