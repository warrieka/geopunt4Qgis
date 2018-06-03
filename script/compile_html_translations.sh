#!/bin/bash

echo '<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="qrichtext" content="1" /><style type="text/css">p, li { white-space: pre-wrap; } </style></head> <body style=" font-size:9pt; font-weight:400; font-style:normal;">' > i18n/about-en.html 

markdown README.md  >> i18n/about-en.html

echo '</body></html>'  >> i18n/about-en.html


echo '<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="qrichtext" content="1" /><style type="text/css">p, li { white-space: pre-wrap; } </style></head> <body style=" font-size:9pt; font-weight:400; font-style:normal;">'  > i18n/about-nl.html

markdown README_NL.md  >> i18n/about-nl.html

echo '</body></html>'  >> i18n/about-en.html

