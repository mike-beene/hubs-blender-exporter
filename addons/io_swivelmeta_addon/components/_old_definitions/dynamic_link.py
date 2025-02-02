from bpy.props import StringProperty
from ..swivelmeta_component import SwivelMetaComponent
from ..types import Category, PanelType, NodeType


class DynamicLink(SwivelMetaComponent):
    _definition = {
        'name': 'dynamic-link',
        'display_name': 'Dynamic Link',
        'category': Category.MIXER,
        'node_type': NodeType.NODE,
        'panel_type': [PanelType.OBJECT],
        'icon': 'LINKED'
    }

    id: StringProperty(
        name="ID",
        description="Unique identifier for use in the SwivelMeta Mixer app. Should only contain alphanumeric characters",
        default=""
    )

    name: StringProperty(
        name="Name",
        description="Name of link as shown in SwivelMeta Builder app",
        default=""
    )

    description: StringProperty(
        name="Description",
        description="Description of link as shown in SwivelMeta Builder app",
        default=""
    )

    url: StringProperty(
        name="Link URL",
        description="Default URL the link should point to",
        default="https://"
    )
