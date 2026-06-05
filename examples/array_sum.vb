Module Program
    Sub Main()
        Dim nums(3) As Integer
        Dim i As Integer = 0
        Dim total As Integer = 0

        nums(0) = 2
        nums(1) = 4
        nums(2) = 6
        nums(3) = 8

        For i = 0 To 3
            total = total + nums(i)
        Next

        Print(total)
    End Sub
End Module
