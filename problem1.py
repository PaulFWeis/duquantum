import itertools
import math

import cirq
import cirq_google
import numpy as np
from typing import Literal


def create_ghz_state(qubits: set[cirq.GridQubit], part: Literal['a','b','c']) -> cirq.Circuit:
    """Create a GHZ state on the specified qubits.

    Args:
        qubits: The qubits on which to prepare the state
        part: Which part of the question this is meant to solve.

    Returns:
        A circuit that creates a GHZ state on these qubits.
    """
def prob1c(qubits):
    circuit = cirq.Circuit(cirq.H(qubits[0]))
    row=len(set(q.col for q in qubits))
    col=len(set(q.row for q in qubits))
    measured = []

    for r in range(row):
        for c in range(col):
            if r==0 or c==0:
                measured.append(cirq.GridQubit(r,c))
    q0=measured[0]
    circuit.append(cirq.Moment(
        cirq.measure(q0, key='control'),
        cirq.measure(*measured[1:], key='others')
    ))
    for q in qubits:
        if q!=q0:
            circuit.append(cirq.X(q).with_classical_controls('control'))

    circuit.append(cirq.measure(*qubits, key="result"))
    print(circuit)


    simulator = cirq.Simulator()
    results = simulator.run(circuit, repetitions=1000)
    print("Counts:", results.histogram(key="result"))

def check_ghz_statevector(
        circuit: cirq.Circuit,
        qubits: set[cirq.GridQubit],
        num_trials: int = 10, # this can be 1 unless the circuit is adaptive
        sampler: cirq.SimulatesFinalState = cirq.Simulator()
        ) -> bool:
    all_qubits = circuit.all_qubits()
    ancilla_qubits = all_qubits.difference(qubits)
    ordered_qubits = sorted(qubits) + sorted(ancilla_qubits)
    keep_indices = range(qubits)
    num_qubits = len(qubits)
    ideal_state = np.zeros(2**num_qubits)
    ideal_state[0] = 1 / np.sqrt(2)
    ideal_state[-1] = 1 / np.sqrt(2)
    for _ in range(num_trials):
        psi_circuit_full = sampler.simulate(circuit, qubit_order=ordered_qubits).final_state_vector
        psi_circuit = cirq.sub_state_vector(
            state_vector=psi_circuit_full,
            keep_indices=keep_indices
        ) if len(all_qubits) > len(qubits) else psi_circuit_full
        if not np.isclose(np.abs(ideal_state @ psi_circuit) ** 2, 1.0):
            return False
    return True

def test_operations_on_adjacent_qubits(circuit: cirq.Circuit):
    for op in circuit.all_operations():
        assert len(op.qubits) <= 2
        if len(op.qubits) == 2:
            assert op.gate == cirq.CZ
            dy = abs(op.qubits[0].row - op.qubits[1].row)
            dx = abs(op.qubits[0].col - op.qubits[1].col)
            assert dx in {0, 1}
            assert dy in {0, 1}
            assert dx + dy == 1

# we may add additional qubit choices beyond these
qubit_choices = [
    cirq.GridQubit.rect(1, 20),
    cirq.GridQubit.rect(4, 5),
    cirq_google.Willow105.metadata.qubit_set,
]
score = sum(
    len(qubits) ** 2 / len(create_ghz_state(qubits)) for qubits in qubit_choices
)
