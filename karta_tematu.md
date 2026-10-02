---
share_link: https://share.note.sx/mdxqmhwe#9dalkcKZZG9oTSGt+Dqi/zjv8lvS1SslMGr78DAE6fY
share_updated: 2026-09-27T09:38:22+02:00
---
# Karta zgłoszenia tematu projektu

> **Instrukcja dla zespołu.** Skopiujcie ten plik do swojego repozytorium pod nazwą `karta-tematu.md`, wypełnijcie i zacommitujcie. Punkty 1–4 wypełniacie na pierwszych zajęciach (wpisujecie je też do arkusza). Całość — do kolejnego zjazdu (L3: 3.10, L2: 15.10). Zatwierdzenie tematu dostaniecie jako komentarz w repozytorium.
> 
> Usuńcie ten blok po wypełnieniu.

**Grupa: L3** 
**Data zgłoszenia: 3.10**

---

## 1. Skład zespołu

|Imię i nazwisko|Nr albumu|Rola w zespole|
|---|---|---|
|Wojciech Stanisławski|31830||
|Igor Chojan|32124||
|Gabriel Czapelski|31873||

Rola to nie stanowisko, tylko deklaracja, za co ta osoba odpowiada: dane, implementacja, ewaluacja, dokumentacja, koordynacja.

## 2. Tytuł projektu

**Po polsku: Znajdę czas szefie**

**Po angielsku: I will find time boss**

## 3. Problem

_Co system ma robić i dla kogo. Opis sytuacji, nie nazwy technologii. 3–5 zdań._

System ma w kilka minut układać tygodniowy grafik kurierów dla menedżera lokalu z dowozem, tak aby liczba osób na zmianie odpowiadała zapotrzebowaniu w każdej godzinie. Dziś menedżer układa grafik "z głowy", łącząc zmienne zapotrzebowanie (piątkowy wieczór vs wtorkowe popołudnie), uprawnienia kurierów (auto, skuter, ważne orzeczenie sanepidowskie i BHP) oraz dostępność i limity godzin (studenci, limity tygodniowe, 11 h odpoczynku). W szczytach brakuje ludzi, a w dołkach kurierzy stoją bezczynnie i generują koszt. Aplikacja przejmuje liczenie, a menedżer tylko zatwierdza lub poprawia wynik.

## 4. Dlaczego zwykły algorytm nie wystarczy

_Wskażcie jeden z trzech powodów omawianych na zajęciach i uzasadnijcie:_

- [ ] nie umiemy zapisać reguły krok po kroku
- [x] przepis istnieje, ale jest obliczeniowo za drogi
- [ ] reguł jest za dużo i zmieniają się w czasie

_Uzasadnienie, 2–3 zdania:_

Liczba możliwych grafików (kto, którego dnia, od której do której godziny) rośnie wykładniczo wraz z liczbą kurierów i godzin, więc sprawdzenie wszystkich jest niewykonalne. Szybki algorytm zachłanny układa grafik dzień po dniu i nie cofa wcześniejszych decyzji, dlatego zostawia braki w obsadzie, mimo że wolni kurierzy istnieją. Potrzebna jest metoda, która przeszukuje przestrzeń rozwiązań globalnie.

---

> Punkty poniżej wypełniacie do 3.10.

---

## 5. Technologia SI

- [ ] sieć neuronowa
- [ ] system ekspertowy / wnioskowanie regułowe
- [x] algorytm genetyczny
- [ ] klasyczne uczenie maszynowe
- [ ] inne:

_Dlaczego akurat ta technologia pasuje do tego problemu, 2–3 zdania:_

Grafik zapisujemy jako chromosom (dla każdego kuriera i dnia: wolne albo start i długość zmiany), a funkcja przystosowania karze za braki obsady, nadwyżki i naruszenia reguł, a nagradza równe obciążenie. GA przeszukuje przestrzeń globalnie, może startować od rozwiązania zachłannego i poprawiać je, a nie potrzebuje danych treningowych, których nie mamy.

## 6. Dane

|||
|---|---|
|Źródło|Dane syntetyczne z własnego generatora w Pythonie: kurierzy (pojazdy, daty ważności sanepidu i BHP, okna dostępności, limity godzin) oraz zapotrzebowanie (zamówienia na godzinę i dzień tygodnia)|
|Rozmiar i format|30 kurierów; zapotrzebowanie 7 dni × godziny otwarcia (np. 11–23); 10 instancji testowych z różnymi ziarnami losowości; pliki CSV (kurierzy.csv, zapotrzebowanie.csv)|
|Czy są już dostępne?|nie|
|Jeśli nie — plan pozyskania|Generator z parametrami i stałym ziarnem, żeby wyniki były powtarzalne. Zapotrzebowanie ma kształt typowy dla dowozu jedzenia: niski poziom w dzień, szczyt wieczorem (obiad i kolacja), wyższy w piątek i sobotę, plus losowy szum. Dane rzeczywiste nie są dostępne|

