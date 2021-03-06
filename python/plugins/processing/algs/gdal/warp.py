# -*- coding: utf-8 -*-

"""
***************************************************************************
    self.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from builtins import str

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtGui import QIcon

from processing.algs.gdal.GdalAlgorithm import GdalAlgorithm
from processing.core.parameters import ParameterRaster
from processing.core.parameters import ParameterExtent
from processing.core.parameters import ParameterSelection
from processing.core.parameters import ParameterCrs
from processing.core.parameters import ParameterNumber
from processing.core.parameters import ParameterString
from processing.core.parameters import ParameterBoolean
from processing.core.outputs import OutputRaster
from processing.algs.gdal.GdalUtils import GdalUtils

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


class warp(GdalAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    SOURCE_SRS = 'SOURCE_SRS'
    DEST_SRS = 'DEST_SRS'
    METHOD = 'METHOD'
    METHOD_OPTIONS = ['near', 'bilinear', 'cubic', 'cubicspline', 'lanczos']
    TR = 'TR'
    NO_DATA = 'NO_DATA'
    EXTRA = 'EXTRA'
    RTYPE = 'RTYPE'
    TYPE = ['Byte', 'Int16', 'UInt16', 'UInt32', 'Int32', 'Float32', 'Float64']
    TILED = 'TILED'
    COMPRESS = 'COMPRESS'
    JPEGCOMPRESSION = 'JPEGCOMPRESSION'
    PREDICTOR = 'PREDICTOR'
    ZLEVEL = 'ZLEVEL'
    BIGTIFF = 'BIGTIFF'
    BIGTIFFTYPE = ['', 'YES', 'NO', 'IF_NEEDED', 'IF_SAFER']
    COMPRESSTYPE = ['NONE', 'JPEG', 'LZW', 'PACKBITS', 'DEFLATE']
    TFW = 'TFW'
    RAST_EXT = 'RAST_EXT'
    EXT_CRS = 'EXT_CRS'

    def getIcon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'gdaltools', 'warp.png'))

    def defineCharacteristics(self):
        self.name, self.i18n_name = self.trAlgorithm('Warp (reproject)')
        self.group, self.i18n_group = self.trAlgorithm('[GDAL] Projections')
        self.addParameter(ParameterRaster(self.INPUT, self.tr('Input layer'), False))
        self.addParameter(ParameterCrs(self.SOURCE_SRS,
                                       self.tr('Source SRS'), '', optional=True))
        self.addParameter(ParameterCrs(self.DEST_SRS,
                                       self.tr('Destination SRS'), ''))
        self.addParameter(ParameterString(self.NO_DATA,
                                          self.tr("Nodata value, leave blank to take the nodata value from input"),
                                          '', optional=True))
        self.addParameter(ParameterNumber(self.TR,
                                          self.tr('Output file resolution in target georeferenced units (leave 0 for no change)'),
                                          0.0, None, 0.0))
        self.addParameter(ParameterSelection(self.METHOD,
                                             self.tr('Resampling method'), self.METHOD_OPTIONS))
        self.addParameter(ParameterExtent(self.RAST_EXT, self.tr('Raster extent')))

        if GdalUtils.version() >= 2000000:
            self.addParameter(ParameterCrs(self.EXT_CRS,
                                           self.tr('CRS of the raster extent'), ''))

        params = []
        params.append(ParameterSelection(self.RTYPE,
                                         self.tr('Output raster type'), self.TYPE, 5))
        params.append(ParameterSelection(self.COMPRESS,
                                         self.tr('GeoTIFF options. Compression type:'), self.COMPRESSTYPE, 4))
        params.append(ParameterNumber(self.JPEGCOMPRESSION,
                                      self.tr('Set the JPEG compression level'),
                                      1, 100, 75))
        params.append(ParameterNumber(self.ZLEVEL,
                                      self.tr('Set the DEFLATE compression level'),
                                      1, 9, 6))
        params.append(ParameterNumber(self.PREDICTOR,
                                      self.tr('Set the predictor for LZW or DEFLATE compression'),
                                      1, 3, 1))
        params.append(ParameterBoolean(self.TILED,
                                       self.tr('Create tiled output (only used for the GTiff format)'), False))
        params.append(ParameterSelection(self.BIGTIFF,
                                         self.tr('Control whether the created file is a BigTIFF or a classic TIFF'), self.BIGTIFFTYPE, 0))
        params.append(ParameterBoolean(self.TFW,
                                       self.tr('Force the generation of an associated ESRI world file (.tfw))'), False))
        params.append(ParameterString(self.EXTRA,
                                      self.tr('Additional creation parameters'), '', optional=True))

        for param in params:
            param.isAdvanced = True
            self.addParameter(param)

        self.addOutput(OutputRaster(self.OUTPUT, self.tr('Reprojected')))

    def getConsoleCommands(self):
        noData = self.getParameterValue(self.NO_DATA)
        if noData is not None:
            noData = str(noData)
        srccrs = self.getParameterValue(self.SOURCE_SRS)
        dstcrs = self.getParameterValue(self.DEST_SRS)
        jpegcompression = str(self.getParameterValue(self.JPEGCOMPRESSION))
        predictor = str(self.getParameterValue(self.PREDICTOR))
        zlevel = str(self.getParameterValue(self.ZLEVEL))
        tiled = str(self.getParameterValue(self.TILED))
        compress = self.COMPRESSTYPE[self.getParameterValue(self.COMPRESS)]
        bigtiff = self.BIGTIFFTYPE[self.getParameterValue(self.BIGTIFF)]
        tfw = str(self.getParameterValue(self.TFW))
        rastext = str(self.getParameterValue(self.RAST_EXT))
        rastext_crs = self.getParameterValue(self.EXT_CRS)

        arguments = []
        arguments.append('-ot')
        arguments.append(self.TYPE[self.getParameterValue(self.RTYPE)])
        if len(srccrs) > 0:
            arguments.append('-s_srs')
            arguments.append(srccrs)
        if len(dstcrs) > 0:
            arguments.append('-t_srs')
            arguments.append(dstcrs)
        if noData and len(noData) > 0:
            arguments.append('-dstnodata')
            arguments.append(noData)
        arguments.append('-r')
        arguments.append(
            self.METHOD_OPTIONS[self.getParameterValue(self.METHOD)])
        arguments.append('-of')
        out = self.getOutputValue(self.OUTPUT)
        arguments.append(GdalUtils.getFormatShortNameFromFilename(out))
        if self.getParameterValue(self.TR) != 0:
            arguments.append('-tr')
            arguments.append(str(self.getParameterValue(self.TR)))
            arguments.append(str(self.getParameterValue(self.TR)))
        extra = self.getParameterValue(self.EXTRA)
        if extra is not None:
            extra = str(extra)
        regionCoords = rastext.split(',')
        try:
            rastext = []
            rastext.append('-te')
            rastext.append(regionCoords[0])
            rastext.append(regionCoords[2])
            rastext.append(regionCoords[1])
            rastext.append(regionCoords[3])
        except IndexError:
            rastext = []
        if rastext:
            arguments.extend(rastext)

        if GdalUtils.version() >= 2000000:
            if rastext and rastext_crs is not None:
                arguments.append('-te_srs')
                arguments.append(rastext_crs)

        if extra and len(extra) > 0:
            arguments.append(extra)
        if GdalUtils.getFormatShortNameFromFilename(out) == "GTiff":
            arguments.append("-co COMPRESS=" + compress)
            if compress == 'JPEG':
                arguments.append("-co JPEG_QUALITY=" + jpegcompression)
            elif (compress == 'LZW') or (compress == 'DEFLATE'):
                arguments.append("-co PREDICTOR=" + predictor)
            if compress == 'DEFLATE':
                arguments.append("-co ZLEVEL=" + zlevel)
            if tiled == "True":
                arguments.append("-co TILED=YES")
            if tfw == "True":
                arguments.append("-co TFW=YES")
            if len(bigtiff) > 0:
                arguments.append("-co BIGTIFF=" + bigtiff)

            arguments.append("-wo OPTIMIZE_SIZE=TRUE")

        arguments.append(self.getParameterValue(self.INPUT))
        arguments.append(out)

        return ['gdalwarp', GdalUtils.escapeAndJoin(arguments)]
