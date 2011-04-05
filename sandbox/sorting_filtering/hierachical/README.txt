init_sort - funkcja do uporządkowania danych przed rozpoczęciem przetwarzania. Musi być użyta, bo wiersze są pomieszane.

compare_obj_budg - funkcja używana w init_sort służąca do porównania dwóch obiektów według specyficznych kryteriów.

Algorytm:
1. Jeśli obiekt ob jest poziomu "a", "b", "c",  id := ob.idef
   w przeciwnym przypadku id := ob.parent
2. Podziel id na liczby i po kolei je porownoj(az jednemu zbraknie znaków).
3. Jesli id jednego z obiektow jest mniejsze, wtedy ten obiekt jest wiekszy (1.1.2 > 3.4).
   Zwroc wynik w zaleznosci, od tego kto jest wiekszy.
4. W przeciwnym wypadku, sprawdź, czy jeden z obiektów jest na wyższym poziomie. Jeśli tak, to jest on większy.
5. W przeciwnym wypadku(oba wiersze poziomu "d") sprawdź w dtx wartość x obu wierszy. Wiersz z mniejszym iksem jest większy
   ( 1-1-dt1 > 1-1-dt2 ).
   
Sortowanie hierarchiczne nie działa, bo nie wiem, na jakim poziomie dane mają być sortowane.
Założyłem, że mieszają się podzadania w zadaniach, czyli zadania nie zmieniają kolejności.
Myślę, że działa to tak, że:
gdy (d2.val > d1.val)
c1            c2
d1      --->  d2
c2            c1
d2            d1
Ale co zrobić, jeśli mam:
c1
d1
d2
to nie wiem, chociaż nie jestem pewien, czy taka sytuacja w ogóle może wystąpić.
swap_lev_c - zamienia c1 i c2 tak jak na zamieszczonym wyżej obrazku. Mogą być problemy, jeśli
jeden z c-nodów ma więcej dzieci niż drugi.

sort - dostosowana do takiego sortowania hierarchicznego wersja bubble_sorta

Żeby to działało, musisz skopiować plik z serwera z danymi projects/rawsalad/script/db/universal/budggofill.json
do katalogu z tym skryptem i nazwać obiekt, który tam jest jako data, a plik budggofill.json nazwać dejta.js.
