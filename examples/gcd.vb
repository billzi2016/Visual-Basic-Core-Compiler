Module Program
    Function Gcd(a As Integer, b As Integer) As Integer
        While b <> 0
            Dim remainder As Integer = a Mod b
            a = b
            b = remainder
        End While

        Return a
    End Function

    Sub Main()
        Print(Gcd(48, 18))
        Print(Gcd(1071, 462))
    End Sub
End Module
