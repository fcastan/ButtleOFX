from PyQt5 import QtCore, QtGui
# quickmamba
from quickmamba.patterns import Signal
# data
from buttleofx.data import ButtleDataSingleton
# connection
from buttleofx.core.graph.connection import IdClip


class ConnectionManager(QtCore.QObject):
    """
        This class manages actions about connections.
    """

    def __init__(self):
        super(ConnectionManager, self).__init__()

        self.undoRedoChanged = Signal()

    ############### flags ###############

    @QtCore.pyqtSlot(QtCore.QObject, QtCore.QObject, bool, result=bool)
    def canConnect(self, clip1, clip2, connected):
        """
            Returns True if the connection between the nodes is possible, else False.
            A connection is possible if the clip isn't already taken, and if the clips are from 2 different nodes, not already connected.
        """
        
        buttleData = ButtleDataSingleton().get()
        graph = buttleData.getGraph()

        # if the clips are from the same node : False
        if (clip1.getNodeName() == clip2.getNodeName()):
            if(not connected):
                return False

        # if the clips are 2 inputs or 2 outputs : False
        if(connected):
          if (clip1.getClipName() == "Output" and clip2.getClipName() != "Output") or (clip1.getClipName() != "Output" and clip2.getClipName() == "Output"):
              return False
        else:
          if (clip1.getClipName() == "Output" and clip2.getClipName() == "Output") or (clip1.getClipName() != "Output" and clip2.getClipName() != "Output"):
              return False

        # if the nodes containing the clips are already connected : False
        if(graph.nodesConnected(clip2, clip1)):
            return False
        return True
        
    @QtCore.pyqtSlot(QtCore.QObject, result=bool)
    def connectionExists(self, clip):
        """
            Returns True if a connection between the nodes already exists, else False.
            A connection is possible if the clip isn't already taken, and if the clips are from 2 different nodes, not already connected.
        """
        buttleData = ButtleDataSingleton().get()
        graph = buttleData.getGraph()

        # if the input clip is already taken : False
        return graph.contains(clip)

    @QtCore.pyqtSlot(str, QtCore.QObject, int, result=bool)
    def canConnectTmpNodes(self, dataTmpClip, clip, clipIndex):
        """
            Returns True if the connection between the nodes is possible, else False.
            This function is called by Clip.qml on the event onDragEnter, to display in real time if the nodes can be connected (during a creation of a connection).
            It simulates a connection and calls the function self.canConnect(clip1, clip2).
        """
        buttleData = ButtleDataSingleton().get()

        print("-----------------------------------------------------------------------")
        # we split the data of the tmpClip (from mimeData) to find needed informations about this clip.
        infosTmpClip = dataTmpClip.split("/")
        #if infosTmpClip[0] != "clip" or len(infosTmpClip) != 4:
            #return False
        #else:
            #tmpClipNodeName, tmpClipName, tmpClipIndex = infosTmpClip[1], infosTmpClip[2], int(infosTmpClip[3])
        tmpClipNodeName = str(clip.getNodeName())
        tmpClipName = str(clip.getClipName())
        tmpClipIndex = str(clipIndex)
        # we find the position of this tmpClip to be able to create a IdClip object.
        positionTmpClip = buttleData.getGraphWrapper().getPositionClip(tmpClipNodeName, tmpClipName, tmpClipIndex)
        tmpClip = IdClip(tmpClipNodeName, tmpClipName)

        if tmpClip:
            # idem, for the "dropped" clip = newClip
            positionNewClip = buttleData.getGraphWrapper().getPositionClip(clip.getNodeName(), clip.getClipName(), clipIndex)
            newClip = IdClip(clip.getNodeName(), clip.getClipName())
            # finally we return if the clips can be connected
            return self.canConnect(tmpClip, newClip)

        else:
            return False

    ############### EVENTS FROM QML ###############
    
    @QtCore.pyqtSlot(QtCore.QObject, result=QtCore.QObject)
    def connectedClip(self, clip):
        buttleData = ButtleDataSingleton().get()
        
        for connection in  buttleData.getGraph()._connections:
            if(clip.getNodeName() == connection.getClipIn().getNodeName() and clip.getClipName() == connection.getClipIn().getClipName()):
                return connection.getClipOut()
        
        return None

    @QtCore.pyqtSlot(QtCore.QObject, int)
    def connectionDragEvent(self, clip, clipIndex):
        """
            Function called when a clip is pressed (but not released yet).
            The function sends mimeData to identify the clip.
        """
        #widget = QtGui.QWidget()
        #drag = QtGui.QDrag(widget)
        mimeData = QtCore.QMimeData()

        # Sets informations of the first clip to the mimedata, as text.
        # Example of mimeData : "clip/TuttleJpegReader_1/Output/1"
        mimeData.setText("clip/" + str(clip.getNodeName()) + "/" + str(clip.getClipName()) + "/" + str(clipIndex))
        #drag.setMimeData(mimeData)

        # transparent pixmap
        #pixmap = QtGui.QPixmap(1, 1)
        #pixmap.fill(QtCore.Qt.transparent)
        #drag.setPixmap(pixmap)

        # starts the drag
        #drag.exec_(QtCore.Qt.MoveAction)

    @QtCore.pyqtSlot(str, QtCore.QObject, int)
    def connectionDropEvent(self, dataTmpClip, clip, clipIndex):
        """
            Creates or deletes a connection between 2 clips ('tmpClip', the "dragged" clip, and 'newClip', the "dropped" clip)
            Arguments :
            - dataTmpClip : the string from mimeData, identifying the tmpClip (the "dragged" clip).
            - clip : the ClipWrapper of the "dropped" clip.
            - clipIndex : the index of the "dropped" clip.
        """
        buttleData = ButtleDataSingleton().get()

        # we split the data of the tmpClip (from mimeData) to find needed informations about this clip.
        infosTmpClip = dataTmpClip.split("/")

        if infosTmpClip[0] != "clip" or len(infosTmpClip) != 4:
            return  # use exception !
        else:
            tmpClipNodeName, tmpClipName, tmpClipIndex = infosTmpClip[1], infosTmpClip[2], int(infosTmpClip[3])

        # we find the position of this tmpClip to be able to create a IdClip object.
        positionTmpClip = buttleData.getGraphWrapper().getPositionClip(tmpClipNodeName, tmpClipName, tmpClipIndex)
        tmpClip = IdClip(tmpClipNodeName, tmpClipName, clipIndex, positionTmpClip)

        if tmpClip:
            # idem, for the "dropped" clip = newClip
            positionNewClip = buttleData.getGraphWrapper().getPositionClip(clip.getNodeName(), clip.getClipName(), clipIndex)
            newClip = IdClip(clip.getNodeName(), clip.getClipName(), clipIndex, positionNewClip)

            # a connection must be created from the ouput clip to the input clip (the order of the arguments is important !)
            if tmpClip.getClipName() == "Output":
                clipOut, clipIn = tmpClip, newClip
            else:
                clipOut, clipIn = newClip, tmpClip

            # if the clips can be connected, we connect them
            if self.canConnect(clipOut, clipIn):
                self.connect(clipOut, clipIn)
                return

            # else if they can't be connected, we check if they are already connected, and disconnect them if it is the case.
            else:
                connection = buttleData.getGraph().getConnectionByClips(clipOut, clipIn)
                if connection:
                    self.disconnect(buttleData.getGraphWrapper().getConnectionWrapper(connection.getId()))
                    return

        # update undo/redo display
        self.undoRedoChanged()

    @QtCore.pyqtSlot(QtCore.QObject, QtCore.QObject)
    def connectWrappers(self, clipOut, clipIn):
        # print("connectWrappers:", clipOut, clipIn)
        id_clipOut = IdClip(clipOut.getNodeName(), clipOut.getClipName())
        id_clipIn = IdClip(clipIn.getNodeName(), clipIn.getClipName())
        
        self.connect(id_clipOut, id_clipIn)
        
        
    @QtCore.pyqtSlot()
    def copyConnections(self):
        """
            Copies the connection(s) of the current node(s).
        """
        buttleData = ButtleDataSingleton().get()
        
        buttleData.clearCurrentCopiedConnectionsInfo()
         
        if buttleData.getCurrentSelectedNodeWrappers():
            for node in buttleData.getCurrentSelectedNodeWrappers():
                copyConnection = {}    
                
                output = self.connectionExists(buttleData.getGraphWrapper().getNodeWrapper(node.getName()).getOutputClip())
                inputs = buttleData.getGraphWrapper().getNodeWrapper(node.getName())._srcClips
                       
                cpt = 0
                saveConnection = False
                for input in inputs:
                    testConnection = self.connectionExists(input)
                    if(testConnection):
                        copyConnection.update({"inputNodeName": node.getNode().getName()})
                        copyConnection.update({"input"+str(cpt) : input.getClipName()}) 
                    connectedClip = buttleData.graphWrapper.getConnectedClipWrapper(input, False)
                    if(connectedClip):
                        connectedNode = buttleData.getGraphWrapper().getNodeWrapper(connectedClip.getNodeName())
                        for nodeSelected in buttleData.getCurrentSelectedNodeWrappers():
                            if(nodeSelected.getName() == connectedNode.getName()):
                                copyConnection.update({"outputNodeName"+str(cpt) : connectedNode.getName()})
                                copyConnection.update({"output"+str(cpt) : connectedClip.getClipName()})
                                saveConnection = True
                                break
                            else:
                                saveConnection = False
                    cpt = cpt + 1
                if(saveConnection):
                    buttleData.getCurrentCopiedConnectionsInfo()[node.getName()] = copyConnection
            
                
    @QtCore.pyqtSlot()
    def pasteConnection(self):
        """
            Pasts the connection of the current node(s).
        """
        buttleData = ButtleDataSingleton().get()
        # If nodes have been copied previously
        if buttleData.getCurrentCopiedNodesInfo():
            # Create a copy for each node copied
            for connection in buttleData.getCurrentCopiedConnectionsInfo():
                length = len(buttleData.getCurrentCopiedConnectionsInfo()[connection])
                    
                copiedNodeInName = buttleData.getCurrentCopiedNodesInfo()[buttleData.getCurrentCopiedConnectionsInfo()[connection]["inputNodeName"]] [buttleData.getCurrentCopiedConnectionsInfo()[connection]["inputNodeName"]]
                copiedNodeIn = buttleData.getGraphWrapper().getNodeWrapper(copiedNodeInName)
                
                if(length > 4):
                  for i in range(0, length-5):   
                      copiedNodeOutName = buttleData.getCurrentCopiedNodesInfo()[buttleData.getCurrentCopiedConnectionsInfo()[connection]["outputNodeName"+str(i)]] [buttleData.getCurrentCopiedConnectionsInfo()[connection]["outputNodeName"+str(i)]]
                      copiedNodeOut = buttleData.getGraphWrapper().getNodeWrapper(copiedNodeOutName)
                      copiedInputName = buttleData.getCurrentCopiedConnectionsInfo()[connection]["input"+str(i)]  
                      copiedInput = copiedNodeIn.getClip(copiedInputName)
                      copiedOutputName = buttleData.getCurrentCopiedConnectionsInfo()[connection]["output"+str(i)]  
                      copiedOutput = copiedNodeOut.getClip(copiedOutputName)
                      self.connectWrappers(copiedOutput, copiedInput)
                else: 
                      copiedNodeOutName = buttleData.getCurrentCopiedNodesInfo()[buttleData.getCurrentCopiedConnectionsInfo()[connection]["outputNodeName0"]] [buttleData.getCurrentCopiedConnectionsInfo()[connection]["outputNodeName0"]]
                      copiedNodeOut = buttleData.getGraphWrapper().getNodeWrapper(copiedNodeOutName)
                      copiedInputName = buttleData.getCurrentCopiedConnectionsInfo()[connection]["input0"]  
                      copiedInput = copiedNodeIn.getClip(copiedInputName)
                      copiedOutputName = buttleData.getCurrentCopiedConnectionsInfo()[connection]["output0"]  
                      copiedOutput = copiedNodeOut.getClip(copiedOutputName)
                      self.connectWrappers(copiedOutput, copiedInput)
        self.undoRedoChanged()
        

    @QtCore.pyqtSlot(QtCore.QObject, QtCore.QObject, QtCore.QObject, QtCore.QObject, QtCore.QObject)
    def dissociate(self, clipOut, clipIn, middleIn, middleOut, connectionWrapper):
        id_clipOut = IdClip(clipOut.getNodeName(), clipOut.getClipName())
        id_clipIn = IdClip(clipIn.getNodeName(), clipIn.getClipName())
        id_middleIn = IdClip(middleIn.getNodeName(), middleIn.getClipName())
        id_middleOut = IdClip(middleOut.getNodeName(), middleOut.getClipName())
        
        self.connect(id_clipOut, id_middleIn)
        self.connect(id_middleOut, id_clipIn)
        self.disconnect(connectionWrapper)
      
    @QtCore.pyqtSlot(QtCore.QObject, QtCore.QObject, QtCore.QObject)
    def replace(self, clip, clipOut, clipIn):
        buttleData = ButtleDataSingleton().get()
        for connection in  buttleData.getGraph()._connections:
            if((clip.getNodeName() == connection.getClipOut().getNodeName() and clip.getClipName() == connection.getClipOut().getClipName()) or (clip.getNodeName() == connection.getClipIn().getNodeName() and clip.getClipName() == connection.getClipIn().getClipName())):
                buttleData.getGraph().deleteConnection(connection)
                
        id_clipOut = IdClip(clipOut.getNodeName(), clipOut.getClipName())
        id_clipIn = IdClip(clipIn.getNodeName(), clipIn.getClipName())
        self.connect(id_clipOut, id_clipIn)
        
    @QtCore.pyqtSlot(QtCore.QObject)
    def unHook(self, clip):
        buttleData = ButtleDataSingleton().get()
        for connection in  buttleData.getGraph()._connections:
            if((clip.getNodeName() == connection.getClipOut().getNodeName() and clip.getClipName() == connection.getClipOut().getClipName()) or (clip.getNodeName() == connection.getClipIn().getNodeName() and clip.getClipName() == connection.getClipIn().getClipName())):
                buttleData.getGraph().deleteConnection(connection)
        
    ############### CREATION AND DESTRUCTION ###############

    def connect(self, clipOut, clipIn):
        """
            Adds a connection between 2 clips.
        """
        buttleData = ButtleDataSingleton().get()
        buttleData.getGraph().createConnection(clipOut, clipIn)
        self.colorChildAsParent(clipOut, clipIn)

    @QtCore.pyqtSlot(QtCore.QObject)
    def disconnect(self, connectionWrapper):
        """
            Removes a connection between 2 clips.
        """
        buttleData = ButtleDataSingleton().get()
        buttleData.getGraph().deleteConnection(connectionWrapper.getConnection())

    ############### COLORS ###############

    def colorChildAsParent(self, clipOut, clipIn):
        """
            When two nodes are connected, the child take the color of its parent
        """
        buttleData = ButtleDataSingleton().get()
        parentNode = buttleData.getGraphWrapper().getNodeWrapper(clipOut.getNodeName()).getNode()
        childNode = buttleData.getGraphWrapper().getNodeWrapper(clipIn.getNodeName()).getNode()
        childNode.setColor(parentNode.getColor())
