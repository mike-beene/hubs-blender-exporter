from bpy.props import StringProperty
from bpy.types import Node
from ..hubs_component import HubsComponent
from ..types import Category, PanelType


class Link(HubsComponent):
    _definition = {
        'name': 'link',
        'display_name': 'Link',
        'category': Category.ELEMENTS,
        'node_type': Node,
        'panel_type': PanelType.OBJECT,
        'icon': 'LINKED',
        'deps': ['networked']
    }

    href: StringProperty(name="URL", description="URL",
                         default="https://mozilla.org")
