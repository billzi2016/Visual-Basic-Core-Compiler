Module Program
    Function ClimbStairs(n As Integer) As Integer
        If n <= 2 Then
            Return n
        End If

        Return ClimbStairs(n - 1) + ClimbStairs(n - 2)
    End Function

    Sub Main()
        Print(ClimbStairs(5))
    End Sub
End Module
