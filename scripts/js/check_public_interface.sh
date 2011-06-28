#!/bin/sh

cd ../../src/rawsalad/site_media/js/
LIST=`ls *js`

for f in $LIST; do
    QUERY=`grep 'that\..*\ =\ fun' $f | sed 's/\ *that\.//;s/\ =\ .*//'`
    echo ''
    echo ''
    echo '==============================' $f '=============================='

    for q in $QUERY; do 
        MODULE=`echo $f | awk -F\. '{ print $1 }'`
        echo ''
        echo $q; 
        echo '---------------------------------------------------------------------------'; 
        grep -rn $MODULE\.$q *js; 
    done
done
