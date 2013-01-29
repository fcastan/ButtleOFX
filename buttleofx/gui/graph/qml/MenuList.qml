import QtQuick 1.1

Item {
    id: menulist

    // parentName = the key for the python dictionary of plugins. Ex: 'tuttle/image/' or 'tuttle/image/process/filter/
    property string parentName
    property variant clickFrom: tools

    ListView {
        height: 300
        width: 160
        id: nodeMenuView
        model: _buttleData.getQObjectPluginsIdentifiersByParentPath(menulist.parentName)

        property variant nextMenu: null

        function destroyNextMenu()
        {
            if( nodeMenuView.nextMenu )
                nodeMenuView.nextMenu.destroy()
        }

        function createNextMenu(parentName, labelElement, x, y)
        {
            destroyNextMenu()
            var newComponent = Qt.createQmlObject('MenuList { parentName: "' + parentName + labelElement + '/"; x: ' + x + '; y: ' + y + '; }', nodeMenuView);
            nodeMenuView.nextMenu = newComponent
        }

        delegate {
            Component {
                MenuElement {
                    id: nodeMenuElement
                    labelElement: object[0]
                    idElement: object[1]
                    parentName: menulist.parentName
                    menuListItem: nodeMenuView
                }
            }
        }
    }

}
