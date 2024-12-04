def euclide_etendu(a, b):
    # Initialisation des valeurs
    s0, t0 = 1, 0
    s1, t1 = 0, 1
    r0, r1 = a, b

    while r1 != 0:
        q = r0 // r1
        r2 = r0 - q * r1
        s2 = s0 - q * s1
        t2 = t0 - q * t1

        r0, r1 = r1, r2
        s0, s1 = s1, s2
        t0, t1 = t1, t2
    return r0, s0, t0


a = 30
b = 12
pgcd, s, t = euclide_etendu(a, b)
print(f"pgcd({a}, {b}) = {pgcd}")
print(f"Coefficients de Bézout : s = {s}, t = {t}")
