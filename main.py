import math

class GCL: 

    def __init__(self,seed:int ,A: int = 16807, C: int = 0, M: int= (2**31) - 1 ):
        self.state = seed
        self.a = A
        self.c = C
        self.m = M

    def next(self):
        """
        Genera el siguiente número aleatorio usando el método del generador congruencial lineal.
        """
        self.state = (self.a * self.state + self.c) % self.m
        return self.state

    def random(self):
        """
        Devuelve un número aleatorio en el rango [0, 1) normalizado.
        """
        return self.next() / self.m


class Xorshift:
    def __init__(self, seed):
        if seed == 0:
            raise ValueError("La semilla debe ser distinta de cero para xorshift32")
        self.state = seed & 0xFFFFFFFF

    def next(self):
        x = self.state
        x ^= (x << 13) & 0xFFFFFFFF # Asegurar que el resultado intermedio sea de 32 bits
        x ^= (x >> 17) # siempre va a ser un entero de 32 bits
        x ^= (x << 5) & 0xFFFFFFFF # Asegurar que el resultado intermedio sea de 32 bits
        self.state = x
        return x 

    def random(self):
        """
        Devuelve un número aleatorio en el rango [0, 1)
        """
        return self.next() / (0xFFFFFFFF +1) # el +1 es panra evitar que el resultado sea 1.0


class Xoshiro:
    """
    Implementación de xoshiro256** para generar números aleatorios.
    """

    MASK64 = 0xFFFFFFFFFFFFFFFF

    def __init__(self, seed): 
        self.state = seed & self.MASK64
        self.s = [self._splitmix64_next() for _ in range(4)]

    def _rotl(self, x, k):
        return ((x << k) | (x >> (64 - k))) & self.MASK64

    def _splitmix64_next(self):
        """
        Generador de números aleatorios SplitMix64.
        Produce un entero de 64 bits a partir del estado actual.
        """
        self.state = (self.state + 0x9E3779B97F4A7C15) & self.MASK64
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & self.MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & self.MASK64
        return z ^ (z >> 31)

    def next(self):
        """
        Genera y devuelve el siguiente número de 64 bits en la secuencia.
        """
        s = self.s
        result = self._rotl(s[1] * 5, 7) * 9 & self.MASK64
        t = (s[1] << 17) & self.MASK64

        s[2] ^= s[0]
        s[3] ^= s[1]
        s[1] ^= s[2]
        s[0] ^= s[3]
        s[2] ^= t
        s[3] = self._rotl(s[3], 45)

        return result

    def random(self):
        """
        Devuelve un número aleatorio en el rango [0, 1).
        """
        return self.next() / (1 << 64)
    
def lambda_t(t):
    return 30 + 30 * math.sin(2*math.pi*t / 24)


#utiliza adelgazamiento para simular arribos que siguen el proceso de poisson no homogeneo
def generar_arribos(T, generador,lambda_max=60):
    Eventos = []
    t = -math.log(generador.random()) / lambda_max # tiempo entre intentos (vars aleatorias con dist exp(lambda_max))
    while t<=T:
        v = generador.random() 
        if v < lambda_t(t) / lambda_max:
            Eventos.append(t)
        t+=-math.log(generador.random()) / lambda_max
    
    return Eventos

def simular(generador,T = 48):
    reloj = 0
    eventos = []  # cola de arribos
    tiempo_fuera = 0  # tiempo total que el servidor está detenido
    lambda_max = 60

    eventos = generar_arribos(T,generador,lambda_max)
    
    cola = []
    i = 0
    while reloj < T or cola:
        # Agregamos llegadas a la cola que ocurrieron hasta el tiempo actual
        while i < len(eventos) and eventos[i] <= reloj:
            cola.append(eventos[i])
            i += 1

        if cola:
            servicio = -math.log(generador.random()) / 40
            reloj += servicio
            cola.pop(0)

            # Añadimos nuevas llegadas ocurridas durante el servicio
            while i < len(eventos) and eventos[i] <= reloj:
                cola.append(eventos[i])
                i += 1
        else:
            if i < len(eventos):
                reloj = eventos[i]
                cola.append(eventos[i])
                i += 1
            else:
               break

    return reloj  # aca habria que devolver todos los datos que se piden para hacer la comparacion

# Pruebas
if __name__ == "__main__":
    # Inicializar el estado (debe ser distinto de cero)
    state_xorshift = Xorshift(123456789)
    state_congruencial = GCL(123456789)
    state_xoshiro = Xoshiro(123456789)

    print(simular(state_xorshift))
    print(simular(state_congruencial))
    print(simular(state_xoshiro))

    '''print("Generando 10 números aleatorios con GCL:")
    for _ in range(10):
        numero_aleatorio = satate_congruencial.next()
        numero_aleatorio_r= satate_congruencial.random()
        print(f"Número: {numero_aleatorio}, Normalizado: {numero_aleatorio_r}")
        

    print("Generando 10 números aleatorios con Xorshift:")
    for _ in range(10):
        numero_aleatorio = state.next()
        numero_aleatorio_r = state.random()
        print(f"Número: {numero_aleatorio}, Normalizado: {numero_aleatorio_r}")

    print("Generando 10 números aleatorios con Xoshiro:")
    for _ in range(10):
        numero_aleatorio = state_xoshiro.next()
        numero_aleatorio_r = state_xoshiro.random()
        print(f"Número: {numero_aleatorio}, Normalizado: {numero_aleatorio_r}")'''
    
        