## 7. Stos technologiczny

_Język, biblioteki, środowisko uruchomieniowe. Pamiętajcie: wszystko ma działać na CPU, bez karty graficznej._

Python 3 w Google Colab (CPU), pandas i numpy, własna implementacja GA (ewentualnie DEAP), matplotlib do wykresów zbieżności i mapy pokrycia, ipywidgets do panelu "co jeśli" (suwaki: wydajność kuriera, udział aut, wzrost zamówień), openpyxl do eksportu grafiku do Excela.

## 8. Kryterium sukcesu

_Po czym poznamy, że projekt działa. Jaka metryka, jaki próg. Liczba, nie deklaracja._

Wszystko mierzone na 10 instancjach (ziarna 1–10), jako średnia:

- 100% ograniczeń twardych spełnionych w każdym grafiku (ważny sanepid i BHP w dniu zmiany, dostępność, limit tygodniowy, 11 h odpoczynku, zmiana 4–10 h, jedna dziennie),
- liczba brakujących godzin-kuriera w GA niższa niż w algorytmie zachłannym o co najmniej 30% (próg doprecyzujcie po zmierzeniu baseline'u, ale zapiszcie go przed końcowymi testami),
- pokrycie zapotrzebowania ≥ 98% godzin-kuriera,
- udział aut w szczycie ≥ 25% i rowerzystów ≤ 40% w każdej godzinie,
- czas generowania tygodniowego grafiku poniżej 60 s na CPU w Colabie dla 30 kurierów.

## 9. Zakres minimalny

_Co powstanie na pewno. To jest obietnica, z której będziecie rozliczeni._

- Generator danych syntetycznych kurierów i zapotrzebowanie z krzywych (lub awaryjnie syntetycznych),
- baseline: algorytm zachłanny,
- reprezentacja grafiku i funkcja przystosowania z regułami twardymi,
- działający algorytm genetyczny,
- porównanie GA z baseline'em na 10 instancjach, wykresy zbieżności i mapa pokrycia (obsada vs potrzeba),
- krótkie sprawozdanie z metrykami.

## 10. Zakres opcjonalny

_Co dorobicie, jeśli starczy czasu. Brak realizacji tej części nie obniża oceny._

- Optymalizator OR-Tools CP-SAT jako punkt odniesienia (optimum),
- ręczne korekty zmian z ponownym przeliczeniem pokrycia,
- alerty o wygasających dokumentach i eksport do Excela,
- panel "co jeśli" z suwakami (np. wzrost zamówień przed meczem lub świętem),
- profile zapotrzebowania (dzień powszedni, weekend, mecz, święto),
- test skalowania na większych instancjach.

## 11. Repozytorium

_Link: https://github.com/Glapso/I-will-find-time-boss/tree/main_

## 12. Główne ryzyko i plan awaryjny

_Co najprawdopodobniej pójdzie nie tak i co wtedy zrobicie._

Najbardziej prawdopodobne, że algorytm genetyczny nie pobije wyraźnie algorytmu zachłannego. Zachłanny jest szybki i na łatwych instancjach daje już dobre grafiki, a GA wymaga strojenia (rozmiar populacji, krzyżowanie, mutacja, wagi kar w funkcji przystosowania) i bez tego może zbiegać wolno albo utknąć w rozwiązaniach łamiących reguły.

Plan awaryjny:

- Populację początkową zasilamy rozwiązaniem zachłannym, więc GA nigdy nie wypada gorzej niż baseline, a tylko je poprawia.
- Jeśli różnica jest mała, zaostrzamy instancje testowe (zapotrzebowanie bliżej pojemności kurierów), bo tam przewaga przeszukiwania globalnego jest widoczna.
- Jeśli mimo to wynik jest słaby, rzetelnie raportujemy porównanie i analizujemy, dlaczego tak wyszło (to też jest wartościowy wniosek do sprawozdania), a punktem odniesienia dodajemy CP-SAT z zakresu opcjonalnego, żeby pokazać, jak daleko oba podejścia są od optimum.
- Zakres minimalny jest zaplanowany tak, żeby projekt dało się oddać nawet bez wyraźnej przewagi GA: liczy się działające rozwiązanie i uczciwy pomiar.

## 13. Podział pracy w czasie

|Etap|Kto|Szacowany czas|
|---|---|---|
|Dane i przygotowanie|||
|Implementacja|||
|Eksperymenty i ewaluacja|||
|Dokumentacja PL|||
|Dokumentacja EN|||
|Prezentacja|||
|**Razem na osobę**||**28–30 h**|

---

## Decyzja prowadzącego

_Wypełnia prowadzący — nie edytujcie tej sekcji._

- [ ] zatwierdzony
- [ ] do poprawy

**Uwagi:**
