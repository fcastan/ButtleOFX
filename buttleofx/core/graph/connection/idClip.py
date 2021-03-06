class IdClip(object):
    """
        Class useful to identify a clip with :
        - _id : the clipId
        - _nodeName : the node name
        - _clipName : the clipName
    """

    def __init__(self, nodeName, clipName):
        super(IdClip, self).__init__()
        
        self._id = nodeName + clipName
        self._nodeName = nodeName
        self._clipName = clipName

    def __eq__(self, otherClip):
        """
            Overloads the operator ==
        """
        return (self._nodeName == otherClip._nodeName and self._clipName == otherClip._clipName)

    def __str__(self):
        return 'Node  "%s" , Clip "%s" (index %d)' % (self._nodeName, self._clipName)

    ######## getters ########

    def getId(self):
        return self._id

    def getNodeName(self):
        return self._nodeName

    def getClipName(self):
        return self._clipName

    ######## setters ########

    def setCoord(self, coord):
        self._coord = coord

    def setXCoord(self, xCoord):
        self._coord[0] = xCoord

    def setYCoord(self, yCoord):
        self._coord[1] = yCoord

    ######## SAVE  ########

    def object_to_dict(self):
        """
            Convert the idClip to a dictionary of his representation.
        """
        clip = {
            "nodeName": self._nodeName,
            "clipName": self._clipName,
        }
        return clip
