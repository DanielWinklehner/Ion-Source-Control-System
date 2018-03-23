#pragma once

namespace Matsusada_USB_Sample_Cpp {

	using namespace System;
	using namespace System::ComponentModel;
	using namespace System::Collections;
	using namespace System::Windows::Forms;
	using namespace System::Data;
	using namespace System::Drawing;

	#include "FTD2XX.h"

	#define FT_PREFIX [DllImport("FTD2XX.dll")]

	#define FT_BUFFER	256

	FT_STATUS FT_Ret;                     // Return value
	FT_HANDLE ftHandle;                   // USB handler
	char strData[FT_BUFFER];

	/// <summary>
	/// Matsusada_USB_Sample の概要
	/// </summary>
	public __gc class Matsusada_USB_Sample : public System::Windows::Forms::Form
	{
	public:
		Matsusada_USB_Sample(void)
		{
			InitializeComponent();
			//
			//TODO: ここにコンストラクター コードを追加します
			//
		}

	protected:
		/// <summary>
		/// 使用中のリソースをすべてクリーンアップします。
		/// </summary>
		~Matsusada_USB_Sample()
		{
			if (components)
			{
				components->Dispose();
			}
		}
	private: System::Windows::Forms::Label *	label1;
	private: System::Windows::Forms::TextBox *	txtWrite;
	private: System::Windows::Forms::Button *	btnWrite;
	private: System::Windows::Forms::Button *	btnRead;
	private: System::Windows::Forms::TextBox *	txtRead;
	private: System::Windows::Forms::Label *	label2;
	private: System::Windows::Forms::TextBox *	txtStatus;
	private: System::Windows::Forms::Label *	label3;
	protected: 

	protected: 



	private:
		/// <summary>
		/// 必要なデザイナー変数です。
		/// </summary>
		System::ComponentModel::Container * components;

#pragma region Windows Form Designer generated code
		/// <summary>
		/// デザイナー サポートに必要なメソッドです。このメソッドの内容を
		/// コード エディターで変更しないでください。
		/// </summary>
		void InitializeComponent(void)
		{
			this->label1 = (new System::Windows::Forms::Label());
			this->txtWrite = (new System::Windows::Forms::TextBox());
			this->btnWrite = (new System::Windows::Forms::Button());
			this->btnRead = (new System::Windows::Forms::Button());
			this->txtRead = (new System::Windows::Forms::TextBox());
			this->label2 = (new System::Windows::Forms::Label());
			this->txtStatus = (new System::Windows::Forms::TextBox());
			this->label3 = (new System::Windows::Forms::Label());
			this->SuspendLayout();
			// 
			// label1
			// 
			this->label1->AutoSize = true;
			this->label1->Location = System::Drawing::Point(21, 45);
			this->label1->Name = L"label1";
			this->label1->Size = System::Drawing::Size(59, 12);
			this->label1->TabIndex = 1;
			this->label1->Text = L"Write Data";
			// 
			// txtWrite
			// 
			this->txtWrite->Location = System::Drawing::Point(108, 42);
			this->txtWrite->Name = L"txtWrite";
			this->txtWrite->Size = System::Drawing::Size(134, 19);
			this->txtWrite->TabIndex = 2;
			// 
			// btnWrite
			// 
			this->btnWrite->Location = System::Drawing::Point(248, 36);
			this->btnWrite->Name = L"btnWrite";
			this->btnWrite->Size = System::Drawing::Size(100, 30);
			this->btnWrite->TabIndex = 3;
			this->btnWrite->Text = L"Write";
			this->btnWrite->UseVisualStyleBackColor = true;
			this->btnWrite->Click += new System::EventHandler(this, &Matsusada_USB_Sample::btnWrite_Click);
			// 
			// btnRead
			// 
			this->btnRead->Location = System::Drawing::Point(248, 77);
			this->btnRead->Name = L"btnRead";
			this->btnRead->Size = System::Drawing::Size(100, 30);
			this->btnRead->TabIndex = 6;
			this->btnRead->Text = L"Read";
			this->btnRead->UseVisualStyleBackColor = true;
			this->btnRead->Click += new System::EventHandler(this, &Matsusada_USB_Sample::btnRead_Click);
			// 
			// txtRead
			// 
			this->txtRead->Location = System::Drawing::Point(108, 83);
			this->txtRead->Name = L"txtRead";
			this->txtRead->ReadOnly = true;
			this->txtRead->Size = System::Drawing::Size(134, 19);
			this->txtRead->TabIndex = 5;
			// 
			// label2
			// 
			this->label2->AutoSize = true;
			this->label2->Location = System::Drawing::Point(21, 86);
			this->label2->Name = L"label2";
			this->label2->Size = System::Drawing::Size(59, 12);
			this->label2->TabIndex = 4;
			this->label2->Text = L"Read Data";
			// 
			// txtStatus
			// 
			this->txtStatus->Location = System::Drawing::Point(108, 124);
			this->txtStatus->Name = L"txtStatus";
			this->txtStatus->ReadOnly = true;
			this->txtStatus->Size = System::Drawing::Size(240, 19);
			this->txtStatus->TabIndex = 8;
			// 
			// label3
			// 
			this->label3->AutoSize = true;
			this->label3->Location = System::Drawing::Point(21, 127);
			this->label3->Name = L"label3";
			this->label3->Size = System::Drawing::Size(38, 12);
			this->label3->TabIndex = 7;
			this->label3->Text = L"Status";
			// 
			// Matsusada_USB_Sample
			// 
			this->AutoScaleDimensions = System::Drawing::SizeF(6, 12);
			this->AutoScaleMode = System::Windows::Forms::AutoScaleMode::Font;
			this->ClientSize = System::Drawing::Size(368, 178);
			this->Controls->Add(this->txtStatus);
			this->Controls->Add(this->label3);
			this->Controls->Add(this->btnRead);
			this->Controls->Add(this->txtRead);
			this->Controls->Add(this->label2);
			this->Controls->Add(this->btnWrite);
			this->Controls->Add(this->txtWrite);
			this->Controls->Add(this->label1);
			this->MaximizeBox = false;
			this->Name = L"Matsusada_USB_Sample";
			this->Text = L"Matsusada_USB_Sample";
			this->FormClosing += new System::Windows::Forms::FormClosingEventHandler(this, &Matsusada_USB_Sample::Matsusada_USB_Sample_FormClosing);
			this->Load += new System::EventHandler(this, &Matsusada_USB_Sample::Matsusada_USB_Sample_Load);
			this->ResumeLayout(false);
			this->PerformLayout();

		}
#pragma endregion


#pragma region Event Handler

		/// <summary>
		/// Form Load
		/// </summary>
		/// <param name="e"></param>
		private: System::Void Matsusada_USB_Sample_Load(System::Object * sender, System::EventArgs * e) {
				 
			 // Open Device
			 FT_Ret = USB_Open();
		}

		/// <summary>
		/// Form Close
		/// </summary>
		/// <param name="e"></param>
		private: System::Void Matsusada_USB_Sample_FormClosing(System::Object * sender, System::Windows::Forms::FormClosingEventArgs * e) {

			 // Close Device
			 FT_Ret = USB_Close();
		}

		/// <summary>
		/// Write Button Click
		/// </summary>
		/// <param name="e"></param>
		private: System::Void btnWrite_Click(System::Object * sender, System::EventArgs * e) {
			 
			 String *writeData;
			 wchar_t wcData[FT_BUFFER];
			 size_t wLen = 0;

			 memset(strData, '\0', strlen(strData));
			 this->txtRead->Text = String::Empty;

			 writeData = String::Empty;
			 writeData = this->txtWrite->Text;

			 for(int i = 0; i < writeData->Length; i++)
			 {
				 wcData[i] = writeData->Chars[i];
 			 }

			 // String conversion (Wide -> Multibyte)
			 wcstombs(strData ,wcData, FT_BUFFER);
			 strcat_s(strData, "\r\n");

			 FT_Ret = USB_Write();
			 if (FT_Ret == FT_OK)
			 {
				 this->txtStatus->Text = "Write OK!";
			 }
			 else
			 {
				 this->txtStatus->Text = "Write NG!";
			 }
		}

		/// <summary>
		/// Read Button Click
		/// </summary>
		/// <param name="e"></param>
		private: System::Void btnRead_Click(System::Object * sender, System::EventArgs * e) {

			 String *readData;
			 wchar_t wcData[FT_BUFFER];
			 size_t wLen = 0;

			 memset(strData, '\0', strlen(strData));
			 this->txtRead->Text = String::Empty;

			 FT_Ret = USB_Read();
			 if (FT_Ret == FT_OK)
			 {
				 // String conversion (Multibyte -> Wide)
				 mbstowcs(wcData, strData, FT_BUFFER);
				 readData = Convert::ToString(wcData);

				 this->txtRead->Text = readData;
				 this->txtStatus->Text = "Read OK!";
			 }
			 else
			 {
				 this->txtStatus->Text = "Read NG!";
			 }
		}

#pragma endregion

#pragma region Public Function
        /// <summary>
        /// USB Open
        /// </summary>
		public: FT_STATUS USB_Open()
        {
            // 1台のパソコンに弊社USB製品を1台のみ接続する時のオープンの方法
            // How to open the device when connecting one "LUs1 option" or "US-32","US-32m" to one PC.
            if (FT_Open(0, &ftHandle) != FT_OK)

            // 1台のパソコンに弊社USB製品を複数台(1台でも可)接続する時のオープンの方法は、"(ﾀﾞﾌﾞﾙｸｫｰﾃｰｼｮﾝ)でくくられた、GP001001 の箇所に、USB S/N を書き込む。FT_Open，FT_OpenExは、どちらか一方を使用。
            // When opening the device while connecting multiple "LUs1 option" or "US-32","US-32m" to one PC. Write USB S/N on the place of GP001001 which is enclosed with “”(double quotation). Either FT_Open or FT_OpenEx is to be used.
            //if (FT_OpenEx("GP001001", FT_OPEN_BY_SERIAL_NUMBER, ref ftHandle) != FT_OK)
            {
                return 1;
            }

            //////////////////////////////////////////////////////////////////////////////////////////////////////////////////
            // 解説 //
            // 各シリーズとも、１台しか使わないときは、FT_Openを使用する（推奨）。
            // （FT_OpenExでもUSB S/N を書きこめば動作します。）
            // 複数台使う時は、
            // GPシリーズの場合	 		…FT_OpenExの"(ﾀﾞﾌﾞﾙｸｫｰﾃｰｼｮﾝ)でくくられた、GP001001 の箇所に、USB S/N を書きみます。
            //   							例：GP001001
            // その他各シリーズの場合	…FT_OpenExの"(ﾀﾞﾌﾞﾙｸｫｰﾃｰｼｮﾝ)でくくられた、GP001001 の箇所に、USB S/N を書きみます。
            // 								例：PKシリーズ		FT_OpenEx("PK001001", ...
            // 									SRAシリーズ		FT_OpenEx("SRA01001", ...
            // 									XXXXXシリーズ	FT_OpenEx("XXXXX001", ...
            //
            // Explanation '
            // In the case only 1 unit is used for all series, use FT_Open (recommended).
            // (Even with FT_OpenEx, if USB S/N is written it will work)
            // In the case multiple unit is used
            // GP series		…Write USB S/N in the place of GP001001 which is enclosed with ""(double quotation) of FT_OpenEx.
            // 					e.g. GP001001
            // Other series 	…Write USB S/N in the place of GP001001 which is enclosed with ""(double quotation) of FT_OpenEx.
            // 					e.g. PK series		FT_OpenEx("PK001001",…
            // 					e.g. SRA series		FT_OpenEx("SRA01001",…
            // 					e.g. XXXXX series	FT_OpenEx("XXXXX001",…
            //////////////////////////////////////////////////////////////////////////////////////////////////////////////////

            // BaudRate 9600bps Set
            if (FT_SetBaudRate(ftHandle, 9600) != FT_OK)
            {
                return 2;
            }
            // 8 data bits, 1 stop bit, no parity
            if (FT_SetDataCharacteristics(ftHandle, FT_BITS_8, FT_STOP_BITS_1, FT_PARITY_NONE) != FT_OK)
            {
                return 3;
            }
            // no flow control
            if (FT_SetFlowControl(ftHandle, FT_FLOW_NONE, 0, 0) != FT_OK)
            {
                return 4;
            }
            // 500m second read, 100m second write timeout
            if (FT_SetTimeouts(ftHandle, 50, 10) != FT_OK)
            {
                return 5;
            }
            // Rx Clear
            if (FT_Purge(ftHandle, FT_PURGE_RX) != FT_OK)
            {
                return 6;
            }
            // Tx Clear
            if (FT_Purge(ftHandle, FT_PURGE_TX) != FT_OK)
            {
                return 7;
            }
            return FT_OK;
		}

        /// <summary>
        /// USB Close
        /// </summary>
		public: FT_STATUS USB_Close()
        {
			if (FT_Close(ftHandle) != FT_OK)
			{
				return 1;
			}
			return FT_OK;
		}

        /// <summary>
        /// USB Write
        /// </summary>
		public: FT_STATUS USB_Write()
        {
			DWORD buf;

			if (FT_Write(ftHandle, strData, strlen(strData), &buf) != FT_OK)
			{
				return 1;
			}
			return FT_OK;
		}

        /// <summary>
        /// USB Read
        /// </summary>
		public: FT_STATUS USB_Read()
        {
			char cData[FT_BUFFER];
			DWORD buf;

			if (FT_Read(ftHandle, cData, FT_BUFFER, &buf) != FT_OK)
			{
				return 1;
			}

			if(buf > 0)
			{
				strncpy_s(strData, cData, buf);
			}
			else
			{
				return 1;
			}

			return FT_OK;
		}

#pragma endregion
};
}

