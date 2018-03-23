using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Runtime.InteropServices;

namespace Matsusada_USB_Sample_Cs
{
    public partial class Matsusada_USB_Sample : Form
    {
        #region Define DLL Import
        [DllImport("ftd2xx.dll")]
        public static extern UInt32 FT_Open(Int16 DeviceNumber, ref UInt32 ftHandle);
        [DllImport("ftd2xx.dll")]
        public static extern UInt32 FT_OpenEx(string ftArg1, UInt32 ftFlags, ref UInt32 ftHandle);
        [DllImport("ftd2xx.dll")]
        public static extern UInt32 FT_SetBaudRate(UInt32 ftHandle, UInt32 BaudRate);
        [DllImport("ftd2xx.dll")]
        public static extern UInt32 FT_SetDataCharacteristics(UInt32 ftHandle, uint WordLength, uint StopBits, uint Parity);
        [DllImport("ftd2xx.dll")]
        public static extern UInt32 FT_SetFlowControl(UInt32 ftHandle, uint FlowControl, uint XonChar, uint XoffChar);
        [DllImport("ftd2xx.dll")]
        public static extern UInt32 FT_SetTimeouts(UInt32 ftHandle, UInt32 ReadTimeout, UInt32 WriteTimeout);
        [DllImport("ftd2xx.dll")]
        public static extern UInt32 FT_Purge(UInt32 ftHandle, UInt32 Mask);
        [DllImport("ftd2xx.dll")]
        public static extern UInt32 FT_Close(UInt32 ftHandle);
        [DllImport("ftd2xx.dll")]
        public static extern UInt32 FT_Write(UInt32 ftHandle, string Buffer, UInt32 BufferSize, ref UInt32 BytesWritten);
        [DllImport("ftd2xx.dll")]
        public static extern UInt32 FT_Read(UInt32 ftHandle, StringBuilder Buffer, UInt32 BufferSize, ref UInt32 BytesReturned);
        [DllImport("ftd2xx.dll")]
        public static extern UInt32 FT_ResetDevice(UInt32 ftHandle);
        [DllImport("ftd2xx.dll")]
        public static extern UInt32 FT_GetQueueStatus(UInt32 ftHandle, ref UInt32 RxBytes);
        [DllImport("ftd2xx.dll")]
        public static extern UInt32 FT_GetStatus(UInt32 ftHandle, ref UInt32 RxBytes, ref UInt32 TxBytes, ref UInt32 Bytes);
        #endregion


        #region Member Constant
        public const UInt32 FT_OK = 0;                      // Return codes
        public const UInt32 FT_BITS_8 = 8;                  // Word Lengths
        public const UInt32 FT_STOP_BITS_1 = 0;             // Stop Bits
        public const UInt32 FT_PARITY_NONE = 0;             // Parity
        public const UInt32 FT_FLOW_NONE = 0;               // Flow Control
        public const UInt32 FT_PURGE_RX = 1;                // Purge rx and tx buffers
        public const UInt32 FT_PURGE_TX = 2;                // Purge rx and tx buffers
        public const UInt32 FT_OPEN_BY_SERIAL_NUMBER = 1;   // FT_OpenEx Flags
        public const UInt32 FT_READ_BUFFER = 256;           // Read Buffer Size
        #endregion


        #region Member Variable
        public static UInt32 FT_Ret;                        // Return value
        public static UInt32 ftHandle;                      // USB handle
        public static UInt32 RxBytes;                       // Length of writing data
        public static UInt32 TxBytes;                       // Length of reading data
        public static UInt32 NumDevs;                       // Number of devices
        #endregion


        #region Constructor
        public Matsusada_USB_Sample()
        {
            InitializeComponent();
        }
        #endregion


        #region Event Handler
        /// <summary>
        /// Form Load
        /// </summary>
        /// <param name="e"></param>
        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);

            // Open Device
            FT_Ret = USB_Open();
        }

        /// <summary>
        /// Form Close
        /// </summary>
        /// <param name="e"></param>
        protected override void OnClosing(CancelEventArgs e)
        {
            // Close Device
            FT_Ret = USB_Close();

            base.OnClosing(e);
        }


        /// <summary>
        /// Write Button Click
        /// </summary>
        /// <param name="e"></param>
        private void btnWrite_Click(object sender, EventArgs e)
        {
            string wdata;
            wdata = this.txtWrite.Text + "\r\n";

            FT_Ret = USB_Write(wdata);
            if (FT_Ret == FT_OK)
            {
                this.txtStatus.Text = "Write OK!";
            }
            else
            {
                this.txtStatus.Text = "Write NG!";
            }
            this.txtRead.Text = wdata;
        }

        /// <summary>
        /// Read Button Click
        /// </summary>
        /// <param name="e"></param>
        private void btnRead_Click(object sender, EventArgs e)
        {
            string rdata;
            rdata = string.Empty;

            FT_Ret = USB_Read(ref rdata);
            if (FT_Ret == FT_OK)
            {
                this.txtRead.Text = rdata;
                this.txtStatus.Text = "Read OK!";
            }
            else
            {
                this.txtRead.Text = string.Empty;
                this.txtStatus.Text = "Read NG!";
            }
        }
        #endregion

        
        #region Public Function
        /// <summary>
        /// Read Button Click
        /// </summary>
        /// <param name="e"></param>
        public static UInt32 USB_Open()
        {

            // 1台のパソコンに弊社USB製品を1台のみ接続する時のオープンの方法
            // How to open the device when connecting one "LUs1 option" or "US-32","US-32m" to one PC.
            if (FT_Open(0, ref ftHandle) != FT_OK)

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
        /// <param name="e"></param>
        public static UInt32 USB_Close()
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
        /// <param name="e"></param>
        public static UInt32 USB_Write(string data)
        {
            UInt32 buf = 0;

            if (FT_Write(ftHandle, data, (UInt32)(data.Length), ref buf) != FT_OK)
            {
                return 1;
            }
            return FT_OK;
        }

        /// <summary>
        /// USB Read
        /// </summary>
        /// <param name="e"></param>
        public static UInt32 USB_Read(ref string data)
        {
            UInt32 buf = 0;
            StringBuilder strRet = new StringBuilder();

            if (FT_Read(ftHandle, strRet, FT_READ_BUFFER, ref buf) != FT_OK)
            {
                return 1;
            }

            if (buf > 0)
            {
                string tmp = strRet.ToString();

                // Cut of the required size
                data = tmp.Substring(0, (int)(buf - 1));
            }
            else
            {
                return 1;
            }
            return FT_OK;
        }
        #endregion

    }
}
