from bpy.props import StringProperty
from ..swivelmeta_component import SwivelMetaComponent
from ..types import Category, PanelType, NodeType


class ShopifyProductModel(SwivelMetaComponent):
    _definition = {
        'name': 'shopify-color-palette',
        'display_name': 'Shopify Color Palette',
        'category': Category.ECOMMERCE,
        'node_type': NodeType.NODE,
        'panel_type': [PanelType.OBJECT],
        'icon': 'MATERIAL'
    }

    primaryColorKey: StringProperty(
        name="Primary color",
        description="Name of material to be replaced with vendor primary color (optional)",
        default=""
    )

    secondaryColorKey: StringProperty(
        name="Secondary color",
        description="Name of material to be replaced with vendor secondary color (optional)",
        default=""
    )

    tertiaryColorKey: StringProperty(
        name="Tertiary color",
        description="Name of material to be replaced with vendor tertiary color (optional)",
        default=""
    )