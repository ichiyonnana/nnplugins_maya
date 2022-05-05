#! python
# coding:utf-8
"""カスタムデフォーマーノードのサンプル

デフォーマーは API2.0 非対応なので API1.0 で記述する
基底クラスは OpenMayaMPx.MPxDeformerNode
"""

import sys
import traceback
from maya import OpenMaya
from maya import OpenMayaMPx

import random


class TestDeformer(OpenMayaMPx.MPxDeformerNode):
    """頂点のY座標に対してランダムな値を足しこむデフォーマ"""
    name = "testDeformer"
    node_id = OpenMaya.MTypeId(0x10000)  # プライベート ID は 0x00000 ～ 0x7ffff

    # 入力アトリビュート
    attr_1 = OpenMaya.MObject()

    @staticmethod
    def creator():
        """インスタンスを作成して返す"""
        return OpenMayaMPx.asMPxPtr(TestDeformer())

    @staticmethod
    def initializer():
        """プラグインロード時に 1 度呼ばれるノードの初期化処理"""
        # 入力アトリビュート
        attr = OpenMaya.MFnNumericAttribute()
        TestDeformer.attr_1 = attr.create("attribute1", "attr1", OpenMaya.MFnNumericData.kDouble, 1.0)
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
        mfn_mesh = OpenMaya.MFnMesh(input_geom)
        envelope = OpenMayaMPx.cvar.MPxGeometryFilter_envelope

        # 変形処理
        while not geometry_iter.isDone():
            # 新しい位置の計算
            current_point = geometry_iter.position()
            new_point = OpenMaya.MPoint()
            new_point.x = current_point.x * attr_1
            new_point.y = current_point.y / attr_1
            new_point.z = current_point.z + 1

            # 出力頂点への反映
            geometry_iter.setPosition(new_point)

            geometry_iter.next()


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
