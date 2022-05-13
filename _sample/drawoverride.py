# -*- coding: utf-8 -*-

# http://hesperas.blog134.fc2.com/blog-entry-251.html

import sys

import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI
import maya.api.OpenMayaRender as OpenMayaRender

def maya_useNewAPI():
    pass

#=========================================
class DrawOverride( OpenMayaUI.MPxLocatorNode ):
    
    # ノードのアトリビュート名
    kPluginNodeTypeName = "DrawOverride"
    
    #TypeIDを入れる
    NodeId = OpenMaya.MTypeId(0x80011)#ユニークID
    
    #オーバーライド用のID
    classfication = 'drawdb/geometry/DrawOverride'
    registrantId = 'DrawOverridePlugin'
    
    #-----------------------------------------------
    def __init__(self):
        OpenMayaUI.MPxLocatorNode.__init__(self)
    
    #-----------------------------------------------
    def draw( self, view, path, style, status ):
        pass
    
    #-----------------------------------------------
    def isBounded( self ):
        return True
    
    #-----------------------------------------------
    def boundingBox( self ):
    
        return OpenMaya.MBoundingBox( OpenMaya.MPoint( 1.0, 1.0, 1.0 ), 
        OpenMaya.MPoint( -1.0, -1.0, -1.0 ) )
    
    #-----------------------------------------------
    # creator
    @staticmethod
    def nodeCreator():
        return DrawOverride()
    
    #-----------------------------------------------
    # initializer
    @staticmethod
    def nodeInitializer():
    
        # アトリビュートの種類の定義
        fnCompAttr = OpenMaya.MFnCompoundAttribute()
        fnMessageAttr = OpenMaya.MFnMessageAttribute()
        typedAttr = OpenMaya.MFnTypedAttribute()
        fnNumericAttr = OpenMaya.MFnNumericAttribute()

        # 描画を実行するチェックのブールアトリビュート
        DrawOverride.abool = fnNumericAttr.create( 'bool', 'bl', OpenMaya.MFnNumericData.kBoolean)
        fnNumericAttr.writable = True
        fnNumericAttr.keyable = True
        
        # ベースメッシュ用のアトリビュート
        typedAttr = OpenMaya.MFnTypedAttribute()
        DrawOverride.baseinput = typedAttr.create('baseinput', 'baseinputMesh', OpenMaya.MFnData.kMesh)
        typedAttr.writable = True
        typedAttr.keyable = True
        
        
        # ターゲットメッシュ用のアトリビュート
        DrawOverride.input = typedAttr.create('input', 'inputMesh', OpenMaya.MFnData.kMesh)
        typedAttr.writable = True
        typedAttr.keyable = True
        
        # アトリビュートをセットする
        DrawOverride.addAttribute( DrawOverride.abool ) 
        DrawOverride.addAttribute( DrawOverride.baseinput )
        DrawOverride.addAttribute( DrawOverride.input )

        
        return True
        
        
#=========================================
class UserData( OpenMaya.MUserData ):

    #DrawOverrideに渡すデータ

    size = 0.0
    #-----------------------------------------------
    def __init__( self ):
        OpenMaya.MUserData.__init__( self, False )
        self.datas = []
        self.basedatas = []
