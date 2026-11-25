# Źródła stawek w cenniku

Stawki w pliku `cennik.json` to średnie arytmetyczne z publicznych cenników polskich drukarni,
punktów ksero, hurtowni papieru i studiów graficznych (stan na listopad 2026).
Wszystkie kwoty są netto. Ceny podane brutto przeliczono na netto, dzieląc przez 1,23.
Cennik jest przykładowy i nie odzwierciedla stawek żadnego konkretnego studia.

## Druk cyfrowy SRA3 (zł za arkusz)

| Próg | Źródło | 4+0 | 4+4 | 1+0 | 1+1 |
| --- | --- | --- | --- | --- | --- |
| od 1 ark. | drukland.pl (50-99) | 4,20 | 8,40 | 0,70 | 1,25 |
| | megraf.pl (51-100) | 1,60 | 2,50 | | |
| | printon.pl (41-80) | 2,20 | | 0,70 | 1,40* |
| | **średnia** | **2,67** | **5,45** | **0,70** | **1,33** |
| od 100 ark. | drukland.pl (100-249) | 3,90 | 7,80 | 0,70 | 1,25 |
| | megraf.pl (101-300) | 1,20 | 2,00 | | |
| | printon.pl (81-250) | 1,70 | | 0,60 | 1,20* |
| | **średnia** | **2,27** | **4,90** | **0,65** | **1,23** |
| od 500 ark. | drukland.pl (500+) | 1,20 | 2,40 | 0,45 | 0,77 |
| | megraf.pl (500+) | 0,80 | 1,30 | | |
| | printon.pl (501-1000) | 1,10 | | 0,40 | 0,80* |
| | **średnia** | **1,03** | **1,85** | **0,43** | **0,79** |

\* printon.pl podaje tylko druk jednostronny; dla 1+1 przyjęto dwukrotność stawki 1+0.

## Papier (zł za arkusz SRA3)

| Papier | Źródła i ceny netto | Średnia |
| --- | --- | --- |
| offset 80 g | drukujcyfrowo.pl 0,29 | 0,29 |
| kreda 130 g | netuno.pl 0,25; drukarniatrojka.pl 0,40; allegro.pl (500 ark.) 0,18 | 0,28 |
| kreda 170 g | netuno.pl 0,32; drukarniatrojka.pl 0,60; allegro.pl (1000 ark.) 0,29 | 0,40 |
| kreda 300 g | allegro.pl (200 ark.) 0,44; antalis.pl Color Copy 0,73 | 0,58 |
| kreda 350 g | netuno.pl 0,64; drukarniatrojka.pl 1,20 | 0,92 |
| Clairefontaine DCP 160 g | bruneau.lu: 22,95 EUR za 250 ark. | 0,09 EUR |
| Clairefontaine DCP 250 g | bruneau.be: 20,50 EUR za 125 ark. | 0,16 EUR |

Papiery DCP kupowane są u dystrybutora z cenami w euro, dlatego aplikacja przelicza je po kursie NBP.

## Oprawa (zł za egzemplarz)

| Oprawa | Źródła | Średnia |
| --- | --- | --- |
| zszywka | ekspresowa-drukarnia.pl 0,20; drukarniapro.pl 0,10 | 0,15 |
| klejona | fabryka-kopii.pl 6,50; printprint.pl 5,00; gutenberg-drukarnia.pl 5,69; drukarniapro.pl 0,85 | 4,51 |
| szyta nićmi | klejona + średnia dopłata za szycie: drukujsam.pl 0,73; drukksiazek24.pl 0,64 | 5,20 |

## Zakres stron dla opraw

| Oprawa | Źródła | Przyjęto |
| --- | --- | --- |
| zszywka | sowadruk.pl 8-120 stron; drukksiazek.pl 8-80 stron | 8-100 |
| klejona | drukksiazek24.pl (oprawa miękka) 32-800 stron | 32-800 |
| szyta nićmi | drukksiazek24.pl (szyto-klejona) 48-800 stron | 48-800 |

## Uszlachetnienia (zł za arkusz SRA3, jedna strona)

| Uszlachetnienie | Źródła | Średnia |
| --- | --- | --- |
| folia mat/błysk | drukujcyfrowo.pl 1,21; megraf.pl 0,30; megakop.pl 0,60; drukland.pl 2,65; drukarniatrojka.pl 2,00 | 1,35 |
| lakier UV wybiórczy | agi.net.pl 0,60 za arkusz + 100 zł przygotowania | 0,60 + 100 |

## Skład DTP (zł za stronę)

grafpa.pl 20-80 (przyjęto 50); sklad-tekstu.pl 15-30 (22,50); artsdesign.pl od 30; projektgraficzny.com od 50;
ksiazki-historia.pl od 25. Średnia: **35,50 zł**.

## Założenia własne

| Parametr | Wartość | Uzasadnienie |
| --- | --- | --- |
| przygotowanie zlecenia | 30 zł | minimalne zamówienie: drukujcyfrowo.pl 20 zł, karlen.pl 30 zł, vicop.pl 40 zł |
| naddatek | 5% | zapas arkuszy na próby i odpady przy druku cyfrowym |
| marża | 30% | założenie do edycji w cenniku |
| VAT | 23% | stawka podstawowa |
| kurs EUR awaryjny | 4,46 zł | kurs średni NBP z 24.11.2026 (4,4633 zł); używany tylko, gdy API NBP nie odpowiada |

Liczbę użytków na arkuszu SRA3 przyjęto według standardowej impozycji ze spadami:
A3: 1, A4: 2, A5: 4, A6: 8, DL: 6, wizytówka 90 x 50 mm: 21.

## Znane ograniczenia modelu

- Model zakłada druk cyfrowy. Przy dużych nakładach (powyżej ok. 1000 egz.) tańszy jest offset.
- Okładka jest drukowana na tym samym papierze co środek publikacji.
- Na granicy progu ilościowego cena może spaść skokowo, np. 499 arkuszy kosztuje więcej niż 500.
