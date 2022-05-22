#! python
# coding:utf-8
"""カスタムノードサンプル

入力アトリビュートを出力アトリビュートに流すだけ
"""

import sys
import traceback

import maya.api.OpenMaya as om


def maya_useNewAPI():
    """プラグインが API2.0 ベースであることの明示"""
    pass


class TestNode(om.MPxNode):
    """コマンドクラス"""
    name = "testNode"
    id = om.MTypeId(0x10001)  # プライベート ID は 0x00000 ～ 0x7ffff
    classify = "utility/general"

    # 入力アトリビュート
    attr_single = om.MObject()
    attr_plugarray = om.MObject()
    attr_array = om.MObject()
    attr_child1 = om.MObject()
    attr_child2 = om.MObject()
    attr_compound = om.MObject()

    # 出力アトリビュート
    output = om.MObject()

    @staticmethod
    def creator():
        """インスタンスを作成して返す"""
        return TestNode()

    @staticmethod
    def initialize():
        """プラグインロード時に 1 度呼ばれるノードの初期化処理"""

        # 実数アトリビュート
        attr = om.MFnNumericAttribute()
        TestNode.attr_single = attr.create("attr_single", "f", om.MFnNumericData.kFloat, 0.0)
        attr.storable = True
        attr.writable = True
        attr.readable = True
        attr.setMin(0.0)
        attr.setMax(1.0)

        # 配列プラグ 実数アトリビュート
        attr = om.MFnNumericAttribute()
        TestNode.attr_plugarray = attr.create("attr_plugarray", "a", om.MFnNumericData.kFloat, 0.0)
        attr.storable = True
        attr.writable = True
        attr.readable = True
        attr.array = True  # 配列プラグアトリビュート
        attr.indexMatters = False  # nextAvailable 使用可

        # 実数配列アトリビュート
        attr = om.MFnNumericAttribute()
        TestNode.attr_array = attr.create("attr_array", "f3", om.MFnNumericData.k3Float, 0.0)
        attr.readable = True

        # 複合アトリビュート
        # 子アトリビュート1 (単一アトリビュート)
        attr = om.MFnNumericAttribute()
        TestNode.attr_child1 = attr.create("attr_child1", "c1", om.MFnNumericData.kFloat, 0.0)
        attr.storable = True
        attr.writable = True
        attr.readable = True

        # 子アトリビュート2 (単一アトリビュート)
        attr = om.MFnNumericAttribute()
        TestNode.attr_child2 = attr.create("attr_child2", "c2", om.MFnNumericData.kFloat, 0.0)
        attr.storable = True
        attr.writable = True
        attr.readable = True

        # 親アトリビュート (複合アトリビュート)
        attr = om.MFnCompoundAttribute()
        TestNode.attr_compound = attr.create("attr_compound", "comp")
        attr.readable = True
        attr.array = True
        attr.indexMatters = False
        attr.addChild(TestNode.attr_child1)
        attr.addChild(TestNode.attr_child2)

        # メッセージ
        fn_attr = om.MFnMessageAttribute()
        TestNode.src_mesh_attr = fn_attr.create("in_message", "im")
        fn_attr.writable =  True 
        fn_attr.readable = False 
        fn_attr.storable =  True 
        fn_attr.hidden = False 
        TestNode.addAttribute(TestNode.src_mesh_attr)

        fn_attr = om.MFnMessageAttribute()
        TestNode.dst_mesh_attr = fn_attr.create("out_message", "om")
        fn_attr.writable =  True 
        fn_attr.readable = False 
        fn_attr.storable =  True 
        fn_attr.hidden = False 
        TestNode.addAttribute(TestNode.dst_mesh_attr)


        # 出力アトリビュート
        attr = om.MFnNumericAttribute()
        TestNode.output = attr.create("output_attr", "o", om.MFnNumericData.kFloat, 0.0)
        attr.storable = True
        attr.writable = True

        # ノードへアトリビュートを追加
        TestNode.addAttribute(TestNode.attr_single)
        TestNode.addAttribute(TestNode.attr_plugarray)
        TestNode.addAttribute(TestNode.attr_array)
        TestNode.addAttribute(TestNode.attr_compound)
        TestNode.addAttribute(TestNode.output)

        # 入力アトリビュート変更時に出力アトリビュートを再計算する設定
        TestNode.attributeAffects(TestNode.attr_single, TestNode.output)
        TestNode.attributeAffects(TestNode.attr_plugarray, TestNode.output)
        TestNode.attributeAffects(TestNode.attr_array, TestNode.output)
        TestNode.attributeAffects(TestNode.attr_compound, TestNode.output)

    def compute(self, plug, data):
        """ノード内の処理本体

        Args:
            plug (_type_): 再計算要求のあったプラグ
            data (_type_): ノードのデータ
        """
        # アウトプットの再計算要求された場合のみ
        if plug == TestNode.output:
            # 配列プラグアトリビュートの値取得
            array_handle = data.inputArrayValue(TestNode.attr_plugarray)
            a = []
            while not array_handle.isDone():
                v = array_handle.inputValue().asFloat()
                a.append(v)
                array_handle.next()

            # 複合アトリビュートの値取得
            array_handle = data.inputArrayValue(TestNode.attr_compound)
            a = []
            while not array_handle.isDone():
                handle = array_handle.inputValue()
                child_handle1 = handle.child(TestNode.attr_child1)
                child_handle2 = handle.child(TestNode.attr_child2)
                v1 = child_handle1.asFloat()
                v2 = child_handle2.asFloat()
                a.append((v1, v2))
                array_handle.next()

            # 実数アトリビュートの値取得
            handle = data.inputValue(TestNode.attr_single)
            v1 = handle.asFloat()

            # 配列アトリビュートの値取得
            handle = data.inputValue(TestNode.attr_array)
            v = handle.asFloat3()
            v[0]
            v[1]
            v[2]

            result = v1

            outputHandle = data.outputValue(TestNode.output)
            outputHandle.setFloat(result)

            # 再計算されたされたことを明示
            data.setClean(plug)


def initializePlugin(mobject):
    """プラグインロード時の処理"""
    # プラグインオブジェクト
    mplugin = om.MFnPlugin(mobject)

    # 登録
    try:
        mplugin.registerNode(TestNode.name, TestNode.id, TestNode.creator, TestNode.initialize, om.MPxNode.kDependNode)

    except:
        message = "Failed to register: %s" % TestNode.name
        sys.stderr.write(message.format(traceback.format_exc()))


def uninitializePlugin(mobject):
    """プラグインアンロード時の処理"""
    # プラグインオブジェクト
    mplugin = om.MFnPlugin(mobject)

    # 削除
    try:
        mplugin.deregisterNode(TestNode.id)

    except:
        message = "Failed to unregister: %s" % TestNode.name
        sys.stderr.write(message.format(traceback.format_exc()))