#=========================================
class DrawOverrideOverride( OpenMayaRender.MPxDrawOverride ):
    
    #-----------------------------------------------
    def __init__( self, obj ):
        OpenMayaRender.MPxDrawOverride.__init__( self, obj, DrawOverrideOverride.draw )
    
    #-----------------------------------------------
    @staticmethod
    def draw( context, data ):
        pass
    
    #-----------------------------------------------
    def supportedDrawAPIs( self ):

        #DirectXを使用して描画うsる
        return OpenMayaRender.MRenderer.kDirectX11
    
    #-----------------------------------------------
    def hasUIDrawables( self ):
        return True
    
    #-----------------------------------------------
    def isBounded( self, objPath, cameraPath ):
        return True
    
    #-----------------------------------------------
    def boundingBox( self, objPath, cameraPath ):
    
        boxsize = 10000.0
        bbox = OpenMaya.MBoundingBox(OpenMaya.MPoint(boxsize, boxsize, boxsize),
        OpenMaya.MPoint(-boxsize, -boxsize, -boxsize))
    
        return bbox
    #-----------------------------------------------
    def disableInternalBoundingBoxDraw( self ):
        return True
    
    #-----------------------------------------------
    def prepareForDraw( self, objPath, cameraPath, frameContext, oldData ):

        # データ更新処理
        if( objPath ):
            newData = None
            if( oldData ):
                newData = oldData
                newData.datas = []
            else:
                newData = UserData()
            
            # 自信のロケータの情報を読み込む
            thisNode = objPath.node()
            fnNode = OpenMaya.MFnDependencyNode( thisNode )
            fnDagNode = OpenMaya.MFnDagNode( thisNode )
            
            # boolプラグからデータを読み込み、Trueならば実行
            boolPlug = fnNode.findPlug( 'bool', False ).asBool()
            if boolPlug == True:
                meshPlug = fnNode.findPlug( 'input', False ).asMObject()
                oMesh = OpenMaya.MFnMesh(meshPlug)
                
                baseMeshPlug = fnNode.findPlug( 'baseinput', False ).asMObject()
                oBaseMesh = OpenMaya.MFnMesh(baseMeshPlug)

                # ベースのメッシュとターゲットのメッシュの頂点の位置情報を取得してデータ保存
                newData.datas.append(oMesh.getPoints())
                newData.basedatas.append(oBaseMesh.getPoints())
            
            return newData

        return None
    
    #-----------------------------------------------
    def addUIDrawables( self, objPath, drawManager, frameContext, data ):

        # ベースメッシュのデータが空でなければ、描画処理を実行する
        if data.datas != []:
        
            mainpos = data.datas[0]
            basepos = data.basedatas[0]
            
            #頂点数分ループ処理をする
            try:
                for i in range(len(mainpos)):
                        
                    # ベースメッシュからターゲットメッシュの差を出す
                    newvec = OpenMaya.MVector(mainpos[i]) - OpenMaya.MVector(basepos[i])
                    bulue = newvec.length()/1 #　←色が変わる距離
                    
                    # 差が一定数以下ならば描画処理を行わない
                    if bulue <= 0.0001:
                        continue
                        
                    # ボックスの描画処理   
                    drawManager.beginDrawable()
                    color = OpenMaya.MColor([bulue,(1.0-bulue),0.0])
                    drawManager.setColor( color )
                    drawManager.box(OpenMaya.MPoint(mainpos[i][0],
                    mainpos[i][1],mainpos[i][2],1),
                    OpenMaya.MVector(0.0,1.0,0.0),OpenMaya.MVector(0.0,0.0,1.0),
                    0.02,0.02,0.02,True) # ←表示されるボックスのサイズ
                    
                    # 元頂点から移動頂点への線を描画する
                    drawManager.line(mainpos[i],basepos[i])
                    
                    
                    drawManager.endDrawable()
            except:
                # エラーが起きれば、処理をしない
                print "error"
                
        return True
    
    #-----------------------------------------------
    @staticmethod
    def creator( obj ):
        return DrawOverrideOverride( obj )
    
#-----------------------------------------------
# initialize
def initializePlugin( obj ):
    
    mplugin = OpenMaya.MFnPlugin( obj, "DrawOverride", "3.0", "Any" )
    try:
        #Override
        mplugin.registerNode( DrawOverride.kPluginNodeTypeName, DrawOverride.NodeId, 
        DrawOverride.nodeCreator, DrawOverride.nodeInitializer, OpenMaya.MPxNode.kLocatorNode,
        DrawOverride.classfication )
    
        #DrawOverride
        OpenMayaRender.MDrawRegistry.registerDrawOverrideCreator( DrawOverride.classfication,
        DrawOverride.registrantId,DrawOverrideOverride.creator )
    													  
    except:
        sys.stderr.write( "Failed to register node: %s" % DrawOverride.kPluginNodeTypeName )
        raise
    
#-----------------------------------------------
# uninitialize
def uninitializePlugin( obj ):
    
    mplugin = OpenMaya.MFnPlugin( obj, "DrawOverride", "3.0", "Any" )
    try:
        mplugin.deregisterNode( DrawOverride.NodeId )
        OpenMayaRender.MDrawRegistry.deregisterDrawOverrideCreator( DrawOverride.classfication,
        DrawOverride.registrantId )
    except:
        sys.stderr.write( "Failed to deregister node: %s" % DrawOverride.kPluginNodeTypeName )
        raise