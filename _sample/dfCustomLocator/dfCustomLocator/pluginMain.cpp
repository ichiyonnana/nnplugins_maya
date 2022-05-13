/*----------------------------------------------------------------------------
//
//  LocatorのViewprot1.0と2.0描画サンプル (OpenGLのみ)
//
//  Copyright(C) 2014 Digital Frontier Inc.
//
//    [免責事項]
//        本ツール、コードを使用したことによって
//        引き起こるいかなる損害も当方は一切責任を負いかねます。
//        自己責任でご使用ください。
//       
//        Terms of Use
//        The following script is provided for your conveniece and is used at your
//        own discretion and risk. Digital Frontier is not responsible for any
//        damage to your computer system or loss of data that results from the
//        access, download and use of the content on this site.
//
----------------------------------------------------------------------------*/
#include <maya/MFnPlugin.h>
#include <maya/MPxLocatorNode.h>
#include <maya/MUserData.h>
#include <maya/MPxDrawOverride.h>
#include <maya/MDrawRegistry.h>
#include <maya/MDrawContext.h>
#include <maya/MHWGeometryUtilities.h>
#include <gl/GLU.h>


//----------------------------------------------------------------------------
// 描画するモデルの情報
//----------------------------------------------------------------------------
static float vertexes[] = {0.0f, 0.0f, -1.0f,
                            0.0f, 1.0f, 0.0f,
                            1.0f, 0.0f, 0.0f,
                            0.0f, 0.0f, 1.0f,
                            -1.0f, 0.0f, 0.0f,
                            0.0f, -1.0f, 0.0f};

static unsigned int tri_indexes[] = {0, 1, 2,
                                       2, 1, 3,
                                       3, 1, 4,
                                       4, 1, 0,
                                       0, 5, 2,
                                       2, 5, 3,
                                       3, 4, 5,
                                       4, 0, 5};

static unsigned int line_indexes[] = {0, 1, 2, 0, 5, 2, 3, 5, 4, 3, 1, 4};


//----------------------------------------------------------------------------
// 描画に必要なデータ
//----------------------------------------------------------------------------
class LocatorDrawUserData: public MUserData
{
/* 描画必要なデータを保持するMUserData。 Viewport2.0で必要 */
public:
    LocatorDrawUserData() : MUserData(false)
    {
        this->is_wireframe = false;
        this->is_selected = false;
    }
    virtual ~LocatorDrawUserData(){}

    bool is_wireframe;
    bool is_selected;
};


//----------------------------------------------------------------------------
// Locator本体
//----------------------------------------------------------------------------
class DFCustomLocator: public MPxLocatorNode
{
public:
    DFCustomLocator(){};
    virtual ~DFCustomLocator(){};

    static MTypeId typeId;
    static MString typeName;
    static MString drawDbClassification;
    static MString drawRegistrantId;

    static void* creator();
    static MStatus initialize();
    virtual MStatus compute(const MPlug& plug, MDataBlock& data);
    virtual void draw(M3dView& view,
                       const MDagPath& path,
                       M3dView::DisplayStyle style,
                       M3dView::DisplayStatus status);
    static void display(const LocatorDrawUserData* draw_data);
};


MTypeId DFCustomLocator::typeId(0x70200);
MString DFCustomLocator::typeName("DFCustomLocator");
MString DFCustomLocator::drawDbClassification("drawdb/geometry/DFCustomLocator");
MString DFCustomLocator::drawRegistrantId("DFCustomLocatorNodePlugin");


void* DFCustomLocator::creator()
{
    // Locatorノード作成時に呼ばれる関数
    return new DFCustomLocator();
}

MStatus DFCustomLocator::initialize()
{
    // 初期化処理. アトリビュート登録処理などを書く
    return MStatus::kSuccess;
}

MStatus DFCustomLocator::compute(const MPlug& plug, MDataBlock& data)
{
    return MStatus::kSuccess;
}

void DFCustomLocator::draw(M3dView& view,
                             const MDagPath& path,
                             M3dView::DisplayStyle style,
                             M3dView::DisplayStatus status)
{
    /* Viewport1.0で描画時に呼ばれる関数
    */
    LocatorDrawUserData draw_data;
    // ワイヤーフレーム表示化どうか
    draw_data.is_wireframe = style == M3dView::kWireFrame;
    // ロケータは選択されているかどうか
    const unsigned int displayStatus = path.getDisplayStatus();
    draw_data.is_selected = !(displayStatus == M3dView::kActive || displayStatus == M3dView::kLead);

    // 描画開始
    view.beginGL();
    DFCustomLocator::display(&draw_data);
    view.endGL();
}

void DFCustomLocator::display(const LocatorDrawUserData* draw_data)
{
    /* 実際の描画処理を扱う関数. Viewport1.0, 2.0共通部分
    */
    glEnableClientState(GL_VERTEX_ARRAY);
    glVertexPointer(3, GL_FLOAT, 0, vertexes);
    if(draw_data->is_selected)
    {
        glColor3f(0.26f, 1.0f, 0.64f);
    }
    else
    {
        glColor3f(1.0f, 1.0f, 0.0f);
    }
    if(draw_data->is_wireframe)
    {
        glDrawElements(GL_LINE_LOOP, 12, GL_UNSIGNED_INT, line_indexes);
    }
    else
    {
        glDrawElements(GL_TRIANGLES, 24, GL_UNSIGNED_INT, tri_indexes);
    }
    glDisableClientState(GL_VERTEX_ARRAY);
}


//----------------------------------------------------------------------------
// Viewport 2.0で追加された描画処理部分
//----------------------------------------------------------------------------
class LocatorDrawOverride : public MHWRender::MPxDrawOverride
{
public:
    LocatorDrawOverride(const MObject& obj) : MHWRender::MPxDrawOverride(obj, LocatorDrawOverride::draw){}
    virtual ~LocatorDrawOverride(){};

