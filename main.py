import math
import matplotlib.pyplot as plt

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

def simular(generador, horas=48):
    arribos = generar_arribos(horas, generador)
    tiempo_servidor = 0
    cola_en_espera = 0
    cola_por_hora = [0] * horas
    tiempos_espera = []
    tiempos_en_sistema = []
    uso_por_hora = [0.0] * horas
    tiempos_entre_arribos = [arribos[i+1] - arribos[i] for i in range(len(arribos)-1)]

    for arribo in arribos:
        hora = int(arribo)
        
        if arribo >= tiempo_servidor:
            inicio_servicio = arribo
            cola_en_espera = max(0, cola_en_espera - 1)
        else:
            inicio_servicio = tiempo_servidor
            cola_en_espera += 1

        cola_por_hora[hora] = cola_en_espera

        espera = max(0, inicio_servicio - arribo)
        servicio = generador_atencion(generador)
        salida = inicio_servicio + servicio

        for h in range(int(inicio_servicio), min(int(salida) + 1, horas)):
            uso_por_hora[h] += min(salida, h + 1) - max(inicio_servicio, h)

        tiempos_espera.append(espera)
        tiempos_en_sistema.append(salida - arribo)
        tiempo_servidor = salida

    clientes = len(arribos)
    uso_por_hora = [min(1.0, u) for u in uso_por_hora]
    prom_espera = sum(tiempos_espera) / clientes if clientes else 0
    prom_en_sistema = sum(tiempos_en_sistema) / clientes if clientes else 0
    tiempos_servicio = [t_en_sistema - t_espera for t_en_sistema, t_espera in zip(tiempos_en_sistema, tiempos_espera)]

    return {
        "arribos": arribos,
        "esperas": tiempos_espera,
        "en_sistema": tiempos_en_sistema,
        "tiempos_entre_arribos": tiempos_entre_arribos,
        "cola_por_hora": cola_por_hora,
        "uso_por_hora": uso_por_hora,
        "uso_total": sum(uso_por_hora),
        "clientes": clientes,
        "prom_espera": prom_espera,
        "prom_en_sistema": prom_en_sistema,
        "tiempos_servicio": tiempos_servicio
    }





# Pruebas
if __name__ == "__main__":
    # Inicializar el estado (debe ser distinto de cero)
    state_xorshift = Xorshift(123456789)
    state_congruencial = GCL(1234)
    state_xoshiro = Xoshiro(123456789)

    sim_gcl = simular(state_congruencial)
    sim_xor = simular(state_xorshift)
    sim_xos = simular(state_xoshiro)
    resultados = [sim_gcl, sim_xor, sim_xos]

    #Tasa de utilización del servidor en función del tiempo. Visualizar cómo varía el comportamiento según la hora del día
    labels = ["GCL", "XORShift", "Xoshiro"]

    plt.figure(figsize=(12, 4))

    for i in range(len(resultados)):
        uso = resultados[i]["uso_por_hora"]
        plt.plot(range(48), uso, label=labels[i])

    plt.xlabel("Hora del día")
    plt.ylabel("Tasa de utilización del servidor")
    plt.title("Tasa de Utilización del servidor durante 48 horas")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("grafico_utilizacion.png")

    #El tiempo promedio en el sistema por cliente
    #tiempo en el sistema = tiempo de espera + tiempo de servicio
    promedios = [
    sim_gcl["prom_en_sistema"],
    sim_xor["prom_en_sistema"],
    sim_xos["prom_en_sistema"]
    ]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, promedios, color=["blue", "green", "red"])
    plt.ylabel("Tiempo promedio en el sistema (horas)")
    plt.title("Comparación tiempo promedio en el sistema por generador")
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig("tiempo_promedio_sistema.png")  

    #La distribución de los tiempos de espera
    colores=["blue", "green", "red"]

    plt.figure(figsize=(14, 4))
    plt.suptitle("Tiempos de espera")
    for i in range(3):
        plt.subplot(1, 3, i + 1)
        plt.title(labels[i])
        plt.hist(resultados[i]["esperas"], bins=50, color=colores[i], edgecolor='black')
        plt.xlabel("Horas")
        if i == 0:
            plt.ylabel("Frecuencia")
        plt.grid(True)

    plt.tight_layout()
    plt.savefig("distribucion_tiempos_espera.png")

    #El porcentaje de tiempo que el servidor está ocupado.
    porcentajes_ocupacion = [
    sim_gcl["uso_total"] / 48 * 100,
    sim_xor["uso_total"] / 48 * 100,
    sim_xos["uso_total"] / 48 * 100
    ]

    plt.figure(figsize=(6, 5))
    bars= plt.bar(labels, porcentajes_ocupacion, color=colores)
    plt.ylabel("Porcentaje de tiempo ocupado (%)")
    plt.title("Uso total del servidor por generador")
    plt.ylim(0, 100)
    plt.grid(axis='y')
    plt.tight_layout()
    for bar, porcentaje in zip(bars, porcentajes_ocupacion):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{porcentaje:.2f}%", ha='center', va='bottom', fontsize=10)
    plt.savefig("porcentaje_ocupacion.png")

    #Evolución de la longitud de la cola en el tiempo
    plt.figure(figsize=(12, 5))

    for i in range(3):
        plt.plot(range(48), resultados[i]["cola_por_hora"], label=labels[i], color=colores[i],linewidth=2)

    plt.xlabel("Hora")
    plt.ylabel("Clientes en cola")
    plt.title("Evolución de la longitud de la cola")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("evolucion_largo_cola.png")

    #Histograma de los tiempos de espera en el sistema.
    plt.figure(figsize=(14, 5))
    plt.suptitle("Histograma de los tiempos de espera en el sistema")

    for i in range(3):
        plt.subplot(1, 3, i + 1)
        plt.title(labels[i])
        plt.hist(resultados[i]["esperas"], bins=50, alpha=0.6, label=labels[i], color=colores[i])
        plt.xlabel("Tiempo de espera (horas)")
        if i == 0:
            # Solo la primera subgráfica tiene etiqueta en el eje y
            plt.ylabel("Número de clientes")
        plt.legend()
        plt.grid(True)
    plt.tight_layout()
    plt.savefig("histograma_espera.png")

    #distribución del tiempo entre arribos y de servicios simulados
    plt.figure(figsize=(20, 10))
    plt.suptitle("Distribución de tiempos entre arribos y servicios")
    for i in range(3):
        plt.subplot(2, 3, i + 1)
        plt.title(f"Tiempo entre Arribos:  {labels[i]}")
        # Tiempos entre arribos
        plt.hist(resultados[i]["tiempos_entre_arribos"], bins=50, alpha=0.6, label="Entre arribos", color="blue",edgecolor='black')
        plt.xlabel("Tiempo entre arribos (horas)")
        plt.ylabel("Frecuencia")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        # Tiempos de servicio
        plt.subplot(2, 3, i + 4)
        plt.title(f"Tiempos de Servicio: {labels[i]}")
        plt.hist(resultados[i]["tiempos_servicio"], bins=50, alpha=0.6, label="Servicios", color="red",edgecolor='black')

        plt.xlabel("Tiempo del servicio (horas)")
        plt.ylabel("Frecuencia")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("distribucion_arribos_servicios.png")


    
        
