#include <hip/hip_runtime.h>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <vector>

void check(hipError_t result) {
  if (result != hipSuccess) throw std::runtime_error(hipGetErrorString(result));
}

struct Buffer {
  float* ptr = nullptr;
  explicit Buffer(size_t bytes) { check(hipMalloc(reinterpret_cast<void**>(&ptr), bytes)); }
  ~Buffer() { if (ptr) hipFree(ptr); }
  Buffer(const Buffer&) = delete;
};

struct Event {
  hipEvent_t value;
  Event() { check(hipEventCreate(&value)); }
  ~Event() { hipEventDestroy(value); }
  Event(const Event&) = delete;
};

__global__ void hip_vector_add(const float* a, const float* b, float* c, int n) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) c[i] = a[i] + b[i];
}

int main() {
  try {
    int count = 0, runtime = 0, driver = 0;
    check(hipGetDeviceCount(&count));
    if (count < 1) {
      std::cout << "{\"status\":\"unavailable\",\"rows\":[]}\n";
      return 2;
    }
    check(hipSetDevice(0));
    check(hipRuntimeGetVersion(&runtime));
    check(hipDriverGetVersion(&driver));
    std::ostringstream rows;
    bool first = true;
    for (int n : {1, 255, 256, 257, 65539}) {
      const size_t bytes = static_cast<size_t>(n) * sizeof(float);
      std::vector<float> a(n), b(n), actual(n);
      for (int i = 0; i < n; ++i) {
        a[i] = static_cast<float>((i % 127) - 63) / 8.0f;
        b[i] = static_cast<float>((i % 31) - 15) / 16.0f;
      }
      Buffer da(bytes), db(bytes), dc(bytes);
      check(hipMemcpy(da.ptr, a.data(), bytes, hipMemcpyHostToDevice));
      check(hipMemcpy(db.ptr, b.data(), bytes, hipMemcpyHostToDevice));
      check(hipMemset(dc.ptr, 0xff, bytes)); // NaN sentinel detects unwritten output.
      auto launch = [&]() {
        hipLaunchKernelGGL(hip_vector_add, dim3((n + 255) / 256), dim3(256), 0, 0,
                          da.ptr, db.ptr, dc.ptr, n);
        check(hipGetLastError());
      };
      launch();
      check(hipDeviceSynchronize());
      check(hipMemcpy(actual.data(), dc.ptr, bytes, hipMemcpyDeviceToHost));
      double max_error = 0.0;
      for (int i = 0; i < n; ++i) {
        double expected = static_cast<double>(a[i]) + static_cast<double>(b[i]);
        if (!std::isfinite(actual[i])) throw std::runtime_error("nonfinite or unwritten result");
        max_error = std::max(max_error, std::abs(actual[i] - expected));
      }
      if (max_error > 1e-6) throw std::runtime_error("vector-add correctness failed");
      for (int warmup = 0; warmup < 3; ++warmup) launch();
      check(hipDeviceSynchronize());
      Event start, stop;
      std::vector<float> samples;
      for (int sample = 0; sample < 7; ++sample) {
        check(hipEventRecord(start.value, 0));
        for (int repeat = 0; repeat < 100; ++repeat) launch();
        check(hipEventRecord(stop.value, 0));
        check(hipEventSynchronize(stop.value));
        float ms = 0;
        check(hipEventElapsedTime(&ms, start.value, stop.value));
        if (!std::isfinite(ms) || ms <= 0) throw std::runtime_error("invalid event timing");
        samples.push_back(ms / 100.0f);
      }
      if (!first) rows << ',';
      first = false;
      rows << "{\"n\":" << n << ",\"max_abs_error\":" << max_error
           << ",\"samples_ms\":[";
      for (size_t i = 0; i < samples.size(); ++i) rows << (i ? "," : "") << samples[i];
      rows << "]}";
    }
    std::cout << "{\"status\":\"passed\",\"device_ordinal\":0,\"runtime_version\":" << runtime
              << ",\"driver_version\":" << driver << ",\"warmup\":3,\"launches_per_sample\":100,"
              << "\"timing_scope\":\"device-event batch average; allocation and copies excluded; launch gaps may be included\",\"rows\":["
              << rows.str() << "]}\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
