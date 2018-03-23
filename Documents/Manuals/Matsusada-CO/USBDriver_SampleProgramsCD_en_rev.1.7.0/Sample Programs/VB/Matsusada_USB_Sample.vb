Public Class Matsusada_USB_Sample

    '------------------------------------------------------------------------------
    Private Declare Function FT_Open Lib "FTD2XX.DLL" (ByVal intDeviceNumber As Short, ByRef lngHandle As Integer) As Integer
    '------------------------------------------------------------------------------
    Private Declare Function FT_OpenEx Lib "FTD2XX.DLL" (ByVal pArg1 As String, ByVal lngFlags As Integer, ByRef lngHandle As Integer) As Integer
    '------------------------------------------------------------------------------
    Private Declare Function FT_SetBaudRate Lib "FTD2XX.DLL" (ByVal lngHandle As Integer, ByVal lngBaudRate As Integer) As Integer
    '------------------------------------------------------------------------------
    Private Declare Function FT_SetDataCharacteristics Lib "FTD2XX.DLL" (ByVal lngHandle As Integer, ByVal byWordLength As Byte, ByVal byStopBits As Byte, ByVal byParity As Byte) As Integer
    '------------------------------------------------------------------------------
    Private Declare Function FT_SetFlowControl Lib "FTD2XX.DLL" (ByVal lngHandle As Integer, ByVal intFlowControl As Integer, ByVal byXonChar As Byte, ByVal byXoffChar As Byte) As Integer
    '------------------------------------------------------------------------------
    Private Declare Function FT_SetTimeouts Lib "FTD2XX.DLL" (ByVal lngHandle As Integer, ByVal lngReadTimeout As Integer, ByVal lngWriteTimeout As Integer) As Integer
    '------------------------------------------------------------------------------
    Private Declare Function FT_Purge Lib "FTD2XX.DLL" (ByVal lngHandle As Integer, ByVal lngMask As Integer) As Integer
    '------------------------------------------------------------------------------
    Private Declare Function FT_Close Lib "FTD2XX.DLL" (ByVal lngHandle As Integer) As Integer
    '------------------------------------------------------------------------------
    Private Declare Function FT_Write Lib "FTD2XX.DLL" (ByVal lngHandle As Integer, ByVal lpszBuffer As String, ByVal lngBufferSize As Integer, ByRef lngBytesWritten As Integer) As Integer
    '------------------------------------------------------------------------------
    Private Declare Function FT_Read Lib "FTD2XX.DLL" (ByVal lngHandle As Integer, ByVal lpszBuffer As String, ByVal lngBufferSize As Integer, ByRef lngBytesReturned As Integer) As Integer
    '------------------------------------------------------------------------------
    Private Declare Function FT_ResetDevice Lib "FTD2XX.DLL" (ByVal lngHandle As Integer) As Integer
    '------------------------------------------------------------------------------
    Private Declare Function FT_GetQueueStatus Lib "FTD2XX.DLL" (ByVal lngHandle As Integer, ByRef dwRxBytes As Integer) As Integer
    '------------------------------------------------------------------------------
    Private Declare Function FT_GetStatus Lib "FTD2XX.DLL" (ByVal lngHandle As Integer, ByRef dwRxBytes As Integer, ByRef dwTxBytes As Integer, ByRef dwBytes As Integer) As Integer
    '------------------------------------------------------------------------------

    ' Return codes
    Const FT_OK = 0
    ' Word Lengths
    Const FT_BITS_8 = 8
    ' Stop Bits
    Const FT_STOP_BITS_1 = 0
    ' Parity
    Const FT_PARITY_NONE = 0
    ' Flow Control
    Const FT_FLOW_NONE = &H0
    ' Purge rx and tx buffers
    Const FT_PURGE_RX = 1
    Const FT_PURGE_TX = 2
    ' FT_OpenEx Flags
    Const FT_OPEN_BY_SERIAL_NUMBER = 1
    ' Read Buffer
    Const FT_READ_BUFFER = 256

    ' USB Handle
    Dim lngHandle As Integer
    ' Write Buffer
    Dim strWriteBuffer As String
    ' Read Buffer
    Dim strReadBuffer As String


    '------------------------------------------------------------------------------
    'Form Load
    Private Sub Matsusada_USB_Sample_Load(sender As System.Object, e As System.EventArgs) Handles MyBase.Load
        UsbOpen()
    End Sub

    '------------------------------------------------------------------------------
    'Form Close
    Private Sub Matsusada_USB_Sample_FormClosing(sender As System.Object, e As System.Windows.Forms.FormClosingEventArgs) Handles MyBase.FormClosing
        UsbClose()
    End Sub


    '------------------------------------------------------------------------------
    'Write Button Click
    Private Sub btnWrite_Click(sender As System.Object, e As System.EventArgs) Handles btnWrite.Click
        Dim wdata As String
        Dim Rt As Integer

        wdata = txtWrite.Text + vbCrLf
        Rt = UsbWrite(wdata)

        If Rt = FT_OK Then
            txtStatus.Text = "Write OK!"
        Else
            txtStatus.Text = "Write NG!"
        End If
        txtRead.Text = String.Empty
    End Sub

    '------------------------------------------------------------------------------
    'Read Button Click
    Private Sub btnRead_Click(sender As System.Object, e As System.EventArgs) Handles btnRead.Click
        Dim rdata As String
        Dim Rt As Long

        rdata = String.Empty
        Rt = UsbRead(rdata, FT_READ_BUFFER)

        If Rt = FT_OK Then
            txtRead.Text = rdata
            txtStatus.Text = "Read OK!"
        Else
            txtRead.Text = String.Empty
            txtStatus.Text = "Read NG!"
        End If
    End Sub


    '------------------------------------------------------------------------------
    'USB Open
    Sub UsbOpen()

        ' 1台のパソコンに弊社USB製品を1台のみ接続する時のオープンの方法
        ' How to open the device when connecting one "LUs1 option" or "US-32","US-32m" to one PC.
        If FT_Open(0, lngHandle) <> FT_OK Then

            ' 1台のパソコンに弊社USB製品を複数台(1台でも可)接続する時のオープンの方法は、"(ﾀﾞﾌﾞﾙｸｫｰﾃｰｼｮﾝ)でくくられた、GP001001 の箇所に、USB S/N を書き込む。FT_Open，FT_OpenExは、どちらか一方を使用。
            ' When opening the device while connecting multiple "LUs1 option" or "US-32","US-32m" to one PC. Write USB S/N on the place of GP001001 which is enclosed with “”(double quotation). Either FT_Open or FT_OpenEx is to be used.
            'If FT_OpenEx("GP001001", FT_OPEN_BY_SERIAL_NUMBER, lngHandle) <> FT_OK Then

            ' ////////////////////////////////////////////////////////////////////////////////////////////////////////////// '
            ' 解説 '
            ' 各シリーズとも、１台しか使わないときは、FT_Openを使用する（推奨）。
            ' （FT_OpenExでもUSB S/N を書きこめば動作します。）
            ' 複数台使う時は、
            ' GPシリーズの場合	 		…FT_OpenExの"(ﾀﾞﾌﾞﾙｸｫｰﾃｰｼｮﾝ)でくくられた、GP001001 の箇所に、USB S/N を書きみます。
            '   							例：GP001001
            ' その他各シリーズの場合	…FT_OpenExの"(ﾀﾞﾌﾞﾙｸｫｰﾃｰｼｮﾝ)でくくられた、GP001001 の箇所に、USB S/N を書きみます。
            ' 								例：PKシリーズ		FT_OpenEx("PK001001", ...
            '									SRAシリーズ		FT_OpenEx("SRA01001", ...
            '									XXXXXシリーズ	FT_OpenEx("XXXXX001", ...

            ' Explanation '
            ' In the case only 1 unit is used for all series, use FT_Open (recommended).
            ' (Even with FT_OpenEx, if USB S/N is written it will work)
            ' In the case multiple unit is used
            ' GP series		…Write USB S/N in the place of GP001001 which is enclosed with ""(double quotation) of FT_OpenEx.
            '					e.g. GP001001
            ' Other series 	…Write USB S/N in the place of GP001001 which is enclosed with ""(double quotation) of FT_OpenEx.
            ' 					e.g. PK series		FT_OpenEx("PK001001",…
            ' 					e.g. SRA series		FT_OpenEx("SRA01001",…
            ' 					e.g. XXXXX series	FT_OpenEx("XXXXX001",…
            ' ////////////////////////////////////////////////////////////////////////////////////////////////////////////// '

            Exit Sub
        End If

        ' BaudRate 9600bps Set
        If FT_SetBaudRate(lngHandle, 9600) <> FT_OK Then
            UsbClose()
            Exit Sub
        End If
        ' 8 data bits, 1 stop bit, no parity
        If FT_SetDataCharacteristics(lngHandle, FT_BITS_8, FT_STOP_BITS_1, FT_PARITY_NONE) <> FT_OK Then
            UsbClose()
            Exit Sub
        End If
        ' no flow control
        If FT_SetFlowControl(lngHandle, FT_FLOW_NONE, 0, 0) <> FT_OK Then
            UsbClose()
            Exit Sub
        End If
        ' 50m second read,write timeout
        If FT_SetTimeouts(lngHandle, 50, 50) <> FT_OK Then
            UsbClose()
            Exit Sub
            ' Rx Clear
        End If
        If FT_Purge(lngHandle, FT_PURGE_RX) <> FT_OK Then
            UsbClose()
            Exit Sub
        End If
        ' Tx Clear
        If FT_Purge(lngHandle, FT_PURGE_TX) <> FT_OK Then
            UsbClose()
            Exit Sub
        End If
    End Sub

    '------------------------------------------------------------------------------
    ' USB Close
    Sub UsbClose()
        FT_Close(lngHandle)
    End Sub

    '------------------------------------------------------------------------------
    ' USB Write
    Function UsbWrite(ByVal data As String) As Integer
        Dim wlen As Integer
        Dim Ln As Integer
        wlen = Len(data)
        strWriteBuffer = data
        UsbWrite = FT_Write(lngHandle, strWriteBuffer, wlen, Ln)
    End Function

    '------------------------------------------------------------------------------
    ' USB Read
    Function UsbRead(ByRef data As String, ByVal n As Integer) As Integer
        Dim Ln As Integer
        strReadBuffer = Space(n)
        UsbRead = FT_Read(lngHandle, strReadBuffer, n, Ln)
        If Ln > 0 Then
            ' Cut of the required size
            data = Microsoft.VisualBasic.Left(strReadBuffer, Ln - 1)
        Else
            data = String.Empty
        End If
    End Function

End Class
