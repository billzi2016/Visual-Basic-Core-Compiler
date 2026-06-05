Module Program
    Function IsPrime(n As Integer) As Boolean
        If n < 2 Then
            Return False
        End If

        Dim i As Integer = 2
        While i * i <= n
            If n Mod i = 0 Then
                Return False
            End If
            i = i + 1
        End While

        Return True
    End Function

    Sub Main()
        Dim value As Integer = 2
        While value <= 20
            If IsPrime(value) Then
                Print(value)
            End If
            value = value + 1
        End While
    End Sub
End Module
