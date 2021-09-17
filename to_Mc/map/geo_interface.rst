Author: Sean Gillies
Version: 1.0

Abstract
========

This document describes a GeoJSON-like protocol for geo-spatial (GIS) vector data.

Introduction
============

Python has a number of built-in protocols (descriptors, iterators, etc). A very
simple and familiar one involves string representations of objects. The
built-in ``str()`` function calls the ``__str__()`` method of its single
argument. By implementing ``__str__()``, instances of any class can be printed
by any other Python program.
::

  >>> class A(object):
  ...     def __str__(self):
  ...         return "Eh!"
  ... 
  >>> a = A()
  >>> str(a)
  'Eh!'
  >>> "%s" % a
  'Eh!'

What if we could do something like this for geo-spatial objects? It might,
for example, let any object be analyzed using any other hypothetical software
package like this::

  >>> from some_analytic_module import as_geometry
  >>> as_geometry(obj).buffer(1.0).area   # obj is a "point" of some kind
  3.1365484905459389

The hypothetical ``as_geometry()`` function of the hypothetical
`some_analytic_module` module would access relevant data of its single argument
using an agreed upon method or attribute.

__geo_interface__
=================
  
Following the lead of numpy's Array Interface [1]_, let's agree on
a ``__geo_interface__`` property. To avoid creating even more protocols, let's
make the value of this attribute a Python mapping. To further minimize
invention, let's borrow from the GeoJSON format [2]_ for the structure of this
mapping.

The keys are:

type (required)
  A string indicating the geospatial type. Possible values are "Feature" or
  a geometry type: "Point", "LineString", "Polygon", etc.

bbox (optional)
  A tuple of floats that describes the geo-spatial bounds of the object: (left,
  bottom, right, top) or (west, south, east, north).

properties (optional)
  A mapping of feature properties (labels, populations ... you name it.
  Dependent on the data). Valid for "Feature" types only.

geometry (optional)
  The geometric object of a "Feature" type, also as a mapping.

coordinates (required)
  Valid only for geometry types. This is an ``(x, y)`` or ``(longitude,
  latitude)`` tuple in the case of a "Point", a list of such tuples in the
  "LineString" case, or a list of lists in the "Polygon" case. See the GeoJSON
  spec for details.

Examples
========

First, a toy class with a point representation::

  >>> class Pointy(object):
  ...     __geo_interface__ = {'type': 'Point', 'coordinates': (0.0, 0.0)}
  ... 
  >>> as_geometry(Pointy()).buffer(1.0).area
  3.1365484905459389

Next, a toy class with a feature representation::

  >>> class Placemark(object):
  ...     __geo_interface__ = {
  ...         'type': 'Feature',
  ...         'properties': {'name': 'Phoo'},
  ...         'geometry': Pointy.__geo_interface__ }
  >>> from my_analytic_module import as_feature
  >>> as_feature(Placemark())['properties']['name']
  'Phoo'

Implementations
===============

Python programs and packages that you have heard of – and made be a frequent
user of – already implement this protocol:

* ArcPy [3]_
* descartes [4]_
* geojson [5]_
* PySAL [6]_

Shapely
-------

Shapely [7]_ provides a ``shape()`` function that makes Shapely geometries from
objects that provide ``__geo_interface__`` and a ``mapping()`` function that
writes geometries out as dictionaries::

  >>> from shapely.geometry import Point
  >>> from shapely.geometry import mapping, shape
  >>> Point(0.0, 0.0).__geo_interface__
  {'type': 'Point', 'coordinates': (0.0, 0.0)}
  >>> shape(Point(0.0, 0.0))
  <shapely.geometry.point.Point object at 0x...>
  >>> mapping(Point(0.0, 0.0))
  {'type': 'Point', 'coordinates': (0.0, 0.0)}

The Shapely version of the example in the introduction is::

  >>> from shapely.geometry import shape
  >>> shape(obj).buffer(1.0).area
  3.1365484905459389

where ``obj`` could be a geometry object from ArcPy or PySAL, or even a mapping
directly::

  >>> shape({'type': 'Point', 'coordinates': (0.0, 0.0)}).buffer(1.0).area
  3.1365484905459389

References
==========

.. [1] http://docs.scipy.org/doc/numpy/reference/arrays.interface.html
.. [2] https://tools.ietf.org/html/rfc7946
.. [3] https://desktop.arcgis.com/en/arcmap/latest/analyze/arcpy-functions/asshape.htm
.. [4] https://bitbucket.org/sgillies/descartes/src/f97e54f3b8d4/descartes/patch.py#cl-14
.. [5] http://pypi.python.org/pypi/geojson/
.. [6] https://pysal.readthedocs.io/en/latest/users/tutorials/shapely.html
.. [7] https://github.com/Toblerity/Shapely
