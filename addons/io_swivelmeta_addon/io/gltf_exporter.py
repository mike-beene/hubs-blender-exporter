from io_scene_gltf2.io.exp.gltf2_io_user_extensions import export_user_extensions
from io_scene_gltf2.blender.exp import gltf2_blender_export
import bpy
from bpy.props import PointerProperty, IntVectorProperty
from ..components.components_registry import get_components_registry
# from .utils import gather_lightmap_texture_info

swivelmeta_config = {
    "gltfExtensionName": "SM_components",
    "gltfExtensionVersion": 4,
}


def get_version_string():
    from .. import (bl_info)
    return str(bl_info['version'][0]) + '.' + str(bl_info['version'][1]) + '.' + str(bl_info['version'][2])


# gather_gltf_hook does not expose the info we need, make a custom hook for now
# ideally we can resolve this upstream somehow https://github.com/KhronosGroup/glTF-Blender-IO/issues/1009
orig_gather_gltf = gltf2_blender_export.__gather_gltf


def glTF2_pre_export_callback(export_settings):
    for ob in bpy.context.view_layer.objects:
        component_list = ob.swivelmeta_component_list

        registered_swivelmeta_components = get_components_registry()

        if component_list.items:
            for component_item in component_list.items:
                component_name = component_item.name
                if component_name in registered_swivelmeta_components:
                    component_class = registered_swivelmeta_components[component_name]
                    component = getattr(ob, component_class.get_id())
                    component.pre_export(export_settings, ob)


def glTF2_post_export_callback(export_settings):
    for ob in bpy.context.view_layer.objects:
        component_list = ob.swivelmeta_component_list

        registered_swivelmeta_components = get_components_registry()

        if component_list.items:
            for component_item in component_list.items:
                component_name = component_item.name
                if component_name in registered_swivelmeta_components:
                    component_class = registered_swivelmeta_components[component_name]
                    component = getattr(ob, component_class.get_id())
                    component.post_export(export_settings, ob)


def patched_gather_gltf(exporter, export_settings):
    orig_gather_gltf(exporter, export_settings)
    export_user_extensions('swivelmeta_gather_gltf_hook',
                           export_settings, exporter._GlTF2Exporter__gltf)
    exporter._GlTF2Exporter__traverse(exporter._GlTF2Exporter__gltf.extensions)

# This class name is specifically looked for by gltf-blender-io and it's hooks are automatically invoked on export


