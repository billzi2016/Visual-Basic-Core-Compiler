Module Program
    Function Fib(n As Integer) As Integer
        If n <= 1 Then
            Return n
        End If
        Return Fib(n - 1) + Fib(n - 2)
    End Function

    Sub Main()
        Dim i As Integer = 0
        For i = 0 To 7
            Print(Fib(i))
        Next
    End Sub
End Module
