import math

class GCL: 

    def __init__(self,seed:int ,A: int = 16807, C: int = 0, M: int= (2**31) - 1 ):
        self.state = seed
        self.a = A
        self.c = C
        self.m = M

    def next(self):
        """
        Genera el siguiente número pseudoaleatorio usando el método del generador congruencial lineal.
        """
        self.state = (self.a * self.state + self.c) % self.m
        return self.state

    def random(self):
        """
        Devuelve un número pseudoaleatorio en el rango [0, 1) normalizado.
        """
        return self.next() / self.m


class Xorshift:
    def __init__(self, seed):
        if seed == 0:
            raise ValueError("La semilla debe ser distinta de cero para xorshift32")
        self.state = seed & 0xFFFFFFFF

    def next(self):
        """Algotimo Xorshift"""
        x = self.state
        x ^= (x << 13) & 0xFFFFFFFF # Asegurar que el resultado intermedio sea de 32 bits
        x ^= (x >> 17) # siempre va a ser un entero de 32 bits
        x ^= (x << 5) & 0xFFFFFFFF # Asegurar que el resultado sea de 32 bits
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


"""Funciones de utilidad para la simulación""" 
def lambda_t(t):
    return 30 + 30 * math.sin(2 * math.pi * t / 24)


#utiliza adelgazamiento para simular arribos que siguen el proceso de poisson no homogeneo
def generar_arribos(T, generador,lambda_max=60):
    eventos = []
    x = generador.random()
    t = -math.log(x) / lambda_max # tiempo entre intentos (vars aleatorias con dist exp(lambda_max))
    while t<=T:
        v = generador.random() 
        if v < lambda_t(t) / lambda_max:
            eventos.append(t)
        t += -math.log(generador.random()) / lambda_max
    
    return eventos

# Generador de tiempos de atención con distribución exponencial
def generador_atencion(generador, lambda_=40):
    x = generador.random() 
    return -math.log(1-x)/lambda_

def simular(generador,Horas = 48):
    arribos = generar_arribos(Horas,generador)
    print(f"Cantidad de arribos: {len(arribos)}")
    tiempo_servidor = 0
    cola_por_hora = [0] * Horas
    i = 0
    print(f"Simulación con generador: {generador.__class__.__name__}")

    for arribo in arribos:
        i += 1
        t_arribo = int(arribo)

        if i in [1, 500, 1000, 1500]: 
            print(f"Arribo {i}: {arribo:.4f}")
        if arribo >= tiempo_servidor:
            tiempo_inicio = arribo
            if i in [1, 500, 1000, 1500]:
                print(f"Tiempo de inicio de servicio: {tiempo_inicio:.4f}")
        else:
            tiempo_inicio = tiempo_servidor
            cola_por_hora[t_arribo] += 1
            if i in [1, 500, 1000, 1500]:
                print(f"Tiempo de inicio de servicio (con cola): {tiempo_inicio:.4f}")
        
        servicio = generador_atencion(generador)
        if i in [1, 500, 1000, 1500]:
            print(f"Tiempo de servicio: {servicio:.4f}")
        tiempo_salida = tiempo_inicio + servicio
        if i in [1, 500, 1000, 1500]:
            print(f"Tiempo de salida de servicio: {tiempo_salida:.4f}")
        tiempo_servidor = tiempo_salida
        if i in [1, 500, 1000, 1500]:
            print(f"El cliente {i} fue atendido en la hora {int(tiempo_servidor)}")
        if i in [1, 500, 1000, 1500]: print("\n")

    return {
    "arribos": arribos,
    "cola_por_hora": cola_por_hora,
    "ocupado": tiempo_servidor,
    "clientes": len(arribos),
}


# Pruebas
if __name__ == "__main__":
    # Inicializar el estado (debe ser distinto de cero)
    state_xorshift = Xorshift(123456789)
    state_congruencial = GCL(1234)
    state_xoshiro = Xoshiro(123456789)

    sim = simular(state_xorshift)
    sim = simular(state_congruencial)
    sim = simular(state_xoshiro)
    print(sim['arribos'])
    print(f"Tiempo total de simulación: {sim['cola_por_hora']} horas")
    print(f"Tiempo ocupado por el servidor: {sim['ocupado']:.4f} horas")
    print(f"Clientes atendidos: {sim['clientes']}")

    
        
