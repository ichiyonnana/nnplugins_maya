/*----------------------------------------------------------------------------
//
//  Locator��Viewprot1.0��2.0�`��T���v�� (OpenGL�̂�)
//
//  Copyright(C) 2014 Digital Frontier Inc.
//
//    [�Ɛӎ���]
//        �{�c�[���A�R�[�h���g�p�������Ƃɂ����
//        �����N���邢���Ȃ鑹�Q�������͈�ؐӔC�𕉂����˂܂��B
//        ���ȐӔC�ł��g�p���������B
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
// �`�悷�郂�f���̏��
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
// �`��ɕK�v�ȃf�[�^
//----------------------------------------------------------------------------
class LocatorDrawUserData: public MUserData
{
/* �`��K�v�ȃf�[�^��ێ�����MUserData�B Viewport2.0�ŕK�v */
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
// Locator�{��
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
    // Locator�m�[�h�쐬���ɌĂ΂��֐�
    return new DFCustomLocator();
}

MStatus DFCustomLocator::initialize()
{
    // ����������. �A�g���r���[�g�o�^�����Ȃǂ�����
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
    /* Viewport1.0�ŕ`�掞�ɌĂ΂��֐�
    */
    LocatorDrawUserData draw_data;
    // ���C���[�t���[���\�����ǂ���
    draw_data.is_wireframe = style == M3dView::kWireFrame;
    // ���P�[�^�͑I������Ă��邩�ǂ���
    const unsigned int displayStatus = path.getDisplayStatus();
    draw_data.is_selected = !(displayStatus == M3dView::kActive || displayStatus == M3dView::kLead);

    // �`��J�n
    view.beginGL();
    DFCustomLocator::display(&draw_data);
    view.endGL();
}

void DFCustomLocator::display(const LocatorDrawUserData* draw_data)
{
    /* ���ۂ̕`�揈���������֐�. Viewport1.0, 2.0���ʕ���
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
// Viewport 2.0�Œǉ����ꂽ�`�揈������
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
    /* Viewport2.0�`��̏���ɌĂ΂��
    */
    return new LocatorDrawOverride(obj);
}

MHWRender::DrawAPI LocatorDrawOverride::supportedDrawAPIs() const
{
    /* �T�|�[�g����API��Ԃ�
    */
    // �����OpenGL�̂ݑΉ��Ȃ̂�OpenGL�݂̂�Ԃ�
    return MHWRender::kOpenGL;
}

MBoundingBox LocatorDrawOverride::boundingBox( const MDagPath& objPath, const MDagPath& cameraPath) const
{
    /* BoundingBox��Ԃ�
    ����BoundingBox��p���āA�`�悷�邩���Ȃ��������߂�
    */
    return MBoundingBox(MPoint(-1.0f, -1.0f, -1.0f),
                         MPoint(1.0f, 1.0f, 1.0f));
}

MUserData* LocatorDrawOverride::prepareForDraw(const MDagPath& objPath, const MDagPath& cameraPath,
                                               const MHWRender::MFrameContext& frameContext, MUserData* oldData)
{
    /* �`��ɕK�v�ȏ���LocatorNode����AMUserData�ɓ���鏈��������
    �`��̑O�ɌĂ΂��
    */
    // �����oldData�͑��݂��Ȃ��ׁANULL�ɂȂ�
    LocatorDrawUserData* draw_data = dynamic_cast<LocatorDrawUserData*>(oldData);
    if(draw_data == NULL)
    {
        draw_data = new LocatorDrawUserData();
    }
    // ���C���[�t���[���\�����ǂ���
    draw_data->is_wireframe = frameContext.getDisplayStyle() & MHWRender::MDrawContext::kWireFrame;
    // ���P�[�^�͑I������Ă��邩�ǂ���
    const MHWRender::DisplayStatus displayStatus = MHWRender::MGeometryUtilities::displayStatus(objPath);
    draw_data->is_selected = MHWRender::kActive == displayStatus || MHWRender::kLead == displayStatus;

    return draw_data;
}

void LocatorDrawOverride::draw(const MHWRender::MDrawContext& context, const MUserData* userdata)
{
    /* �`��̏���������
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
// �v���O�C��(�A��)���[�h���̏�������
//----------------------------------------------------------------------------
MStatus initializePlugin(MObject obj)
{
    /* �v���O�C�����[�h���ɌĂ΂��֐� */
    MStatus status;
    // �v���O�C�����
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
    /* �v���O�C���A�����[�h���ɌĂ΂��֐� */
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
