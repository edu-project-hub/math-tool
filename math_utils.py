def factorial(n):
    """Berechnet die Fakultät n!"""
    if n < 0:
        raise ValueError("n muss nicht-negativ sein.")
    if n in (0, 1):
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def binom_coeff(n, k):
    """Berechnet den Binomialkoeffizienten 'n choose k' = n! / (k! * (n-k)!)"""
    if k < 0 or n < 0 or k > n:
        raise ValueError("Ungültige Werte für n und k.")
    return factorial(n) // (factorial(k) * factorial(n - k))
