Module Program
    Sub Main()
        Dim value As Integer = 7

        While value > 1
            Print(value)
            If value Mod 2 = 0 Then
                value = value / 2
            Else
                value = value * 3 + 1
            End If
        End While

        Print(1)
    End Sub
End Module
