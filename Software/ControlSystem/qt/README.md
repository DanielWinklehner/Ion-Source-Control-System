This branch replaces the channel plot widgets with pyqtGraph "RemoteGraphicsView" objects. These offload the drawing to spearate python processes.

Current state of this feature is that it doesn't really improve performance at all (which is nice to know)

# Qt Ion Source Control System Software

Written for Python 3/PyQt5/PyQtGraph

New features:
 - No interruption on device disconnect (requires newest RasPi server)
 - Procedures

Features in Progress:
 - Device/Channel editor
 - h5 logging

Requirements:
 - Python 3
 - PyQt5
 - PyQtGraph
 - numpy
 - scipy
 - Requests
 - h5py
