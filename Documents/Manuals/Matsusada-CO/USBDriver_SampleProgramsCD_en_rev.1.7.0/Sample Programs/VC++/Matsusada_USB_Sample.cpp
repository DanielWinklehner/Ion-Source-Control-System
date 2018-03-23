// Matsusada_USB_Sample.cpp : メイン プロジェクト ファイルです。

#include "stdafx.h"
#include "Matsusada_USB_Sample.h"

using namespace Matsusada_USB_Sample_Cpp;

[STAThreadAttribute]
int main()
{
	// コントロールが作成される前に、Windows XP ビジュアル効果を有効にします
	Application::EnableVisualStyles();
	Application::SetCompatibleTextRenderingDefault(false); 

	// メイン ウィンドウを作成して、実行します
	Application::Run(new Matsusada_USB_Sample());
	return 0;
}