class glTF2ExportUserExtension:
    def __init__(self):
        # We need to wait until we create the gltf2UserExtension to import the gltf2 modules
        # Otherwise, it may fail because the gltf2 may not be loaded yet
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension

        self.Extension = Extension
        self.properties = bpy.context.scene.SwivelMetaComponentsExtensionProperties
        self.was_used = False

    def swivelmeta_gather_gltf_hook(self, gltf2_object, export_settings):
        if not self.properties.enabled or not self.was_used:
            return

        extension_name = swivelmeta_config["gltfExtensionName"]
        gltf2_object.extensions[extension_name] = self.Extension(
            name=extension_name,
            extension={
                "version": swivelmeta_config["gltfExtensionVersion"],
                "exporterVersion": get_version_string()
            },
            required=False
        )

        if gltf2_object.asset.extras is None:
            gltf2_object.asset.extras = {}
        gltf2_object.asset.extras["SM_blenderExporterVersion"] = get_version_string(
        )

    def gather_scene_hook(self, gltf2_object, blender_scene, export_settings):
        if not self.properties.enabled:
            return

        # Don't include hubs component data again in extras, even if "include custom properties" is enabled
        if gltf2_object.extras:
            for key in list(gltf2_object.extras):
                if key.startswith("swivelmeta_"):
                    del gltf2_object.extras[key]

        self.add_swivelmeta_components(gltf2_object, blender_scene, export_settings)

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if not self.properties.enabled:
            return

        # Don't include hubs component data again in extras, even if "include custom properties" is enabled
        if gltf2_object.extras:
            for key in list(gltf2_object.extras):
                if key.startswith("swivelmeta_"):
                    del gltf2_object.extras[key]

        self.add_swivelmeta_components(gltf2_object, blender_object, export_settings)

    def gather_material_hook(self, gltf2_object, blender_material, export_settings):
        if not self.properties.enabled:
            return

        self.add_swivelmeta_components(
            gltf2_object, blender_material, export_settings)

        # if blender_material.node_tree and blender_material.use_nodes:
        #     lightmap_texture_info = gather_lightmap_texture_info(
        #         blender_material, export_settings)
        #     if lightmap_texture_info:
        #         gltf2_object.extensions["MOZ_lightmap"] = self.Extension(
        #             name="MOZ_lightmap",
        #             extension=lightmap_texture_info,
        #             required=False,
        #         )

    def gather_material_unlit_hook(self, gltf2_object, blender_material, export_settings):
        self.gather_material_hook(
            gltf2_object, blender_material, export_settings)

    def gather_joint_hook(self, gltf2_object, blender_pose_bone, export_settings):
        if not self.properties.enabled:
            return
        self.add_swivelmeta_components(
            gltf2_object, blender_pose_bone.bone, export_settings)

    def add_swivelmeta_components(self, gltf2_object, blender_object, export_settings):
        component_list = blender_object.swivelmeta_component_list

        registered_swivelmeta_components = get_components_registry()

        if component_list.items:
            extension_name = swivelmeta_config["gltfExtensionName"]
            component_data = {}

            for component_item in component_list.items:
                component_name = component_item.name
                if component_name in registered_swivelmeta_components:
                    component_class = registered_swivelmeta_components[component_name]
                    component = getattr(
                        blender_object, component_class.get_id())
                    component_data[component_class.get_name()] = component.gather(
                        export_settings, blender_object)
                else:
                    print('Could not export unsupported component "%s"' %
                          (component_name))

            if gltf2_object.extensions is None:
                gltf2_object.extensions = {}
            gltf2_object.extensions[extension_name] = self.Extension(
                name=extension_name,
                extension=component_data,
                required=False
            )

            self.was_used = True


class SwivelMetaComponentsExtensionProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="Export SwivelMeta Components",
        description='Include this extension in the exported glTF file.',
        default=True
    )
    version: IntVectorProperty(size=3)


class SwivelMetaGLTFExportPanel(bpy.types.Panel):

    bl_idname = "SMBA_PT_Export_Panel"
    bl_label = "SwivelMeta Export Panel"
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "SwivelMeta Components"
    bl_parent_id = "GLTF_PT_export_user_extensions"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXPORT_SCENE_OT_gltf"

    def draw_header(self, context):
        props = bpy.context.scene.SwivelMetaComponentsExtensionProperties
        self.layout.prop(props, 'enabled', text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        props = bpy.context.scene.SwivelMetaComponentsExtensionProperties
        layout.active = props.enabled

        box = layout.box()
        box.label(text="No options yet")

# called by gltf-blender-io after it has loaded


def register_export_panel():
    try:
        bpy.utils.register_class(SwivelMetaGLTFExportPanel)
    except Exception:
        pass
    return unregister_export_panel


def unregister_export_panel():
    # Since panel is registered on demand, it is possible it is not registered
    try:
        bpy.utils.unregister_class(SwivelMetaGLTFExportPanel)
    except Exception:
        pass


def register():
    print("Register GLTF Exporter")
    register_export_panel()
    gltf2_blender_export.__gather_gltf = patched_gather_gltf
    bpy.utils.register_class(SwivelMetaComponentsExtensionProperties)
    bpy.types.Scene.SwivelMetaComponentsExtensionProperties = PointerProperty(
        type=SwivelMetaComponentsExtensionProperties)


def unregister():
    print("Unregister GLTF Exporter")
    unregister_export_panel()
    del bpy.types.Scene.SwivelMetaComponentsExtensionProperties
    bpy.utils.unregister_class(SwivelMetaComponentsExtensionProperties)
    gltf2_blender_export.__gather_gltf = orig_gather_gltf
    unregister_export_panel()
