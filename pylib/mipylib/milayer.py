#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2015-9-20
# Purpose: MeteoInfoLab layer module
# Note: Jython
#-----------------------------------------------------
from org.meteoinfo.data import TableUtil, XYListDataset
from org.meteoinfo.layer import LayerTypes
from org.meteoinfo.projection import ProjectionManage
from java.util import Date, Calendar
from java.awt import Font

from datetime import datetime

class MILayer():
    def __init__(self, layer):
        self.layer = layer
    
    def __repr__(self):
        return self.layer.getLayerInfo()
    
    def isvectorlayer(self):
        return self.layer.getLayerType() == LayerTypes.VectorLayer
    
    def cellvalue(self, fieldname, shapeindex):
        v = self.layer.getCellValue(fieldname, shapeindex)
        if isinstance(v, Date):
            cal = Calendar.getInstance()
            cal.setTime(v)
            year = cal.get(Calendar.YEAR)
            month = cal.get(Calendar.MONTH) + 1
            day = cal.get(Calendar.DAY_OF_MONTH)
            hour = cal.get(Calendar.HOUR_OF_DAY)
            minute = cal.get(Calendar.MINUTE)
            second = cal.get(Calendar.SECOND)
            dt = datetime(year, month, day, hour, minute, second)
            return dt
        else:
            return v
            
    def setcellvalue(self, fieldname, shapeindex, value):
        self.layer.editCellValue(fieldname, shapeindex, value)
            
    def shapes(self):
        return self.layer.getShapes()
        
    def shapenum(self):
        return self.layer.getShapeNum()
        
    def legend(self):
        return self.layer.getLegendScheme()
        
    def setlegend(self, legend):
        self.layer.setLegendScheme(legend)
    
    def addfield(self, fieldname, dtype, values=None):
        dt = TableUtil.toDataTypes(dtype)
        self.layer.editAddField(fieldname, dt)
        if not values is None:
            n = self.shapenum()
            for i in range(n):
                if i < len(values):
                    self.layer.editCellValue(fieldname, i, values[i])
                    
    def addlabels(self, fieldname, **kwargs):
        labelset = self.layer.getLabelSet()
        labelset.setFieldName(fieldname)
        fontname = kwargs.pop('fontname', 'Arial')
        fontsize = kwargs.pop('fontsize', 14)
        bold = kwargs.pop('bold', False)
        if bold:
            font = Font(fontname, Font.BOLD, fontsize)
        else:
            font = Font(fontname, Font.PLAIN, fontsize)
        labelset.setLabelFont(font)
        xoffset = kwargs.pop('xoffset', 0)
        labelset.setXOffset(xoffset)
        yoffset = kwargs.pop('yoffset', 0)
        labelset.setYOffset(yoffset)
        avoidcoll = kwargs.pop('avoidcoll', True)
        labelset.setAvoidCollision(avoidcoll)
        self.layer.addLabels()
        
    def getlabel(self, text):
        return self.layer.getLabel(text)
        
    def movelabel(self, label, x=0, y=0):
        self.layer.moveLabel(label, x, y)
        
    def project(self, toproj):
        r = ProjectionManage.projectLayer(self.layer, toproj)
        return MILayer(r)
        
    def clone(self):
        return MILayer(self.layer.clone())
    
    def save(self, fn=None):
        if fn is None:
            if self.layer.getFileName().strip() == '':
                print 'File name is needed to save the layer!'
            else:
                self.layer.saveFile()    
        else:
            self.layer.saveFile(fn)
        
class MIXYListData():
    def __init__(self, data=None):
        if data is None:
            self.data = XYListDataset()
        else:
            self.data = data
        
    def __getitem__(self, indices):
        if not isinstance(indices, tuple):
            inds = []
            inds.append(indices)
            indices = inds
            
        if isinstance(indices[0], int):
            if isinstance(indices[1], int):
                x = self.data.getX(indices[0], indices[1])
                y = self.data.getY(indices[0], indices[1])
                return x, y
            else:
                return self.data.getXValues(indices[0]), self.data.getXValues(indices[0])           
        
    def size(self, series=None):
        if series is None:
            return self.data.getSeriesCount()
        else:
            return self.data.getItemCount(series)
            
    def addseries(self, xdata, ydata, key=None):
        if key is None:
            key = 'Series_' + str(self.size())
        if isinstance(xdata, list):
            self.data.addSeries(key, xdata, ydata)
        else:
            self.data.addSeries(key, xdata.asarray(), ydata.asarray())   