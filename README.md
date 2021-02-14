**Reality scraper**

Aplikace pro získávání informací o jednotlivých inzerátech z portálu bezrealitky.cz. Výstupem aplikace je vyrenderovaný report s grafy obsahující základní přehled - průměrnou cenu za m², strukturu a počet nabídek v jednotlivých regionech. Data se následně uloží do sqlite pro sledování historických vývojů cen. 


Struktura repositáře:
- config: obsahuje základní konfiguraci a sql dotazy pro práci s daty
- output: vyrenderovaný html report, sqlite db
- scraper: python scraper
- templates: html šablona pro generování reportu
- tmp: grafy do reportu


Aplikace se spouští přes scraper/main.py. 