    static MHWRender::MPxDrawOverride* Creator(const MObject& obj);
    virtual MHWRender::DrawAPI supportedDrawAPIs() const;
    virtual MBoundingBox boundingBox(const MDagPath& objPath, const MDagPath& cameraPath) const;
    virtual MUserData* prepareForDraw(const MDagPath& objPath, const MDagPath& cameraPath,
                                       const MHWRender::MFrameContext& frameContext, MUserData* oldData);
    static void draw(const MHWRender::MDrawContext& context, const MUserData* userdata);
    virtual bool hasUIDrawables() const { return false; }
};


MHWRender::MPxDrawOverride* LocatorDrawOverride::Creator(const MObject& obj)
{
    /* Viewport2.0描画の初回に呼ばれる
    */
    return new LocatorDrawOverride(obj);
}

MHWRender::DrawAPI LocatorDrawOverride::supportedDrawAPIs() const
{
    /* サポートするAPIを返す
    */
    // 今回はOpenGLのみ対応なのでOpenGLのみを返す
    return MHWRender::kOpenGL;
}

MBoundingBox LocatorDrawOverride::boundingBox( const MDagPath& objPath, const MDagPath& cameraPath) const
{
    /* BoundingBoxを返す
    このBoundingBoxを用いて、描画するかしないかを決める
    */
    return MBoundingBox(MPoint(-1.0f, -1.0f, -1.0f),
                         MPoint(1.0f, 1.0f, 1.0f));
}

MUserData* LocatorDrawOverride::prepareForDraw(const MDagPath& objPath, const MDagPath& cameraPath,
                                               const MHWRender::MFrameContext& frameContext, MUserData* oldData)
{
    /* 描画に必要な情報をLocatorNodeから、MUserDataに入れる処理を書く
    描画の前に呼ばれる
    */
    // 初回はoldDataは存在しない為、NULLになる
    LocatorDrawUserData* draw_data = dynamic_cast<LocatorDrawUserData*>(oldData);
    if(draw_data == NULL)
    {
        draw_data = new LocatorDrawUserData();
    }
    // ワイヤーフレーム表示かどうか
    draw_data->is_wireframe = frameContext.getDisplayStyle() & MHWRender::MDrawContext::kWireFrame;
    // ロケータは選択されているかどうか
    const MHWRender::DisplayStatus displayStatus = MHWRender::MGeometryUtilities::displayStatus(objPath);
    draw_data->is_selected = MHWRender::kActive == displayStatus || MHWRender::kLead == displayStatus;

    return draw_data;
}

void LocatorDrawOverride::draw(const MHWRender::MDrawContext& context, const MUserData* userdata)
{
    /* 描画の処理を書く
    */
    MStatus status;
    const LocatorDrawUserData* draw_data = dynamic_cast<const LocatorDrawUserData*>(userdata);
    const MMatrix transform = context.getMatrix(MHWRender::MFrameContext::kWorldViewMtx, &status);
    if (status != MStatus::kSuccess)
    {
        return;
    }
    const MMatrix projection = context.getMatrix(MHWRender::MFrameContext::kProjectionMtx, &status);
    if (status != MStatus::kSuccess)
    {
        return;
    }

    glMatrixMode(GL_MODELVIEW);
    glPushMatrix();
    glLoadMatrixd(transform.matrix[0]);
    glMatrixMode(GL_PROJECTION);
    glPushMatrix();
    glLoadMatrixd(projection.matrix[0]);
    glPushAttrib(GL_ALL_ATTRIB_BITS);

    DFCustomLocator::display(draw_data);

    glPopAttrib();
    glPopMatrix();
    glMatrixMode(GL_MODELVIEW);
    glPopMatrix();
}


//----------------------------------------------------------------------------
// プラグイン(アン)ロード時の処理部分
//----------------------------------------------------------------------------
MStatus initializePlugin(MObject obj)
{
    /* プラグインロード時に呼ばれる関数 */
    MStatus status;
    // プラグイン情報
    MFnPlugin plugin(obj, "DigitalFrontier.Inc", "1.0", "ore" );
    status = plugin.registerNode(DFCustomLocator::typeName,
                                 DFCustomLocator::typeId,
                                 DFCustomLocator::creator,
                                 DFCustomLocator::initialize,
                                 MPxNode::kLocatorNode,
                                 &DFCustomLocator::drawDbClassification);
    if(!status)
    {
        std::cout << "Failed registerNode" << std::endl;
        return status;
    }
    status = MHWRender::MDrawRegistry::registerDrawOverrideCreator(DFCustomLocator::drawDbClassification,
                                                                   DFCustomLocator::drawRegistrantId,
                                                                   LocatorDrawOverride::Creator);
    if(!status)
    {
        std::cout << "Failed registerDrawOverride" << std::endl;
        return status;
    }
    return status;
}


MStatus uninitializePlugin( MObject obj )
{
    /* プラグインアンロード時に呼ばれる関数 */
    MStatus status;
    MFnPlugin plugin( obj );
    status = MHWRender::MDrawRegistry::deregisterDrawOverrideCreator(DFCustomLocator::drawDbClassification,
                                                                     DFCustomLocator::drawRegistrantId);
    if(!status)
    {
        std::cout << "Failed deregisterDrawOverrideCreator" << std::endl;
        return status;
    }
    status = plugin.deregisterNode(DFCustomLocator::typeId);
    if(!status)
    {
        std::cout << "Failed deregisterNode" << std::endl;
        return status;
    }
    return status;
}
