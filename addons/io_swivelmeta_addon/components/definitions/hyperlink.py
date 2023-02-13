from ..swivelmeta_component import SwivelMetaComponent
from ..types import Category, PanelType, NodeType
from bpy.props import StringProperty
from bpy.types import Object


class IntraRoomTeleport(SwivelMetaComponent):
    _definition = {
        'name': 'hyperlink',
        'display_name': 'Hyperlink',
        'category': Category.MEDIA,
        'node_type': NodeType.NODE,
        'panel_type': [PanelType.OBJECT],
        'icon': 'LIBRARY_DATA_DIRECT'
    }

    url: StringProperty(
        name="Link URL",
        description="Link URL",
        default="https://"
    )