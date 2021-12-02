import QtQuick 2.15
import QtQuick.Controls 2.15

/*
 QML Multiline comments
*/

ApplicationWindow {
    visible: true
    width: 400
    height: 600
    title: "Example App"
	property string currTime: "00:00:00"

    Rectangle {
        anchors.fill: parent

        Image {
            // sourceSize.width: parent.width  // inline comment
            // sourceSize.height: parent.height
            anchors.fill: parent
            // source: "./img/background.png" srcset="https://ik.imagekit.io/mfitzp/pythonguis/tutorials/qml-qtquick-python-application/background.png?tr=w-100 100w, https://ik.imagekit.io/mfitzp/pythonguis/tutorials/qml-qtquick-python-application/background.png?tr=w-200 200w, https://ik.imagekit.io/mfitzp/pythonguis/tutorials/qml-qtquick-python-application/background.png?tr=w-400 400w, https://ik.imagekit.io/mfitzp/pythonguis/tutorials/qml-qtquick-python-application/background.png?tr=w-600 600w" loading="lazy" width="564" height="1003"
            // source: "./img/background.png" loading="lazy" width="564" height="1003"
            source: "./img/background.png"
            fillMode: Image.PreserveAspectCrop
        }

        Rectangle {
            anchors.fill: parent
            color: "transparent"
            // color: "steelblue"

            Text {
                anchors {
                    bottom: parent.bottom
                    bottomMargin: 12
                    left: parent.left
                    leftMargin: 12
                }
                text: currTime  
                font.pixelSize: 48
                color: "white"
            }

        }

    }

}
