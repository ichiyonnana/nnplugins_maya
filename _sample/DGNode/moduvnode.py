#! python
# coding:utf-8
"""カスタムノードサンプル"""

import sys
import traceback
import random

import maya.api.OpenMaya as om


def maya_useNewAPI():
    """プラグインが API2.0 ベースであることの明示"""
    pass


class TestNode(om.MPxNode):
    """コマンドクラス"""
    name = "modUVNode"
    id = om.MTypeId(0x10003)  # プライベート ID は 0x00000 ～ 0x7ffff

    # アトリビュート
    input_test = None
    input_mesh = None

    output_mesh = None

    @staticmethod
    def creator():
        """インスタンスを作成して返す"""
        return TestNode()

    @staticmethod
    def initialize():
        """プラグインロード時に 1 度呼ばれるノードの初期化処理"""

        fn_attr = om.MFnNumericAttribute()
        TestNode.input_test = fn_attr.create("test", "t", om.MFnNumericData.kFloat)
        fn_attr.writable = True
        fn_attr.readable = False
        fn_attr.storable = True
        fn_attr.hidden = False
        TestNode.addAttribute(TestNode.input_test)

        fn_attr = om.MFnTypedAttribute()
        TestNode.input_mesh = fn_attr.create("inputMesh", "im", om.MFnData.kMesh)
        fn_attr.writable = True
        fn_attr.readable = False
        fn_attr.storable = False
        fn_attr.hidden = False
        TestNode.addAttribute(TestNode.input_mesh)

        # 出力アトリビュート
        fn_attr = om.MFnTypedAttribute()
        TestNode.output_mesh = fn_attr.create("outputMesh", "om", om.MFnData.kMesh)
        fn_attr.writable = False
        fn_attr.readable = True
        fn_attr.storable = False
        fn_attr.hidden = False
        TestNode.addAttribute(TestNode.output_mesh)

        # アトリビュートの依存関係
        TestNode.attributeAffects(TestNode.input_test, TestNode.output_mesh)
        TestNode.attributeAffects(TestNode.input_mesh, TestNode.output_mesh)

    def compute(self, plug, dataBlock):
        """ノード内の処理本体

        Args:
            plug (_type_): 再計算要求のあったプラグ
            data (_type_): ノードのデータ
        """
        print("compute")

        # 出力ジオメトリの再計算
        if plug.attribute() == TestNode.output_mesh:
            print("update out mesh")
            handle = dataBlock.inputValue(TestNode.input_mesh)
            inmesh = handle.asMesh()

            # 入力メッシュの情報取得
            fn_mesh = om.MFnMesh(inmesh)

            # 出力メッシュのデータ構築
            output_mesh_data = om.MFnMeshData().create()
            fn_mesh.copy(inmesh, output_mesh_data)
            fn_outmesh = om.MFnMesh(output_mesh_data)

            # メッシュの編集
            fn_outmesh.setUV(0, random.random(), random.random())
            uv_counts, uv_ids = fn_outmesh.getAssignedUVs()
            fn_outmesh.assignUVs(uv_counts, uv_ids)
            fn_outmesh.setPoint(0, om.MPoint(random.random(), random.random()))
            fn_outmesh.updateSurface()

            # 出力プラグの値更新
            handle = dataBlock.outputValue(TestNode.output_mesh)
            handle.setMObject(output_mesh_data)

            # ダーティー解除
            dataBlock.setClean(plug)


def initializePlugin(mobject):
    """プラグインロード時の処理"""
    # プラグインオブジェクト
    mplugin = om.MFnPlugin(mobject)

    # 登録
    try:
        mplugin.registerNode(TestNode.name, TestNode.id, TestNode.creator, TestNode.initialize, om.MPxNode.kDependNode)

        message = "register: %s\n" % TestNode.name
        sys.stderr.write(message.format(traceback.format_exc()))

    except:
        message = "Failed to register: %s\n" % TestNode.name
        sys.stderr.write(message.format(traceback.format_exc()))


def uninitializePlugin(mobject):
    """プラグインアンロード時の処理"""
    # プラグインオブジェクト
    mplugin = om.MFnPlugin(mobject)

    # 削除
    try:
        mplugin.deregisterNode(TestNode.id)

        message = "deregister: %s\n" % TestNode.name
        sys.stderr.write(message.format(traceback.format_exc()))

    except:
        message = "Failed to unregister: %s\n" % TestNode.name
        sys.stderr.write(message.format(traceback.format_exc()))
