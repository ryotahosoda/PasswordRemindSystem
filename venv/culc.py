import math


def c_count(n, r):
    return math.factorial(n) / (math.factorial(n - r) * math.factorial(r))


if __name__ == '__main__':
    a = c_count(12, 3) * pow(95, 3)
    b = c_count(12, 2) * pow(95, 2)
    c = c_count(12, 1) * pow(95, 1)
    d = pow(96, 12)

    print(math.log2((a + b + c + 1) / d))

    a1 = c_count(12, 3) * pow(96, 3)
    b1 = c_count(12, 2) * pow(96, 2)
    c1 = c_count(12, 1) * pow(96, 1)
    d1 = pow(96, 12)

    print(math.log2((a1 + b1 + c1 + 1) / d1))