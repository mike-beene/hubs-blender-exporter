from ..swivelmeta_component import SwivelMetaComponent
from ..types import Category, PanelType, NodeType
from bpy.types import Object


class PresentationFrame(SwivelMetaComponent):
    _definition = {
        'name': 'presentation-frame',
        'display_name': 'Presentation Frame',
        'category': Category.UTILITIES,
        'node_type': NodeType.NODE,
        'panel_type': [PanelType.OBJECT],
        'icon': 'RESTRICT_VIEW_OFF'
    }