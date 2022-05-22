#! python
# coding:utf-8
"""カスタムデフォーマーノードのサンプル

deform メソッドではなく compute を使用する場合

デフォーマーは API2.0 非対応なので API1.0 で記述する
"""

import sys
import traceback
import random

from maya import OpenMaya
from maya import OpenMayaMPx


class TestDeformer(OpenMayaMPx.MPxDeformerNode):
    """頂点のY座標に対してランダムな値を足しこむデフォーマ"""
    name = "testDeformer"
    node_id = OpenMaya.MTypeId(0x10000)  # プライベート ID は 0x00000 ～ 0x7ffff

    # 入力アトリビュート
    num_attr = None

    # 出力アトリビュート
    outmesh_attr = None

    @staticmethod
    def creator():
        """インスタンスを作成して返す"""
        return OpenMayaMPx.asMPxPtr(TestDeformer())

    @staticmethod
    def initializer():
        """プラグインロード時に 1 度呼ばれるノードの初期化処理"""

        try:
            # 入力アトリビュート1
            attr = OpenMaya.MFnNumericAttribute()
            TestDeformer.num_attr = attr.create("numAttr", "n", OpenMaya.MFnNumericData.kDouble, 1.0)
            attr.setReadable(False)
            attr.setWritable(True)
            TestDeformer.addAttribute(TestDeformer.num_attr)

            # 出力アトリビュート
            TestDeformer.outmesh_attr = OpenMayaMPx.cvar.MPxGeometryFilter_outputGeom

            # アトリビュート間の依存関係
            TestDeformer.attributeAffects(TestDeformer.num_attr, TestDeformer.outmesh_attr)

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

    def compute(self, plug, dataBlock):
        # 出力ジオメトリ (複数ある OutputGeometry のうちのひとつ) の再計算
        if plug.attribute() == TestDeformer.outmesh_attr:
            # 入力アトリビュートの取得
            handle = dataBlock.inputValue(self.num_attr)
            num = handle.asDouble()

            # ノードと Output Geometry 配列 のインデックス取得
            logical_index = plug.logicalIndex()
            thisNode = self.thisMObject()

            # デフォーマーの持つ input[] アトリビュートの取得
            input_attr = OpenMayaMPx.cvar.MPxGeometryFilter_input  # input[] アトリビュート
            inPlug = OpenMaya.MPlug(thisNode, input_attr)  # input[] プラグ
            inPlug.selectAncestorLogicalIndex(logical_index, input_attr)  # 出力メッシュに対応する input[i] のプラグ
            hInput = dataBlock.inputValue(inPlug)  # input[i] のハンドル

            # input[i].inputGeometry の取得
            inputGeomAttr = OpenMayaMPx.cvar.MPxGeometryFilter_inputGeom
            hGeom = hInput.child(inputGeomAttr)
            geom = hGeom.asMesh()

            # input[i].groupId の取得
            groupIdAttr = OpenMayaMPx.cvar.MPxGeometryFilter_groupId
            hGroup = hInput.child(groupIdAttr)
            groupId = hGroup.asLong()

            # 出力メッシュのハンドル取得して入力メッシュをコピー
            hOutput = dataBlock.outputValue(plug)
            hOutput.copy(hGeom)

            geometry_iter = OpenMaya.MItGeometry(hOutput, groupId, False)

            while not geometry_iter.isDone():
                # 変形処理
                current_point = geometry_iter.position()

                new_point = OpenMaya.MPoint()
                new_point.x = current_point.x + random.random() * num
                new_point.y = current_point.y + random.random() * num
                new_point.z = current_point.z + random.random() * num

                # 出力頂点への反映
                geometry_iter.setPosition(new_point)

                geometry_iter.next()

            dataBlock.setClean(plug)


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
