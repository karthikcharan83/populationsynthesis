
from qgis.core import *
from qgis.gui import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ClickTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas=canvas
        self.ll = None
        self.ur = None
        self.o = QObject()
        self.precision = 0.000001
        self.cursor = QCursor(Qt.PointingHandCursor)


    def canvasPressEvent(self,event):
        print "got a click event"
        print event.pos().x(),event.pos().y()
        transform = self.canvas.getCoordinateTransform()
        coord = transform.toMapCoordinates(event.pos().x(),event.pos().y())
        self.bb = QgsRect(
            QgsPoint(coord.x()*(1-self.precision),coord.y()*(1-self.precision)),
            QgsPoint(coord.x()*(1+self.precision),coord.y()*(1+self.precision))
            )
        self.o.emit(SIGNAL("finished()"))


    def isZoomTool(self):
        return False





