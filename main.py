class GeneradorCongruencialLineal: 

    def __init__(self,Y:int ,A: int = 16807, C: int = 0, M: int= (2**31) - 1 ):
        self.seed = Y
        self.a = A
        self.c = C
        self.m = M

    def congruencial_lineal(self):
        self.seed = (self.a * self.seed + self.c) % self.m
        return self.seed



class Xorshift:
    def __init__(self, semilla):
        if semilla == 0:
            raise ValueError("La semilla debe ser distinta de cero para xorshift32")
        # Asegurar que la semilla esté en el rango de 32bits
        self.seed = semilla & 0xFFFFFFFF

    def xor_shift_32(self):
        x = self.seed
        x ^= (x << 13) & 0xFFFFFFFF # Asegurar que el resultado intermedio sea de 32 bits
        x ^= (x >> 17) # siempre va a ser un entero de 32 bits
        x ^= (x << 5) & 0xFFFFFFFF # Asegurar que el resultado intermedio sea de 32 bits
        self.seed = x

        return x 
    


# Pruebas
if __name__ == "__main__":
    # Inicializar el estado (debe ser distinto de cero)
    state = Xorshift(123456789)
    satate_congruencial = GeneradorCongruencialLineal(123456789)
    print("Generando 10 números aleatorios con Xorshift:")
    for _ in range(10):
        numero_aleatorio = state.xor_shift_32()
        print(numero_aleatorio)

    print("Generando 10 números aleatorios:")
    for _ in range(10):
        numero_aleatorio = Xorshift.xor_shift_32(state)
        print(numero_aleatorio)
