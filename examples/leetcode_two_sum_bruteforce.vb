Module Program
    Sub Main()
        Dim nums(3) As Integer
        Dim target As Integer = 9
        Dim i As Integer = 0
        Dim j As Integer = 0
        Dim found As Boolean = False
        Dim firstIndex As Integer = -1
        Dim secondIndex As Integer = -1

        nums(0) = 2
        nums(1) = 7
        nums(2) = 11
        nums(3) = 15

        For i = 0 To 3
            If Not found Then
                For j = i + 1 To 3
                    If Not found Then
                        If nums(i) + nums(j) = target Then
                            firstIndex = i
                            secondIndex = j
                            found = True
                        End If
                    End If
                Next
            End If
        Next

        If found Then
            Print(firstIndex)
            Print(secondIndex)
        Else
            Print(-1)
        End If
    End Sub
End Module
