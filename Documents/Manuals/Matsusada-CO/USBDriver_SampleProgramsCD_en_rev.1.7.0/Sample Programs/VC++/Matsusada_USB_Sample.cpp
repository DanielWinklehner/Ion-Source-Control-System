// Matsusada_USB_Sample.cpp : ���C�� �v���W�F�N�g �t�@�C���ł��B

#include "stdafx.h"
#include "Matsusada_USB_Sample.h"

using namespace Matsusada_USB_Sample_Cpp;

[STAThreadAttribute]
int main()
{
	// �R���g���[�����쐬�����O�ɁAWindows XP �r�W���A�����ʂ�L���ɂ��܂�
	Application::EnableVisualStyles();
	Application::SetCompatibleTextRenderingDefault(false); 

	// ���C�� �E�B���h�E���쐬���āA���s���܂�
	Application::Run(new Matsusada_USB_Sample());
	return 0;
}
