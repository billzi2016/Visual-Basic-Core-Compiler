Module Program
    Function IsPalindrome(value As Integer) As Boolean
        If value < 0 Then
            Return False
        End If

        Dim original As Integer = value
        Dim reversed As Integer = 0

        While value > 0
            reversed = reversed * 10 + (value Mod 10)
            value = value / 10
        End While

        Return original = reversed
    End Function

    Sub Main()
        Print(IsPalindrome(121))
        Print(IsPalindrome(123))
        Print(IsPalindrome(0))
    End Sub
End Module
