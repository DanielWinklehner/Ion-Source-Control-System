<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class Matsusada_USB_Sample
    Inherits System.Windows.Forms.Form

    'フォームがコンポーネントの一覧をクリーンアップするために dispose をオーバーライドします。
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Windows フォーム デザイナーで必要です。
    Private components As System.ComponentModel.IContainer

    'メモ: 以下のプロシージャは Windows フォーム デザイナーで必要です。
    'Windows フォーム デザイナーを使用して変更できます。  
    'コード エディターを使って変更しないでください。
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(Matsusada_USB_Sample))
        Me.btnRead = New System.Windows.Forms.Button()
        Me.btnWrite = New System.Windows.Forms.Button()
        Me.txtStatus = New System.Windows.Forms.TextBox()
        Me.label7 = New System.Windows.Forms.Label()
        Me.txtRead = New System.Windows.Forms.TextBox()
        Me.label6 = New System.Windows.Forms.Label()
        Me.txtWrite = New System.Windows.Forms.TextBox()
        Me.label5 = New System.Windows.Forms.Label()
        Me.SuspendLayout()
        '
        'btnRead
        '
        Me.btnRead.Location = New System.Drawing.Point(248, 71)
        Me.btnRead.Name = "btnRead"
        Me.btnRead.Size = New System.Drawing.Size(100, 30)
        Me.btnRead.TabIndex = 6
        Me.btnRead.Text = "Read"
        Me.btnRead.UseVisualStyleBackColor = True
        '
        'btnWrite
        '
        Me.btnWrite.Location = New System.Drawing.Point(248, 30)
        Me.btnWrite.Name = "btnWrite"
        Me.btnWrite.Size = New System.Drawing.Size(100, 30)
        Me.btnWrite.TabIndex = 3
        Me.btnWrite.Text = "Write"
        Me.btnWrite.UseVisualStyleBackColor = True
        '
        'txtStatus
        '
        Me.txtStatus.Location = New System.Drawing.Point(108, 118)
        Me.txtStatus.Name = "txtStatus"
        Me.txtStatus.ReadOnly = True
        Me.txtStatus.Size = New System.Drawing.Size(240, 19)
        Me.txtStatus.TabIndex = 8
        '
        'label7
        '
        Me.label7.AutoSize = True
        Me.label7.Location = New System.Drawing.Point(21, 121)
        Me.label7.Name = "label7"
        Me.label7.Size = New System.Drawing.Size(38, 12)
        Me.label7.TabIndex = 7
        Me.label7.Text = "Status"
        '
        'txtRead
        '
        Me.txtRead.Location = New System.Drawing.Point(108, 77)
        Me.txtRead.Name = "txtRead"
        Me.txtRead.ReadOnly = True
        Me.txtRead.Size = New System.Drawing.Size(134, 19)
        Me.txtRead.TabIndex = 5
        '
        'label6
        '
        Me.label6.AutoSize = True
        Me.label6.Location = New System.Drawing.Point(21, 80)
        Me.label6.Name = "label6"
        Me.label6.Size = New System.Drawing.Size(59, 12)
        Me.label6.TabIndex = 4
        Me.label6.Text = "Read Data"
        '
        'txtWrite
        '
        Me.txtWrite.Location = New System.Drawing.Point(108, 36)
        Me.txtWrite.Name = "txtWrite"
        Me.txtWrite.Size = New System.Drawing.Size(134, 19)
        Me.txtWrite.TabIndex = 2
        '
        'label5
        '
        Me.label5.AutoSize = True
        Me.label5.Location = New System.Drawing.Point(21, 39)
        Me.label5.Name = "label5"
        Me.label5.Size = New System.Drawing.Size(59, 12)
        Me.label5.TabIndex = 1
        Me.label5.Text = "Write Data"
        '
        'Matsusada_USB_Sample
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 12.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.ClientSize = New System.Drawing.Size(368, 178)
        Me.Controls.Add(Me.btnRead)
        Me.Controls.Add(Me.btnWrite)
        Me.Controls.Add(Me.txtStatus)
        Me.Controls.Add(Me.label7)
        Me.Controls.Add(Me.txtRead)
        Me.Controls.Add(Me.label6)
        Me.Controls.Add(Me.txtWrite)
        Me.Controls.Add(Me.label5)
        Me.Icon = CType(resources.GetObject("$this.Icon"), System.Drawing.Icon)
        Me.MaximizeBox = False
        Me.Name = "Matsusada_USB_Sample"
        Me.Text = "Matsusada_USB_Sample"
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub
    Private WithEvents btnRead As System.Windows.Forms.Button
    Private WithEvents btnWrite As System.Windows.Forms.Button
    Private WithEvents txtStatus As System.Windows.Forms.TextBox
    Private WithEvents label7 As System.Windows.Forms.Label
    Private WithEvents txtRead As System.Windows.Forms.TextBox
    Private WithEvents label6 As System.Windows.Forms.Label
    Private WithEvents txtWrite As System.Windows.Forms.TextBox
    Private WithEvents label5 As System.Windows.Forms.Label

End Class
