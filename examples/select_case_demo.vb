Module Program
    Sub Main()
        Dim score As Integer = 3
        Dim label As String = "beta"

        Select Case score
            Case 1
                Print("one")
            Case 2
                Print("two")
            Case 3, 4
                Print("three")
            Case Else
                Print("other")
        End Select

        Select Case label
            Case "alpha"
                Print("miss")
            Case "beta"
                Print("match")
            Case Else
                Print("other")
        End Select
    End Sub
End Module
