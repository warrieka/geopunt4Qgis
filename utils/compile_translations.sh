#!/bin/bash
pylupdate4 ../i18n/geopunt4qgis_ts.pro
lrelease ../i18n/*.ts

OLD='images\/logogeopunt4Q.png'
NEW='..\/images\/logogeopunt4Q.png'

TEMPNL=$RANDOM
TEMPEN=$RANDOM

markdown ../README.md > ../i18n/about-en.html
markdown ../README_NL.md > ../i18n/about-nl.html

sed "s/$OLD/$NEW/g" ../i18n/about-en.html > ../i18n/$TEMPEN
cat ../i18n/$TEMPEN > ../i18n/about-en.html
rm ../i18n/$TEMPEN

sed "s/$OLD/$NEW/g" ../i18n/about-nl.html > ../i18n/$TEMPNL
cat ../i18n/$TEMPNL > ../i18n/about-nl.html
rm ../i18n/$TEMPNL