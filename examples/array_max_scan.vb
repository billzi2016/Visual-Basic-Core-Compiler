Module Program
    Sub Main()
        Dim nums(4) As Integer
        Dim i As Integer = 0
        Dim best As Integer = 0

        nums(0) = 3
        nums(1) = 9
        nums(2) = 1
        nums(3) = 7
        nums(4) = 4

        best = nums(0)
        For i = 1 To 4
            If nums(i) > best Then
                best = nums(i)
            End If
        Next

        Print(best)
    End Sub
End Module
