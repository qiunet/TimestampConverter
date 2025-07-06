import xml.etree.ElementTree as ET
import sys
import os
import time
import logging
import logging.handlers

ICON_ROOT = '/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources'

ICON_ACCOUNT = os.path.join(ICON_ROOT, 'Accounts.icns')
ICON_BURN = os.path.join(ICON_ROOT, 'BurningIcon.icns')
ICON_CLOCK = os.path.join(ICON_ROOT, 'Clock.icns')
ICON_COLOR = os.path.join(ICON_ROOT, 'ProfileBackgroundColor.icns')
ICON_COLOUR = ICON_COLOR  # Queen's English, if you please
ICON_EJECT = os.path.join(ICON_ROOT, 'EjectMediaIcon.icns')
# Shown when a workflow throws an error
ICON_ERROR = os.path.join(ICON_ROOT, 'AlertStopIcon.icns')
ICON_FAVORITE = os.path.join(ICON_ROOT, 'ToolbarFavoritesIcon.icns')
ICON_FAVOURITE = ICON_FAVORITE
ICON_GROUP = os.path.join(ICON_ROOT, 'GroupIcon.icns')
ICON_HELP = os.path.join(ICON_ROOT, 'HelpIcon.icns')
ICON_HOME = os.path.join(ICON_ROOT, 'HomeFolderIcon.icns')
ICON_INFO = os.path.join(ICON_ROOT, 'ToolbarInfo.icns')
ICON_NETWORK = os.path.join(ICON_ROOT, 'GenericNetworkIcon.icns')
ICON_NOTE = os.path.join(ICON_ROOT, 'AlertNoteIcon.icns')
ICON_SETTINGS = os.path.join(ICON_ROOT, 'ToolbarAdvanced.icns')
ICON_SWIRL = os.path.join(ICON_ROOT, 'ErasingIcon.icns')
ICON_SWITCH = os.path.join(ICON_ROOT, 'General.icns')
ICON_SYNC = os.path.join(ICON_ROOT, 'Sync.icns')
ICON_TRASH = os.path.join(ICON_ROOT, 'TrashIcon.icns')
ICON_USER = os.path.join(ICON_ROOT, 'UserIcon.icns')
ICON_WARNING = os.path.join(ICON_ROOT, 'AlertCautionIcon.icns')
ICON_WEB = os.path.join(ICON_ROOT, 'BookmarkIcon.icns')


class Item(object):
    """Represents a feedback item for Alfred.

    Generates Alfred-compliant XML for a single item.

    You probably shouldn't use this class directly, but via
    :meth:`Workflow.add_item`. See :meth:`~Workflow.add_item`
    for details of arguments.

    """

    def __init__(self, title, subtitle='', modifier_subtitles=None,
                 arg=None, autocomplete=None, valid=False, uid=None,
                 icon=None, icontype=None, type=None, largetext=None,
                 copytext=None, quicklookurl=None):
        """Same arguments as :meth:`Workflow.add_item`."""
        self.title = title
        self.subtitle = subtitle
        self.modifier_subtitles = modifier_subtitles or {}
        self.arg = arg
        self.autocomplete = autocomplete
        self.valid = valid
        self.uid = uid
        self.icon = icon
        self.icontype = icontype
        self.type = type
        self.largetext = largetext
        self.copytext = copytext
        self.quicklookurl = quicklookurl

    @property
    def elem(self):
        """Create and return feedback item for Alfred.

        :returns: :class:`ElementTree.Element <xml.etree.ElementTree.Element>`
            instance for this :class:`Item` instance.

        """
        # Attributes on <item> element
        attr = {}
        if self.valid:
            attr['valid'] = 'yes'
        else:
            attr['valid'] = 'no'
        # Allow empty string for autocomplete. This is a useful value,
        # as TABing the result will revert the query back to just the
        # keyword
        if self.autocomplete is not None:
            attr['autocomplete'] = self.autocomplete

        # Optional attributes
        for name in ('uid', 'type'):
            value = getattr(self, name, None)
            if value:
                attr[name] = value

        root = ET.Element('item', attr)
        ET.SubElement(root, 'title').text = self.title
        ET.SubElement(root, 'subtitle').text = self.subtitle

        # Add modifier subtitles
        for mod in ('cmd', 'ctrl', 'alt', 'shift', 'fn'):
            if mod in self.modifier_subtitles:
                ET.SubElement(root, 'subtitle',
                            {'mod': mod}).text = self.modifier_subtitles[mod]

        # Add arg as element instead of attribute on <item>, as it's more
        # flexible (newlines aren't allowed in attributes)
        if self.arg:
            ET.SubElement(root, 'arg').text = self.arg

        # Add icon if there is one
        if self.icon:
            if self.icontype:
                attr = dict(type=self.icontype)
            else:
                attr = {}
            ET.SubElement(root, 'icon', attr).text = self.icon

        if self.largetext:
            ET.SubElement(root, 'text',
                        {'type': 'largetype'}).text = self.largetext

        if self.copytext:
            ET.SubElement(root, 'text',
                        {'type': 'copy'}).text = self.copytext

        if self.quicklookurl:
            ET.SubElement(root, 'quicklookurl').text = self.quicklookurl

        return root



class Workflow:
    def __init__(self):
        self._items = []
        self._logger = None
        self.help_url = None
        self._debugging = None
        self._name = None
        self._bundleid = None
        self._version = None
        self._update_settings = None
        self.args = sys.argv[1:]

    def add_item(self, title, subtitle='', modifier_subtitles=None, arg=None,
                autocomplete=None, valid=False, uid=None, icon=None,
                icontype=None, type=None, largetext=None, copytext=None,
                quicklookurl=None):
        self._items.append(Item(title, subtitle, modifier_subtitles, arg,
                                autocomplete, valid, uid, icon, icontype, type,
                                largetext, copytext, quicklookurl))

    def send_feedback(self):
        """Print stored items to console/Alfred as XML."""
        root = ET.Element('items')
        for item in self._items:
            root.append(item.elem)
        sys.stdout.write('<?xml version="1.0" encoding="utf-8"?>\n')
        sys.stdout.write(ET.tostring(root).decode('utf-8'))
        sys.stdout.flush()

    def logger(self):
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
            handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)
        return self._logger