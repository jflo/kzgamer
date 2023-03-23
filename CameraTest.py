from PyQt5.QtWidgets import QApplication
from picamera2.previews.qt import QGlPicamera2
from picamera2 import Picamera2
import os
os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")
os.environ.update({"QT_QPA_PLATFORM_PLUGIN_PATH":"/usr/lib/aarch64-linux-gnu/qt5/plugins/xcbglintegrations/libqxcb-glx-integration.so"})

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
app = QApplication([])
qpicamera2 = QGlPicamera2(picam2, width=470, height=750, keep_ar=True)
qpicamera2.setWindowTitle("Qt Picamera2 App")
picam2.start()
qpicamera2.show()
app.exec()
