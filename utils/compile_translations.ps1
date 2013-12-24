C:\OSGeo4W\bin\pylupdate4.exe ..\i18n\geopunt4qgis_ts.pro
Get-ChildItem  ..\i18n\*.ts | foreach {C:\OSGeo4W\bin\lrelease.exe $_.FullName  }

[string]$OLD = 'images/logogeopunt4Q.png'
[string]$NEW = '../images/logogeopunt4Q.png'

[string]$TEMPEN = "$(Get-Random)" + ".txt"
[string]$TEMPNL = "$(Get-Random)" + ".txt"

#install markdown from https://pypi.python.org/pypi/Markdown/2.3.1 -> adapt to your python path
C:\Python26\ArcGIS10.0\python -m markdown.__main__ ../README.md > $TEMPEN
C:\Python26\ArcGIS10.0\python -m markdown.__main__ ../README_NL.md > $TEMPNL

echo '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd"><html><head><meta name="qrichtext" content="1" /><style type="text/css">p, li { white-space: pre-wrap; } </style></head> <body style=" font-size:9pt; font-weight:400; font-style:normal;">' > ../i18n/about-en.html 
(gc $TEMPEN) -replace $OLD, $NEW >> ../i18n/about-en.html
echo '</body></html>' >> ../i18n/about-en.html
rm $TEMPEN

echo '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd"><html><head><meta name="qrichtext" content="1" /><style type="text/css">p, li { white-space: pre-wrap; } </style></head> <body style=" font-size:9pt; font-weight:400; font-style:normal;">' > ../i18n/about-nl.html 
(gc $TEMPNL) -replace $OLD, $NEW >> ../i18n/about-nl.html 
echo '</body></html>' >> ../i18n/about-nl.html
rm $TEMPNL