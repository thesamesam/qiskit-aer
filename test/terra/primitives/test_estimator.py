# This code is part of Qiskit.
#
# (C) Copyright IBM 2022.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Estimator class tests
"""


import unittest
from test.terra.common import QiskitAerTestCase

import numpy as np
from ddt import data, ddt
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.library import RealAmplitudes
from qiskit.exceptions import QiskitError
from qiskit.opflow import PauliSumOp
from qiskit.primitives import EstimatorResult
from qiskit.quantum_info import Operator, SparsePauliOp

from qiskit_aer.primitives import Estimator


@ddt
class TestEstimator(QiskitAerTestCase):
    """Testing estimator class"""

    def setUp(self):
        super().setUp()
        self.ansatz = RealAmplitudes(num_qubits=2, reps=2)
        self.observable = SparsePauliOp.from_list(
            [
                ("II", -1.052373245772859),
                ("IZ", 0.39793742484318045),
                ("ZI", -0.39793742484318045),
                ("ZZ", -0.01128010425623538),
                ("XX", 0.18093119978423156),
            ]
        )
        self.expval = -1.284366511861733
        self.expval_rev = -0.5140997668602956

    @data(True, False)
    def test_estimator(self, abelian_grouping):
        """test for a simple use case"""
        lst = [("XX", 1), ("YY", 2), ("ZZ", 3)]
        with self.subTest("PauliSumOp"):
            observable = PauliSumOp.from_list(lst)
            ansatz = RealAmplitudes(num_qubits=2, reps=2)
            est = Estimator(abelian_grouping=abelian_grouping)
            result = est.run(
                ansatz, observable, parameter_values=[[0, 1, 1, 2, 3, 5]], seed=15
            ).result()
            self.assertIsInstance(result, EstimatorResult)
            np.testing.assert_allclose(result.values, [1.728515625])

        with self.subTest("SparsePauliOp"):
            observable = SparsePauliOp.from_list(lst)
            ansatz = RealAmplitudes(num_qubits=2, reps=2)
            est = Estimator(abelian_grouping=abelian_grouping)
            result = est.run(
                ansatz, observable, parameter_values=[[0, 1, 1, 2, 3, 5]], seed=15
            ).result()
            self.assertIsInstance(result, EstimatorResult)
            np.testing.assert_allclose(result.values, [1.728515625])

    @data(True, False)
    def test_init_observable_from_operator(self, abelian_grouping):
        """test for evaluate without parameters"""
        circuit = self.ansatz.bind_parameters([0, 1, 1, 2, 3, 5])
        matrix = Operator(
            [
                [-1.06365335, 0.0, 0.0, 0.1809312],
                [0.0, -1.83696799, 0.1809312, 0.0],
                [0.0, 0.1809312, -0.24521829, 0.0],
                [0.1809312, 0.0, 0.0, -1.06365335],
            ]
        )
        est = Estimator(abelian_grouping=abelian_grouping)
        result = est.run([circuit], [matrix], seed=15, shots=8192).result()
        self.assertIsInstance(result, EstimatorResult)
        np.testing.assert_allclose(result.values, [self.expval], rtol=0.02)

    @data(True, False)
    def test_evaluate(self, abelian_grouping):
        """test for evaluate"""
        est = Estimator(abelian_grouping=abelian_grouping)
        result = est.run(
            self.ansatz, self.observable, parameter_values=[[0, 1, 1, 2, 3, 5]], seed=15, shots=8192
        ).result()
        self.assertIsInstance(result, EstimatorResult)
        np.testing.assert_allclose(result.values, [self.expval], rtol=0.02)

    @data(True, False)
    def test_evaluate_multi_params(self, abelian_grouping):
        """test for evaluate with multiple parameters"""
        est = Estimator(abelian_grouping=abelian_grouping)
        result = est.run(
            [self.ansatz] * 2,
            [self.observable] * 2,
            parameter_values=[[0, 1, 1, 2, 3, 5], [5, 3, 2, 1, 1, 0]],
            seed=15,
        ).result()
        self.assertIsInstance(result, EstimatorResult)
        np.testing.assert_allclose(result.values, [self.expval, self.expval_rev], rtol=0.02)

    @data(True, False)
    def test_evaluate_no_params(self, abelian_grouping):
        """test for evaluate without parameters"""
        circuit = self.ansatz.bind_parameters([0, 1, 1, 2, 3, 5])
        est = Estimator(abelian_grouping=abelian_grouping)
        result = est.run(circuit, self.observable, seed=15, shots=8192).result()
        self.assertIsInstance(result, EstimatorResult)
        np.testing.assert_allclose(result.values, [self.expval], rtol=0.02)

    @data(True, False)
    def test_run_with_multiple_observables_and_none_parameters(self, abelian_grouping):
        """test for evaluate without parameters"""
        circuit = QuantumCircuit(3)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        est = Estimator(abelian_grouping=abelian_grouping)
        result = est.run(
            [circuit] * 2, [SparsePauliOp("ZZZ"), SparsePauliOp("III")], seed=15
        ).result()
        self.assertIsInstance(result, EstimatorResult)
        np.testing.assert_allclose(result.values, [0.00390625, 1.0])

    @data(True, False)
    def test_1qubit(self, abelian_grouping):
        """Test for 1-qubit cases"""
        qc0 = QuantumCircuit(1)
        qc1 = QuantumCircuit(1)
        qc1.x(0)

        op0 = SparsePauliOp.from_list([("I", 1)])
        op1 = SparsePauliOp.from_list([("Z", 1)])

        est = Estimator(abelian_grouping=abelian_grouping)
        with self.subTest("test circuit 0, observable 0"):
            result = est.run(qc0, op0).result()
            self.assertIsInstance(result, EstimatorResult)
            np.testing.assert_allclose(result.values, [1])

        with self.subTest("test circuit 0, observable 1"):
            result = est.run(qc0, op1).result()
            self.assertIsInstance(result, EstimatorResult)
            np.testing.assert_allclose(result.values, [1])

        with self.subTest("test circuit 1, observable 0"):
            result = est.run(qc1, op0).result()
            self.assertIsInstance(result, EstimatorResult)
            np.testing.assert_allclose(result.values, [1])

        with self.subTest("test circuit 1, observable 1"):
            result = est.run(qc1, op1).result()
            self.assertIsInstance(result, EstimatorResult)
            np.testing.assert_allclose(result.values, [-1])

    @data(True, False)
    def test_2qubits(self, abelian_grouping):
        """Test for 2-qubit cases (to check endian)"""
        qc0 = QuantumCircuit(2)
        qc1 = QuantumCircuit(2)
        qc1.x(0)

        op0 = SparsePauliOp.from_list([("II", 1)])
        op1 = SparsePauliOp.from_list([("ZI", 1)])
        op2 = SparsePauliOp.from_list([("IZ", 1)])

        est = Estimator(abelian_grouping=abelian_grouping)
        with self.subTest("test circuit 0, observable 0"):
            result = est.run(qc0, op0).result()
            self.assertIsInstance(result, EstimatorResult)
            np.testing.assert_allclose(result.values, [1])

        with self.subTest("test circuit 1, observable 0"):
            result = est.run(qc1, op0).result()
            self.assertIsInstance(result, EstimatorResult)
            np.testing.assert_allclose(result.values, [1])

        with self.subTest("test circuit 0, observable 1"):
            result = est.run(qc0, op1).result()
            self.assertIsInstance(result, EstimatorResult)
            np.testing.assert_allclose(result.values, [1])

        with self.subTest("test circuit 1, observable 1"):
            result = est.run(qc1, op1).result()
            self.assertIsInstance(result, EstimatorResult)
            np.testing.assert_allclose(result.values, [1])

        with self.subTest("test circuit 0, observable 2"):
            result = est.run(qc0, op2).result()
            self.assertIsInstance(result, EstimatorResult)
            np.testing.assert_allclose(result.values, [1])

        with self.subTest("test circuit 1, observable 2"):
            result = est.run(qc1, op2).result()
            self.assertIsInstance(result, EstimatorResult)
            np.testing.assert_allclose(result.values, [-1])

    @data(True, False)
    def test_empty_parameter(self, abelian_grouping):
        """Test for empty parameter"""
        n = 2
        qc = QuantumCircuit(n)
        op = SparsePauliOp.from_list([("I" * n, 1)])
        estimator = Estimator(abelian_grouping=abelian_grouping)
        with self.subTest("one circuit"):
            result = estimator.run(qc, op, shots=1000).result()
            np.testing.assert_allclose(result.values, [1])
            self.assertEqual(len(result.metadata), 1)

        with self.subTest("two circuits"):
            result = estimator.run([qc] * 2, [op] * 2, shots=1000).result()
            np.testing.assert_allclose(result.values, [1, 1])
            self.assertEqual(len(result.metadata), 2)

    @data(True, False)
    def test_numpy_params(self, abelian_grouping):
        """Test for numpy array as parameter values"""
        qc = RealAmplitudes(num_qubits=2, reps=2)
        op = SparsePauliOp.from_list([("IZ", 1), ("XI", 2), ("ZY", -1)])
        k = 5
        params_array = np.random.rand(k, qc.num_parameters)
        params_list = params_array.tolist()
        params_list_array = list(params_array)
        estimator = Estimator(abelian_grouping=abelian_grouping)
        target = estimator.run([qc] * k, [op] * k, params_list, seed=15).result()

        with self.subTest("ndarrary"):
            result = estimator.run([qc] * k, [op] * k, params_array, seed=15).result()
            self.assertEqual(len(result.metadata), k)
            np.testing.assert_allclose(result.values, target.values)

        with self.subTest("list of ndarray"):
            result = estimator.run([qc] * k, [op] * k, params_list_array, seed=15).result()
            self.assertEqual(len(result.metadata), k)
            np.testing.assert_allclose(result.values, target.values)

    @data(True, False)
    def test_with_shots_option_with_approximation(self, abelian_grouping):
        """test with shots option."""
        # Note: abelian_gropuing is ignored when approximation is True as documented.
        # The purpose of this test is to make sure the results remain the same.
        est = Estimator(approximation=True, abelian_grouping=abelian_grouping)
        result = est.run(
            self.ansatz, self.observable, parameter_values=[[0, 1, 1, 2, 3, 5]], shots=1024, seed=15
        ).result()
        self.assertIsInstance(result, EstimatorResult)
        np.testing.assert_allclose(result.values, [-1.3088991960117797])

    def test_with_shots_option_without_approximation(self):
        """test with shots option."""
        est = Estimator(approximation=False, abelian_grouping=False)
        result = est.run(
            self.ansatz, self.observable, parameter_values=[[0, 1, 1, 2, 3, 5]], shots=1024, seed=15
        ).result()
        self.assertIsInstance(result, EstimatorResult)
        np.testing.assert_allclose(result.values, [-1.2895828299114598])


if __name__ == "__main__":
    unittest.main()
