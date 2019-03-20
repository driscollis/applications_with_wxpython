import wx

from edit_dialog import EditDialog
from pubsub import pub


class AttributeDialog(EditDialog):
    """
    Dialog class for adding attributes
    """

    def on_save(self, event):
        """
        Event handler that is called when the Save button is
        pressed.
        Updates the XML object with the new node element and
        tells the UI to update to display the new element
        before destroying the dialog
        """
        attr = self.value_one.GetValue()
        value = self.value_two.GetValue()
        if attr:
            self.xml_obj.attrib[attr] = value
            pub.sendMessage('ui_updater_{}'.format(self.page_id),
                            xml_obj=self.xml_obj)

        else:
            # TODO - Show a dialog telling the user that there is no attr to save
            raise NotImplemented

self.Close()