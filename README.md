Geopunt4Qgis
============

![Geopunt for QGIS](images/logogeopunt4Q.png "Geopunt for QGIS")


Functions
--------

  * <a href="http://warrieka.github.io/index.html#!geopuntAddress.md" ><img src="images/geopuntAddressSmall.png" /> Search an Address</a> 
  * <a href="http://warrieka.github.io/index.html#!geopuntReverse.md" ><img src="images/geopuntReverseSmall.png" /> Click an Address on the m   map</a>
  * <a href="http://warrieka.github.io/index.html#!geopuntBatchgeocode.md" ><img src="images/geopuntBatchgeocodeSmall.png" /> Geocode CSV-files </a>
  * <a href="http://warrieka.github.io/index.html#!geopuntPoi.md" ><img src="images/geopuntPoiSmall.png" /> Find a point of intrest</a>
  * <a href="http://warrieka.github.io/index.html#!geopuntGIPOD.md" ><img src="images/geopuntGIPODsmall.png" /> GIPOD</a>
  * <a href="http://warrieka.github.io/index.html#!geopuntElevation.md" ><img src="images/geopuntElevationSmall.png" /> Elevation profile</a>
  * <a href="http://warrieka.github.io/index.html#!geopuntDatacatalog.md" ><img src="images/geopuntDataCatalogusSmall.png" /> Geopunt catalog</a>

  
System requirements
-------------------

- QGIS 2.0 or above
- Python 2.7 (installed with qgis)
- Any OS capable of running QGIS with python plug-ins: ao. MS Windows, Mac OSX and Linux
- The python modules mathplotlib and numpy, installed with the Windows and Linux version of QGIS, but on MacOSX you have to install them separately. 
- Requires internet connection, restrictive firewalls may block connection

 
Goals
-----

geopunt4Qgis - *"Geopunt for QGIS"* is a plugin for the [QGIS](http://www.qgis.org/) open source desktop GIS. 

The Flemish government Geographical Portal Geopunt offers several web-services that can be used freely by third party's, including other governments and citizens. 

The mapping services are based on the OGC open standard WMS or WMTS and can be added to to QGIS easily. These services can be found through the [metadacenter](https://metadata.geopunt.be/zoekdienst/apps/tabsearch/index.html).

But some services are not standardized because there is no widely used open standard. These public web-services are  composed with a REST-full API, this easier to use for programmers then OGC-services. But because they are not standardized, they can't be used directly by desktop software.

These include:

- **Geocoding** based on the Flemish [CRAB](http://www.agiv.be/gis/projecten/?catid=34) address-database
- **Location search** based on databases joined to the CRAB database, like the locations of the schools in Flanders.
- **Traffic obstruction information** from the [GIPOD](http://gipod.api.agiv.be/#!index.md) public works and manifestation database.
- **Elevation profile** a service that queries the digital elevation model Flanders, a set of along a line is retrieved.
- **Metadata catalog** the [metadatacenter](https://metadata.geopunt.be) of Geopunt contains information about datasets and services from AGIV, DOV (geology) and MercatorNet (a co-operation between several Flemish governmental agencies).

The goal of this project is to make these web-services available to QGIS-users, so they can be uses for creating print-maps and for doing research and analyses.


What is Geopunt ?
--------------

[Geopunt](http://www.geopunt.be/) is the central gateway to government geographic information in Flanders. The portal focuses on a comprehensive data, services and application offerings to a broad and diverse audience. Citizens looking for a suitable land or the GIS-user or engineer who wishes to perform an environmental study. Socially relevant geographic data and services are brought together in an intelligent and user-friendly manner. 

All components (metadata catalog , download application, data and network services) are directly integrated. The geoportal is the Flemish node in a European spatial data infrastructure and meets the requirements of the [European INSPIRE directive](http://inspire-geoportal.ec.europa.eu/).

Geopunt is the website of the partnership for geographic information within the Flemish government, GDI Flanders (GDI = Spatial Data Infrastructures). The Flemish Agency for Geographical Information [(AGIV)](http://www.agiv.be/gis/) is responsible for organizing and maintaining geopunt.

About the author
----------------

My name is **Kay Warrie**. I am geospatial data-analyst and developer from Belgium. 
My current employer is the research department of the city of Antwerp. 
Professionaly I work on webmapping with ESRI arcgis-server or Mapbox Tilemill and on desktop GIS using arcgis or QGIS and other open source GIS. I also maintain INSPIRE-compliant metadata as a part of the Flemish Geodata Infrastruce (GDI). But above all I do all kinds of GIS analyses on city data. Most analyses are related to adressing-geocoding, spatial relationships,  proximity analyses (routing, service area's etc.) for environmental impact studies, zoning or construction permits.

[Contact me](mailto:kaywarrie@gmail.com)

[More about me](http://warrieka.github.io/#!aboutMe.md)

#### Sources:

- *[http://www.geopunt.be](http://www.geopunt.be/over-geopunt)* 
- *[http://gditestbed.agiv.be/](http://gditestbed.agiv.be/)*
- *[https://www.agiv.be/](https://www.agiv.be/)*
