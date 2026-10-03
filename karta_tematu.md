**Grupa: L3** 
**Data zgłoszenia: 3.10**

---

## 1. Skład zespołu

|||
|---|---|
|Imię i nazwisko|Nr albumu|Rola w zespole|
|Wojciech Stanisławski|31830|koordynacja, dokumentacja|
|Igor Chojan|32124|implementacja|
|Gabriel Czapelski|31873|dane,ewaluacja|

Rola to nie stanowisko, tylko deklaracja, za co ta osoba odpowiada: dane, implementacja, ewaluacja, dokumentacja, koordynacja.

## 2. Tytuł projektu

**Po polsku: Znajdę czas szefie**

**Po angielsku: I will find time boss**

## 3. Problem

_Co system ma robić i dla kogo. Opis sytuacji, nie nazwy technologii. 3–5 zdań._

System ma w kilka minut układać tygodniowy grafik kurierów dla menedżera lokalu z dowozem, tak aby liczba osób na zmianie odpowiadała zapotrzebowaniu w każdej godzinie. Dziś menedżer układa grafik "z głowy", łącząc zmienne zapotrzebowanie , uprawnienia kurierów oraz dostępność i limity godzin. W szczytach brakuje ludzi, a w dołkach kurierzy stoją bezczynnie i generują koszt. Aplikacja przejmuje liczenie, a menedżer tylko zatwierdza lub poprawia wynik.

## 4. Dlaczego zwykły algorytm nie wystarczy

_Wskażcie jeden z trzech powodów omawianych na zajęciach i uzasadnijcie:_

- [ ] nie umiemy zapisać reguły krok po kroku
- [x] przepis istnieje, ale jest obliczeniowo za drogi
- [ ] reguł jest za dużo i zmieniają się w czasie

_Uzasadnienie, 2–3 zdania:_

Liczba możliwych grafików (kto, którego dnia, od której do której godziny) rośnie wykładniczo wraz z liczbą kurierów i godzin, więc sprawdzenie wszystkich jest niewykonalne. Szybki algorytm zachłanny układa grafik dzień po dniu i nie cofa wcześniejszych decyzji, dlatego zostawia braki w obsadzie, mimo że wolni kurierzy istnieją. Potrzebna jest metoda, która przeszukuje przestrzeń rozwiązań globalnie.

---

---

## 5. Technologia SI

- [ ] sieć neuronowa
- [ ] system ekspertowy / wnioskowanie regułowe
- [x] algorytm genetyczny
- [ ] klasyczne uczenie maszynowe
- [ ] inne:

_Dlaczego akurat ta technologia pasuje do tego problemu, 2–3 zdania:_

Grafik zapisujemy jako chromosom (dla każdego kuriera i dnia: wolne albo start i długość zmiany), a funkcja przystosowania karze za braki obsady, nadwyżki i naruszenia reguł, a nagradza równe obciążenie. Model przeszukuje przestrzeń globalnie, może startować od rozwiązania zachłannego i poprawiać je.

## 6. Dane

|||
|---|---|
|Źródło|Dane syntetyczne z własnego generatora: kurierzy (pojazdy, daty ważności badań sanepidu i BHP, okna dostępności, limity godzin) oraz zapotrzebowanie (zamówienia na godzinę i dzień tygodnia)|
|Rozmiar i format|30 kurierów; zapotrzebowanie 7 dni × godziny otwarcia (np. 11–23); 10 instancji testowych z różnymi ziarnami losowości; pliki CSV |
|Czy są już dostępne?|nie|
|Jeśli nie — plan pozyskania|Generator z parametrami i stałym ziarnem, żeby wyniki były powtarzalne. Zapotrzebowanie ma kształt typowy dla dowozu jedzenia: niski poziom w dzień, szczyt wieczorem, wyższy w piątek i sobotę, plus losowy szum. Dane rzeczywiste nie są dostępne|

## 7. Stos technologiczny

Python 3 w Google Colab (CPU), pandas i numpy

## 8. Kryterium sukcesu

Wszystko mierzone na 10 instancjach, jako średnia:

- 100% ograniczeń twardych spełnionych w każdym grafiku (ważny sanepid i BHP w dniu zmiany, dostępność, limit tygodniowy, 11 h odpoczynku, zmiana 4–10 h, jedna dziennie)
- liczba brakujących godzin-kuriera w GA niższa niż w algorytmie zachłannym o co najmniej 30%
- pokrycie zapotrzebowania ≥ 98% godzin-kuriera
- udział aut w szczycie ≥ 25% i rowerzystów ≤ 40% w każdej godzinie
- czas generowania tygodniowego grafiku poniżej 60 s na CPU w Colabie dla 30 kurierów.

## 9. Zakres minimalny

_Co powstanie na pewno. To jest obietnica, z której będziecie rozliczeni._

- Generator danych syntetycznych kurierów i zapotrzebowanie,
- reprezentacja grafiku i funkcja przystosowania z regułami twardymi,
- działający algorytm genetyczny,
- działający algorytm zachłanny
- porównanie algorytmu genetycznego z algorytmem zachłannym
- dokumentacja

## 10. Zakres opcjonalny

_Co dorobicie, jeśli starczy czasu. Brak realizacji tej części nie obniża oceny._

- ręczne korekty zmian z ponownym przeliczeniem pokrycia,
- eksport do Excela,
- panel "co jeśli" z suwakami (np. wzrost zamówień przed meczem lub świętem),
- profile zapotrzebowania (dzień powszedni, weekend, mecz, święto),
- test skalowania na większych instancjach.

## 11. Repozytorium

_Link: https://github.com/Glapso/I-will-find-time-boss/tree/main_

## 12. Główne ryzyko i plan awaryjny

_Co najprawdopodobniej pójdzie nie tak i co wtedy zrobicie._

Najbardziej prawdopodobne, że algorytm genetyczny nie pobije wyraźnie algorytmu zachłannego, bo wymaga strojenia, a na łatwych danych zachłanny daje już dobry wynik. Wtedy wystartujemy GA od rozwiązania zachłannego, zaostrzymy dane testowe i rzetelnie opiszemy w sprawozdaniu, jak wyszło i dlaczego.

## 13. Podział pracy w czasie

|Etap|Kto|Szacowany czas|
|---|---|---|
|Dane i przygotowanie|Gabriel Czapelski|12h|
|Implementacja|Igor Chojan|28h|
|Eksperymenty i ewaluacja|Gabriel Czapelski|16h|
|Dokumentacja PL|Wojciech Stanisławski|16h|
|Dokumentacja EN|Wojciech Stanisławski|8h|
|Prezentacja|Wojciech Stanisławski|8h|
|**Razem na osobę**||**28–30 h**|

---

## Decyzja prowadzącego

_Wypełnia prowadzący — nie edytujcie tej sekcji._

- [ ] zatwierdzony
- [ ] do poprawy

**Uwagi:**
