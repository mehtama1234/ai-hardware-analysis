import sys
import unittest
import json
import threading
import urllib.request
import urllib.error
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "13-capstone-mini-serving-engine"))
from neural_generator import CharacterModel, NeuralGenerator
import server


class NeuralServingTests(unittest.TestCase):
    def setUp(self):
        self.threads = torch.get_num_threads()
        torch.set_num_threads(1)
        self.generator = NeuralGenerator()

    def tearDown(self):
        torch.set_num_threads(self.threads)

    def test_cached_matches_full_autoregression(self):
        for prompt in ("a", "hello gpu", "z" * 120):
            cached, cache_logits = self.generator.generate(prompt, 8)
            full, full_logits = self.generator.generate(prompt, 8, cached=False)
            self.assertEqual(cached, full)
            for a, b in zip(cache_logits, full_logits):
                torch.testing.assert_close(a, b, atol=2e-6, rtol=2e-5)

    def test_trained_state_dict_can_cross_into_serving_generator(self):
        torch.manual_seed(8181)
        source = CharacterModel(context=128, hidden=128, heads=8).eval()
        trained = NeuralGenerator(
            hidden=128, heads=8,
            state_dict={key: value.clone() for key, value in source.state_dict().items()},
            model_name="trained-synthetic-character",
        )
        reference, _ = trained.generate("hello gpu", 6, cached=False)
        cached, _ = trained.generate("hello gpu", 6, cached=True)
        self.assertEqual(reference, cached)
        self.assertEqual(trained.model_name, "trained-synthetic-character")

    def test_request_isolation_and_batch(self):
        before = self.generator.complete("hello", 4)
        self.generator.complete("different", 6)
        self.assertEqual(before, self.generator.complete("hello", 4))
        batch = self.generator.complete_batch(["hello", "gpu"], 4)
        self.assertEqual(batch["choices"][0]["text"], before["text"])
        self.assertEqual(batch["prefix_tokens_reused"], 0)
        self.assertEqual(batch["completion_tokens"], 8)

    def test_invalid_requests(self):
        for prompt, count in (("", 1), ("x", 0), ("x", True), ("x" * 128, 1)):
            with self.assertRaises(ValueError):
                self.generator.complete(prompt, count)

    def test_http_neural_completion(self):
        previous = server.GENERATOR
        server.GENERATOR = self.generator
        http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        worker = threading.Thread(target=http.serve_forever, daemon=True)
        worker.start()
        try:
            base = f"http://127.0.0.1:{http.server_port}"
            for path, body in (("completions", {"prompt": "hello", "max_tokens": 4}),
                               ("batch_completions", {"prompts": ["hello", "gpu"], "max_tokens": 4})):
                request = urllib.request.Request(base + "/v1/" + path,
                    data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(request, timeout=10) as response:
                    result = json.load(response)
                self.assertEqual(result["model"], self.generator.model_name)
                self.assertEqual(result["choices"][0]["text"], self.generator.complete("hello", 4)["text"])
                self.assertEqual(result["backend"], self.generator.backend)
            for body in ([], {"prompt": 12}, {"prompt": "x", "max_tokens": True},
                         {"prompt": "x", "max_tokens": "4"},
                         {"prompt": "x" * 128, "max_tokens": 1}):
                request = urllib.request.Request(base + "/v1/completions",
                    data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    urllib.request.urlopen(request, timeout=10)
                self.assertEqual(caught.exception.code, 400)
                caught.exception.close()
        finally:
            http.shutdown()
            http.server_close()
            worker.join(timeout=10)
            server.GENERATOR = previous

    def test_request_resource_limits(self):
        for body in ({"prompts": "not a list"}, {"prompts": []},
                     {"prompts": ["x"] * 17}, {"prompts": [None]},
                     {"prompts": ["x" * 4097]}, {"prompts": ["x"], "max_tokens": 129}):
            with self.assertRaises(ValueError):
                server.validate_request(body, batch=True)

    def test_neural_decode_honors_cancellation_event(self):
        cancelled = threading.Event()
        cancelled.set()
        with self.assertRaises(RuntimeError):
            self.generator.complete("hello", 4, cancel_event=cancelled)

    def test_vectorized_neural_decode_honors_cancellation_events(self):
        cancelled = threading.Event()
        cancelled.set()
        with self.assertRaises(RuntimeError):
            self.generator.complete_batch(["hello", "hello"], 4, cancel_events=[cancelled, threading.Event()])


if __name__ == "__main__":
    unittest.main()
