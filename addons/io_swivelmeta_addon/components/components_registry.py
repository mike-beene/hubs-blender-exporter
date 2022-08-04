from .types import NodeType
import bpy.utils.previews
import bpy
from bpy.props import BoolProperty, StringProperty, CollectionProperty, PointerProperty
from bpy.types import PropertyGroup

import importlib
import inspect
import os
from os import listdir
from os.path import join, isfile, isdir, dirname, realpath

from .swivelmeta_component import SwivelMetaComponent


class SwivelMetaComponentName(PropertyGroup):
    # For backwards compatibility reasons this attribute is called "name" but it actually points to the component id
    name: StringProperty(name="name")
    expanded: BoolProperty(name="expanded", default=True)


class SwivelMetaComponentList(PropertyGroup):
    items: CollectionProperty(type=SwivelMetaComponentName)


def get_components_in_dir(dir):
    components = []
    for f in os.listdir(dir):
        f_path = join(dir, f)
        if isfile(f_path) and f.endswith(".py"):
            components.append(f[:-3])
        elif isdir(f_path) and f != "__pycache__":
            comps = [f + '.' + name for name in get_components_in_dir(f_path)]
            components = components + comps
    return sorted(components)


def get_component_definitions():
    components_dir = join(dirname(realpath(__file__)), "definitions")
    component_module_names = get_components_in_dir(components_dir)
    return [
        importlib.import_module(".definitions." + name, package=__package__)
        for name in component_module_names
    ]


def register_component(component_class):
    print("Registering component: " + component_class.get_name())
    bpy.utils.register_class(component_class)

    component_id = component_class.get_id()
    if component_class.get_node_type() == NodeType.SCENE:
        setattr(
            bpy.types.Scene,
            component_id,
            PointerProperty(type=component_class)
        )
    elif component_class.get_node_type() == NodeType.NODE:
        setattr(
            bpy.types.Object,
            component_id,
            PointerProperty(type=component_class)
        )
        setattr(
            bpy.types.Bone,
            component_id,
            PointerProperty(type=component_class)
        )
        setattr(
            bpy.types.EditBone,
            component_id,
            PointerProperty(type=component_class)
        )
    elif component_class.get_node_type() == NodeType.MATERIAL:
        setattr(
            bpy.types.Material,
            component_id,
            PointerProperty(type=component_class)
        )


def unregister_component(component_class):
    component_id = component_class.get_id()
    if component_class.get_node_type() == NodeType.SCENE:
        delattr(bpy.types.Scene, component_id)
    elif component_class.get_node_type() == NodeType.NODE:
        delattr(bpy.types.Object, component_id)
        delattr(bpy.types.Bone, component_id)
        delattr(bpy.types.EditBone, component_id)
    elif component_class.get_node_type() == NodeType.MATERIAL:
        delattr(bpy.types.Material, component_id)

    bpy.utils.unregister_class(component_class)

    print("Component unregistered: " + component_class.get_name())


def load_components_registry():
    """Recurse in the components directory to build the components registry"""
    global __components_registry
    __components_registry = {}
    for module in get_component_definitions():
        for _, member in inspect.getmembers(module):
            if inspect.isclass(member) and issubclass(member, SwivelMetaComponent) and member != SwivelMetaComponent:
                register_component(member)
                __components_registry[member.get_name()] = member


def unload_components_registry():
    """Recurse in the components directory to unload the registered components"""
    global __components_registry
    for _, component_class in __components_registry.items():
        unregister_component(component_class)


def load_icons():
    global __component_icons
    __component_icons = {}
    pcoll = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    icons = [f for f in listdir(icons_dir) if isfile(join(icons_dir, f))]
    for icon in icons:
        pcoll.load(icon, os.path.join(icons_dir, icon), 'IMAGE')
        print("Loading icon: " + icon)
    __component_icons["swivelmeta"] = pcoll


def unload_icons():
    global __component_icons
    __component_icons["swivelmeta"].close()
    del __component_icons


__component_icons = {}
__components_registry = {}


def get_components_registry():
    global __components_registry
    return __components_registry


def get_components_icons():
    global __component_icons
    return __component_icons["swivelmeta"]


def get_component_by_name(component_name):
    global __components_registry
    return next((component_class for _, component_class in __components_registry.items() if component_class.get_name() == component_name), None)


def register():
    load_icons()
    load_components_registry()

    bpy.utils.register_class(SwivelMetaComponentName)
    bpy.utils.register_class(SwivelMetaComponentList)

    bpy.types.Object.swivelmeta_component_list = PointerProperty(
        type=SwivelMetaComponentList)
    bpy.types.Scene.swivelmeta_component_list = PointerProperty(
        type=SwivelMetaComponentList)
    bpy.types.Material.swivelmeta_component_list = PointerProperty(
        type=SwivelMetaComponentList)
    bpy.types.Bone.swivelmeta_component_list = PointerProperty(
        type=SwivelMetaComponentList)
    bpy.types.EditBone.swivelmeta_component_list = PointerProperty(
        type=SwivelMetaComponentList)


def unregister():
    del bpy.types.Object.swivelmeta_component_list
    del bpy.types.Scene.swivelmeta_component_list
    del bpy.types.Material.swivelmeta_component_list
    del bpy.types.Bone.swivelmeta_component_list
    del bpy.types.EditBone.swivelmeta_component_list

    bpy.utils.unregister_class(SwivelMetaComponentName)
    bpy.utils.unregister_class(SwivelMetaComponentList)

    unload_components_registry()
    unload_icons()

    global __components_registry
    del __components_registry