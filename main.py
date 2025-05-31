class Generadores: 
    M: int = (2**31) - 1  

    def congruencial_lineal(self,y: int, a: int = 16807, c: int = 0, m: int = M):
        return ((a*y) + c) % m
    
    def xor_shift_32(self,x:int,a:int = 13,b=17,c=5):
        x ^= (x << a) & 0xFFFFFFFF
        x ^= (x >> b)
        x ^= (x << c) & 0xFFFFFFFF

        return x & 0xFFFFFFFF
    