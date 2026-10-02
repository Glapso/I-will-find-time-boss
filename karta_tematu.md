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
|Źródło||
|Rozmiar i format||
|Czy są już dostępne?|tak / nie|
|Jeśli nie — plan pozyskania||

## 7. Stos technologiczny

_Język, biblioteki, środowisko uruchomieniowe. Pamiętajcie: wszystko ma działać na CPU, bez karty graficznej._

## 8. Kryterium sukcesu

_Po czym poznamy, że projekt działa. Jaka metryka, jaki próg. Liczba, nie deklaracja._

## 9. Zakres minimalny

_Co powstanie na pewno. To jest obietnica, z której będziecie rozliczeni._

## 10. Zakres opcjonalny

_Co dorobicie, jeśli starczy czasu. Brak realizacji tej części nie obniża oceny._

## 11. Repozytorium

_Link:_

## 12. Główne ryzyko i plan awaryjny

_Co najprawdopodobniej pójdzie nie tak i co wtedy zrobicie._

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
