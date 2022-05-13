#! python
# coding:utf-8
"""カスタムデフォーマーノードのサンプル

デフォーマーは API2.0 非対応なので API1.0 で記述する
基底クラスは OpenMayaMPx.MPxDeformerNode
"""

import sys
import traceback

import maya.OpenMaya as om1
from maya import OpenMayaMPx

import random


def slpit_all_uv(obj):
    """全てのUVを切断する

    Args:
        obj (MDagPath): 編集対象のオブジェク
    """
    fn_mesh = om1.MFnMesh(obj)

    uvset = "map1"

    # 現在の UV
    current_us = om1.MFloatArray()
    current_vs = om1.MFloatArray()
    fn_mesh.getUVs(current_us, current_vs, uvset)

    # 新しい UV
    new_us_m = om1.MFloatArray()
    new_vs_m = om1.MFloatArray()

    # 新UVリストへ旧UV値をコピー
    comp = om1.MObject.kNullObj
    vf_itr = om1.MItMeshFaceVertex(obj)

    while not vf_itr.isDone():
        uv_id_m = om1.MScriptUtil()
        uv_id_m.createFromInt(1)
        uv_id_ptr = uv_id_m.asIntPtr()
        vf_itr.getUVIndex(uv_id_ptr, uvset)
        uv_id = om1.MScriptUtil(uv_id_ptr).asInt()

        new_us_m.append(current_us[uv_id] + random.random()*0.5)
        new_vs_m.append(current_vs[uv_id] + random.random()*0.5)

        vf_itr.next()

    # 全VFにUVアサイン
    num_vertex_per_face_m = om1.MIntArray()  # ポリゴンごとの頂点数を保存したリスト

    for fid in range(fn_mesh.numPolygons()):
        vertex_ids = om1.MIntArray()
        fn_mesh.getPolygonVertices(fid, vertex_ids)
        num_vertex_per_face_m.append(vertex_ids.length())

    uv_names = []
    fn_mesh.getUVSetNames(uv_names)

    if uvset in uv_names:
        # fn_mesh.deleteUVSet(uvset)
        pass

    # fn_mesh.createUVSet(uvset)
    num_vf = fn_mesh.numFaceVertices()
    fn_mesh.setUVs(new_us_m, new_vs_m, uvset)
    uv_indices = om1.MIntArray()
    [uv_indices.append(i) for i in range(num_vf)]
    fn_mesh.assignUVs(num_vertex_per_face_m, uv_indices, uvset)

    # API でメッシュ更新
    fn_mesh.updateSurface()


class TestDeformer(OpenMayaMPx.MPxDeformerNode):
    """頂点のY座標に対してランダムな値を足しこむデフォーマ"""
    name = "splitAllUVDeformer"
    node_id = om1.MTypeId(0x10001)  # プライベート ID は 0x00000 ～ 0x7ffff

    # 入力アトリビュート
    attr_1 = om1.MObject()

    @staticmethod
    def creator():
        """インスタンスを作成して返す"""
        return OpenMayaMPx.asMPxPtr(TestDeformer())

    @staticmethod
    def initializer():
        """プラグインロード時に 1 度呼ばれるノードの初期化処理"""
        # 入力アトリビュート
        attr = om1.MFnNumericAttribute()
        TestDeformer.attr_1 = attr.create("attribute1", "attr1", om1.MFnNumericData.kDouble, 1.0)
        attr.setKeyable(True)

        try:
            # 入力アトリビュートの追加
            TestDeformer.addAttribute(TestDeformer.attr_1)

            # 出力アトリビュート
            output_geometry = OpenMayaMPx.cvar.MPxGeometryFilter_outputGeom

            # 入力アトリビュート変更時に出力アトリビュートを再計算する設定
            TestDeformer.attributeAffects(TestDeformer.attr_1, output_geometry)

        except:
            message = "Failed to create attributes: %s" % TestDeformer.name
            sys.stderr.write(message.format(TestDeformer.name, traceback.format_exc()))

    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    def getDeformerInputGeometry(self, pDataBlock, pGeometryIndex):
        '''deform 内で入力ジオメトリを取得するヘルパ関数

        https://help.autodesk.com/view/MAYAUL/2017/JPN/?guid=__files_GUID_10CE99A6_2C32_49E1_85ED_2E2F6782CF23_htm

        Obtain a reference to the input mesh. This mesh will be used to compute our bounding box, and we will also require its normals.
        
        We use MDataBlock.outputArrayValue() to avoid having to recompute the mesh and propagate this recomputation throughout the 
        Dependency Graph.
        
        OpenMayaMPx.cvar.MPxDeformerNode_input and OpenMayaMPx.cvar.MPxDeformerNode_inputGeom (for pre Maya 2016) and 
        OpenMayaMPx.cvar.MPxGeometryFilter_input and OpenMayaMPx.cvar.MPxGeometryFilter_inputGeom (Maya 2016) are SWIG-generated 
        variables which respectively contain references to the deformer's 'input' attribute and 'inputGeom' attribute.   
        '''
        inputAttribute = OpenMayaMPx.cvar.MPxGeometryFilter_input
        inputGeometryAttribute = OpenMayaMPx.cvar.MPxGeometryFilter_inputGeom
        
        inputHandle = pDataBlock.outputArrayValue(inputAttribute)
        inputHandle.jumpToElement(pGeometryIndex)
        inputGeometryObject = inputHandle.outputValue().child(inputGeometryAttribute).asMesh()
        
        return inputGeometryObject

    def deform(self, data_block, geometry_iter, matrix, multi_index):
        """処理本体

        Args:
            data_block (MDataBlock): ノードのデータ
            geometry_iter (MItGeometry): メッシュの場合は頂点のイテレーター
            matrix (MMatrix): ワールド変換行列
            multi_index (int): 変形対象メッシュの入力インデックス
        """
        # 入力アトリビュートの取得
        handle = data_block.inputValue(self.attr_1)
        attr_1 = handle.asDouble()
        # input_geom = OpenMayaMPx.cvar.MPxGeometryFilter_inputGeom
        input_geom = self.getDeformerInputGeometry(data_block, multi_index)
        fn_mesh = om1.MFnMesh(input_geom)
        envelope = OpenMayaMPx.cvar.MPxGeometryFilter_envelope

        obj = input_geom
        slpit_all_uv(obj)


def initializePlugin(MObj_mobject):
    """プラグインロード時の処理"""
    # プラグインオブジェクト
    mplugin = OpenMayaMPx.MFnPlugin(MObj_mobject)

    try:
        mplugin.registerNode(TestDeformer.name, TestDeformer.node_id, TestDeformer.creator, TestDeformer.initializer, OpenMayaMPx.MPxNode.kDeformerNode)

    except:
        msg = "Failed to register: %s" % TestDeformer.name
        sys.stderr.write(msg.format(traceback.format_exc()))


def uninitializePlugin(MObj_mobject):
    """プラグインアンロード時の処理"""
    mplugin = OpenMayaMPx.MFnPlugin(MObj_mobject)

    try:
        mplugin.deregisterNode(TestDeformer.node_id)

    except:
        msg = "Failed to unregister: %s" % TestDeformer.name
        sys.stderr.write(msg.format(traceback.format_exc()))
