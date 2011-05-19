for f in *js; do echo $f; grep 'that\..*{$' $f | sed 's/^\ *that\.//;s/\ =\ function//;s/\ {//'; done
