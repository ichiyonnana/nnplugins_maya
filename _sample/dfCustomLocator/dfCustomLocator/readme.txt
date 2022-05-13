/*----------------------------------------------------------------------------
//
//  DF_TALK SAMPLE PROGRAM
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

※免責事項※
本記事内で公開している全ての手法・コードの有用性、安全性について、当方は一切の保証を与えるものではありません。
これらのコードを使用したことによって引き起こる直接的、間接的な損害に対し、当方は一切責任を負うものではありません。
自己責任でご使用ください。


[ファイル]
・dfCustomLocator.sln
・dfCustomLocator.vcxproj
・dfCustomLocator.vcxproj.filters
・pluginMain.cpp


[ビルド方法]
1. dfCustomLocator.slnを開きます
2. Configurationを目的のMayaのバージョンに合わせます
3. ビルド

[使用方法]

1. 環境変数: MAYA_PLUG_IN_PATHをビルドした、mllがある場所に設定する
2. Mayaを起動
3. scriptEditorで、下記のMELを実行する

    loadPlugin "dfCustomLocator";
    createNode "DFCustomLocator";
