from qiskit import QuantumCircuit, Aer, transpile, assemble
from qiskit.visualization import plot_histogram
import numpy as np
import random
import time  

def classical_search(target_index, array):
    start_time_classical = time.time()  
    for i, elem in enumerate(array):
        if elem == target_index:
            end_time_classical = time.time()  
            time_taken_classical = end_time_classical - start_time_classical  
            return i, time_taken_classical  
    return -1, 0  

def oracle_circuit(n, marked_element):
    oracle = QuantumCircuit(n, name="oracle")
    
    # Apply X to mark the element
    for qubit in range(n):
        if marked_element & (1 << qubit):
            oracle.x(qubit)
    
    # Apply Z to introduce a phase flip
    oracle.h(n-1)
    oracle.mcx(list(range(n-1)), n-1)  # Multi-controlled Toffoli gate
    oracle.h(n-1)
    
    # Uncompute the X operations
    for qubit in range(n):
        if marked_element & (1 << qubit):
            oracle.x(qubit)
    
    return oracle

#h=Puerta Hadamard, x=puertas X, mcx = multi-control-X (Toffoli)
def grover_circuit(n, marked_element, num_iterations):
    #Crea un circuito con n qubits y n-1 qubits para medir
    grover = QuantumCircuit(n, n-1)
    
    # Se aplica una puerta Hadamard a todos los qubits, para colocarlos en una superposicion uniforme
    grover.h(range(n))
    
    # Realiza el oraculo y la inversion sobre la media num_iterations veces
    for _ in range(num_iterations):
        #Oraculo
        grover.append(oracle_circuit(n, marked_element), range(n)) #Aplica el oraculo (funcion aparte)
        #Inversion sobre la media, que amplian la amplitud de probabilidad de la solucion deseada, aumentando la probabilidad de medirla
        grover.h(range(n))
        grover.x(range(n))
        grover.h(n-1)
        grover.mcx(list(range(n-1)), n-1)  # Multi-controlled Toffoli gate
        grover.h(n-1)
        grover.x(range(n))
        grover.h(range(n))
    
    # Se realiza la medicion, midiendo los n-1 primeros bits
    grover.measure(range(n-1), range(n-1))
    
    return grover

# Simulate the Grover search algorithm
n = 11  # Number of qubits
marked_element = 1023  # Element to be searched (binary: 011)
target = marked_element
rango = 2 ** (n-1)
num_iterations =int(rango ** 0.5)
print(num_iterations)

marked_element = ~marked_element & (2**n - 1)

grover_circuit = grover_circuit(n, marked_element, num_iterations)

# Use the Aer simulator
simulator = Aer.get_backend('qasm_simulator')

# Transpile the circuit for the simulator
tqc = transpile(grover_circuit, simulator)

# Run the simulation
result = simulator.run(tqc, shots=1024).result()

#print(result)
#print(result.get_counts(grover_circuit))
# Get and plot the histogram of the results
counts = result.get_counts(grover_circuit)

#Ordena el diccionario (dict) segun el segundo item (nº apariciones), reverse ture para uqe sea de mayor a menor
counts_ordenado = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
print(counts_ordenado)



print(rango)
array = list(range(rango))

# Desordenar la lista
random.shuffle(array)

# Asegurarse de que el número target está presente
if target not in array:
    # Elegir una posición al azar e insertar el número target
    random_index = random.randint(0, rango)
    array[random_index] = target

result_classical = classical_search(target, array)
print(result_classical)

print("Tiempo del Algoritmo Cuántico:", result.time_taken, "s")
print("Tiempo total de ejecución (Búsqueda Clásica):", result_classical[1], "s")  

#print("Número de Shots:", result.results[0].shots)
print("Número de Iteraciones Clásicas:", result_classical[0] + 1)  
print("Número de Iteraciones Cuánticas:", num_iterations)  

#Encuentra el estado con mayor probabilidad y lo escribe en decimal
value_quantum = int(max(counts, key=counts.get), 2)
if result_classical[0] is not None and array[result_classical[0]] == value_quantum:
    print("¡Los resultados coinciden!")
else:
    print("Los resultados no coinciden.")



