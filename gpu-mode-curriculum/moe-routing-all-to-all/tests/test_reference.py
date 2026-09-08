from pathlib import Path
import sys
import unittest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from moe_routing_all_to_all.reference import routed_linear


def scalar_oracle(tokens, logits, weights, top_k, capacity):
    loads = [0] * len(weights)
    outputs = []
    for token, scores in zip(tokens, logits):
        ids = sorted(range(len(weights)), key=lambda e: (-float(scores[e].detach()), e))[:top_k]
        gates = torch.softmax(torch.stack([scores[e] for e in ids]), dim=0)
        output = torch.zeros(weights.shape[1], dtype=tokens.dtype)
        for slot, expert in enumerate(ids):
            if loads[expert] < capacity:
                # Per-output scalar dot products, not the batched expert path.
                computed = torch.stack([sum(token[d] * weights[expert, o, d]
                                            for d in range(token.numel()))
                                        for o in range(weights.shape[1])])
                output = output + gates[slot] * computed
                loads[expert] += 1
        outputs.append(output)
    return torch.stack(outputs) + sum(t.sum() * 0 for t in (tokens, logits, weights))


class MoEReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old_threads = torch.get_num_threads()
        torch.set_num_threads(1)

    @classmethod
    def tearDownClass(cls):
        torch.set_num_threads(cls.old_threads)

    def inputs(self, dtype=torch.float64):
        rng = torch.Generator().manual_seed(241)
        return tuple(torch.randn(shape, dtype=dtype, generator=rng).requires_grad_()
                     for shape in ((7, 3), (7, 4), (4, 2, 3)))

    def test_outputs_and_gradients(self):
        for dtype in (torch.float32, torch.float64):
            for k, capacity in ((1, 7), (2, 3), (4, 1), (2, 0)):
                with self.subTest(dtype=dtype, k=k, capacity=capacity):
                    inputs = self.inputs(dtype)
                    actual, route = routed_linear(*inputs, top_k=k, capacity=capacity)
                    expected = scalar_oracle(*inputs, k, capacity)
                    upstream = torch.arange(actual.numel(), dtype=dtype).reshape_as(actual) / 10
                    for got, ref in zip((actual, *torch.autograd.grad(actual, inputs, upstream)),
                                        (expected, *torch.autograd.grad(expected, inputs, upstream))):
                        torch.testing.assert_close(got, ref, atol=2e-6, rtol=2e-5)
                    self.assertEqual(sum(route["offered_loads"]), 7 * k)
                    self.assertEqual(route["accepted"].sum().item(), sum(route["accepted_loads"]))

    def test_ties_unique_capacity_and_no_renormalization(self):
        tokens = torch.tensor([[2.], [4.], [6.]], dtype=torch.float64)
        logits = torch.zeros((3, 3), dtype=torch.float64)
        weights = torch.tensor([[[1.]], [[3.]], [[9.]]], dtype=torch.float64)
        output, route = routed_linear(tokens, logits, weights, top_k=2, capacity=1)
        self.assertEqual(route["expert_indices"].tolist(), [[0, 1]] * 3)
        self.assertEqual(route["accepted"].tolist(), [[True, True], [False, False], [False, False]])
        self.assertEqual(output.tolist(), [[4.], [0.], [0.]])
        # Expert 0 fills on token 0; token 1 loses half its mass, retaining 0.5*3*4.
        logits[0] = torch.tensor([0., -10., 0.])
        output, route = routed_linear(tokens, logits, weights, top_k=2, capacity=1)
        self.assertEqual(output[1].item(), 6.)
        self.assertEqual(route["accepted"][1].tolist(), [False, True])

    def test_empty_tokens(self):
        output, route = routed_linear(torch.empty(0, 3), torch.empty(0, 4),
                                      torch.ones(4, 2, 3), top_k=2, capacity=0)
        self.assertEqual(tuple(output.shape), (0, 2))
        self.assertEqual(route["dropped_assignments"], 0)

    def test_top_one_selected_softmax_has_no_router_gradient(self):
        tokens = torch.tensor([[2.]], dtype=torch.float64)
        weights = torch.tensor([[[1.]], [[3.]]], dtype=torch.float64)
        logits = torch.tensor([[2., 0.]], dtype=torch.float64, requires_grad=True)
        output, route = routed_linear(tokens, logits, weights, top_k=1, capacity=1)
        self.assertEqual(route["gates"].tolist(), [[1.]])
        self.assertEqual(output.item(), 2.)
        self.assertEqual(torch.autograd.grad(output.sum(), logits)[0].tolist(), [[0., 0.]])
        # Full-expert normalization retains a differentiable selected probability.
        probability = torch.softmax(logits, dim=1)[0, 0]
        alternative = probability * 2
        derivative = torch.autograd.grad(alternative, logits)[0]
        expected = 2 * probability.detach() * (1 - probability.detach())
        torch.testing.assert_close(derivative, torch.stack([expected, -expected])[None])
        self.assertGreater(derivative.abs().sum().item(), 0.)

    def test_top_two_router_can_reduce_fixed_expert_loss(self):
        # A controlled learning mechanism check, not trained-model task quality.
        tokens = torch.tensor([[1.]], dtype=torch.float64)
        weights = torch.tensor([[[0.]], [[2.]]], dtype=torch.float64)
        logits = torch.tensor([[0.2, -0.2]], dtype=torch.float64, requires_grad=True)
        losses = []
        for _ in range(30):
            output, _ = routed_linear(tokens, logits, weights, top_k=2, capacity=1)
            loss = (output - 1.5).square().sum()
            losses.append(loss.item())
            gradient, = torch.autograd.grad(loss, logits)
            with torch.no_grad():
                logits -= 0.2 * gradient
        self.assertLess(losses[-1], losses[0] * 0.01)

    def test_dispatch_combine_identity(self):
        tokens, logits, _ = self.inputs()
        weights = torch.eye(3, dtype=tokens.dtype).repeat(4, 1, 1)
        for capacity in (0, 2, 7):
            actual, route = routed_linear(tokens, logits, weights, top_k=3, capacity=capacity)
            retained_mass = (route["gates"] * route["accepted"]).sum(dim=1)
            torch.testing.assert_close(actual, tokens * retained_mass[:, None])
            if capacity == 7:
                torch.testing.assert_close(actual, tokens)
            self.assertEqual(route["dropped_assignments"], 21 - sum(route["accepted_loads"]))

    def test_noncontiguous_inputs(self):
        contiguous = self.inputs()
        strided = tuple(t.detach().transpose(-1, -2).contiguous().transpose(-1, -2).requires_grad_()
                        for t in contiguous)
        self.assertTrue(all(not t.is_contiguous() for t in strided))
        actual, route = routed_linear(*strided, top_k=2, capacity=3)
        expected, expected_route = routed_linear(*contiguous, top_k=2, capacity=3)
        torch.testing.assert_close(actual, expected)
        self.assertEqual(route["accepted"].tolist(), expected_route["accepted"].tolist())
        for got, ref in zip(torch.autograd.grad(actual.sum(), strided),
                            torch.autograd.grad(expected.sum(), contiguous)):
            torch.testing.assert_close(got, ref)

    def test_finite_difference_away_from_routing_boundaries(self):
        tokens, _, weights = self.inputs()
        tokens = tokens[:3].detach().requires_grad_()
        # Clear ordering prevents perturbations from changing discrete top-k.
        logits = torch.tensor([[4., 2., 0., -2.], [0., 4., 2., -2.],
                               [2., 0., 4., -2.]], dtype=torch.float64, requires_grad=True)
        self.assertTrue(torch.autograd.gradcheck(
            lambda x, l, w: routed_linear(x, l, w, top_k=2, capacity=1)[0],
            (tokens, logits, weights), eps=1e-6, atol=1e-5, rtol=1e-3))

    def test_all_dropped_large_finite_values_have_zero_gradients(self):
        inputs = tuple(torch.full(shape, 1e38, dtype=torch.float32, requires_grad=True)
                       for shape in ((7, 3), (7, 4), (4, 2, 3)))
        output, _ = routed_linear(*inputs, top_k=2, capacity=0)
        self.assertTrue(torch.equal(output, torch.zeros_like(output)))
        for gradient in torch.autograd.grad(output.sum(), inputs):
            self.assertTrue(torch.equal(gradient, torch.zeros_like(gradient)))

    def test_invalid_contracts(self):
        for k, capacity in ((0, 1), (5, 1), (True, 1), (1, -1), (1, True)):
            with self.assertRaises(ValueError):
                routed_linear(*self.inputs(), top_k=k, capacity=capacity)
        tokens, logits, weights = self.inputs()
        logits = logits.detach()
        logits[0, 0] = float("nan")
        with self.assertRaises(ValueError):
            routed_linear(tokens, logits, weights, top_k=2, capacity=2)


if __name__ == "__main__":
    unittest.main()
