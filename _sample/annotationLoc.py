# -*- coding: utf-8 -*-
import sys

import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI
import maya.api.OpenMayaRender as OpenMayaRender

maya_useNewAPI = True 

#=========================================
class AnnotationLocNode( OpenMayaUI.MPxLocatorNode ):
	"""
	ロケーターノード
	"""

	kPluginNodeTypeName = "AnnotationLocNode"
	#TypeIDは適当
	NodeId = OpenMaya.MTypeId(0xF0F0F0)
	
	#ノードがDrawOverrideを使う為には、OverrideをMayaに登録しておく必要がある。以下２つはその為のID
	classfication = 'drawdb/geometry/AnnotationLoc'
	registrantId = 'AnnotationLocPlugin'
	
	#ノードのアトリビュート。このアトリビュートにセットした文字列が描画される
	aString = OpenMaya.MObject()
	
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
		return OpenMaya.MBoundingBox( OpenMaya.MPoint( -0.5, -0.5, -0.5 ), OpenMaya.MPoint( 0.5, 0.5, 0.5 ) )

	#-----------------------------------------------
	# creator
	@staticmethod
	def nodeCreator():
		return AnnotationLocNode()

	#-----------------------------------------------
	# initializer
	@staticmethod
	def nodeInitializer():
		fnCompAttr = OpenMaya.MFnCompoundAttribute()
		fnMessageAttr = OpenMaya.MFnMessageAttribute()
		fnTypedAttr = OpenMaya.MFnTypedAttribute()
		fnNumericAttr = OpenMaya.MFnNumericAttribute()

		AnnotationLocNode.aString = fnTypedAttr.create( "String", "string", OpenMaya.MFnData.kString )
		AnnotationLocNode.addAttribute( AnnotationLocNode.aString )
		
		return True


#=========================================
class UserData( OpenMaya.MUserData ):
	"""
	DrawOverrideにユーザー定義の情報を供給する為のデータ構造
	"""
	
	#-----------------------------------------------
	def __init__( self ):
		OpenMaya.MUserData.__init__( self, False )
		self.datas = []

#=========================================
class AnnotationLocOverride( OpenMayaRender.MPxDrawOverride ):
	"""
	ロケーターのDrawOverride
	"""

	#-----------------------------------------------
	def __init__( self, obj ):
		OpenMayaRender.MPxDrawOverride.__init__( self, obj, AnnotationLocOverride.draw )
		
	#-----------------------------------------------
	@staticmethod
	def draw( context, data ):
		pass
	
	#-----------------------------------------------
	def supportedDrawAPIs( self ):
		"""
		DirectX11だけサポート
		"""

		return OpenMayaRender.MRenderer.kDirectX11
	
	#-----------------------------------------------
	def hasUIDrawables( self ):
		"""
		addUIDrawablesを使うために必要
		"""
		return True

	#-----------------------------------------------
	def isBounded( self, objPath, cameraPath ):
		return True

	#-----------------------------------------------
	def boundingBox( self, objPath, cameraPath ):
		bbox=OpenMaya.MBoundingBox(OpenMaya.MPoint(-0.5,-0.5,-0.5),
								   OpenMaya.MPoint( 0.5, 0.5, 0.5))

		return bbox
	#-----------------------------------------------
	def disableInternalBoundingBoxDraw( self ):
		return True

	#-----------------------------------------------
	def prepareForDraw( self, objPath, cameraPath, frameContext, oldData ):
		"""
		ロケーターからアトリビュートを読んでUserDataとして返す
		"""

		if( objPath ):
			newData = None
			if( oldData ):
				newData = oldData
				newData.datas = []
			else:
				newData = UserData()
			
			thisNode = objPath.node()
			fnNode = OpenMaya.MFnDependencyNode( thisNode )
			fnDagNode = OpenMaya.MFnDagNode( thisNode )
			parentNode = fnDagNode.parent( 0 )
		
			strPlug = fnNode.findPlug( 'String', False )
			newData.datas.append( strPlug.asString() )

			return newData
		
		return None

	#-----------------------------------------------
	def addUIDrawables( self, objPath, drawManager, frameContext, data ):
		"""
		UI描画。MUIDrawManagerを使う事で簡単なライン描画とかも出来る。
		"""

		if( data ):
			drawManager.beginDrawable()
			c = OpenMaya.MColor()
			c[0] = 1.0
			c[1] = 0.8
			c[2] = 0.5
			drawManager.setColor( c )
			drawManager.setFontSize( OpenMayaRender.MUIDrawManager.kDefaultFontSize )
			drawManager.text( OpenMaya.MPoint( 0.5, 0.5 ), data.datas[0] )
			drawManager.endDrawable()

		return True

	#-----------------------------------------------
	# creator
	@staticmethod
	def creator( obj ):
		return AnnotationLocOverride( obj )
	
#-----------------------------------------------
# initialize the script plug-in
def initializePlugin( obj ):

	mplugin = OpenMaya.MFnPlugin( obj, "Autodesk", "3.0", "Any" )
	try:
		#Override使うためにはオーバーロードされた専用のregisterNode関数を使う必要がある
		mplugin.registerNode( AnnotationLocNode.kPluginNodeTypeName, 
							  AnnotationLocNode.NodeId, 
							  AnnotationLocNode.nodeCreator, 
							  AnnotationLocNode.nodeInitializer, 
							  OpenMaya.MPxNode.kLocatorNode,
							  AnnotationLocNode.classfication )

		#DrawOverride登録
		OpenMayaRender.MDrawRegistry.registerDrawOverrideCreator( AnnotationLocNode.classfication,
																  AnnotationLocNode.registrantId,
																  AnnotationLocOverride.creator )
																  
	except:
		sys.stderr.write( "Failed to register node: %s" % AnnotationLocNode.kPluginNodeTypeName )
		raise

#-----------------------------------------------
# uninitialize the script plug-in
def uninitializePlugin( obj ):
	
	mplugin = OpenMaya.MFnPlugin( obj, "Autodesk", "3.0", "Any" )
	try:
		mplugin.deregisterNode( AnnotationLocNode.NodeId )
		OpenMayaRender.MDrawRegistry.deregisterDrawOverrideCreator( AnnotationLocNode.classfication,
																	AnnotationLocNode.registrantId )
	except:
		sys.stderr.write( "Failed to deregister node: %s" % AnnotationLocNode.kPluginNodeTypeName )
		raise
