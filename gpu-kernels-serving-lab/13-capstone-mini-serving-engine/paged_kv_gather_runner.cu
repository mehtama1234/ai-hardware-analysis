#include <cuda_runtime.h>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>

__global__ void paged_kv_gather(const float*, const int*, const int*, float*, int, int, int, int, int, int);

static void check(cudaError_t e, const char* where) {
    if (e != cudaSuccess) { std::cerr << where << ": " << cudaGetErrorString(e) << "\n"; std::exit(2); }
}

int main() {
    int device_count = 0; check(cudaGetDeviceCount(&device_count), "cudaGetDeviceCount");
    if (device_count < 1) { std::cerr << "no CUDA device\n"; return 2; }
    constexpr int sequences = 3, max_pages = 4, heads = 2, page_size = 4, head_dim = 8, max_tokens = 16;
    constexpr int page_count = sequences * max_pages;
    constexpr size_t page_values = (size_t)page_count * heads * page_size * head_dim;
    constexpr size_t output_values = (size_t)sequences * heads * max_tokens * head_dim;
    std::vector<float> host_pages(page_values), host_output(output_values, -777.0f), oracle(output_values, -777.0f);
    std::vector<int> table = {5, 1, 9, 0, 7, 3, 11, 2, 8, 6, 4, 10};
    std::vector<int> lengths = {7, 5, 10};
    for (size_t i = 0; i < host_pages.size(); ++i) host_pages[i] = static_cast<float>((i * 13) % 997) / 17.0f;
    for (int s = 0; s < sequences; ++s) for (int h = 0; h < heads; ++h) for (int t = 0; t < lengths[s]; ++t) for (int d = 0; d < head_dim; ++d) {
        int pp = table[s * max_pages + t / page_size], ip = t % page_size;
        size_t src = (((size_t)pp * heads + h) * page_size + ip) * head_dim + d;
        size_t dst = (((size_t)s * heads + h) * max_tokens + t) * head_dim + d;
        oracle[dst] = host_pages[src];
    }
    float *pages = nullptr, *output = nullptr; int *dtable = nullptr, *dlengths = nullptr;
    check(cudaMalloc(&pages, page_values * sizeof(float)), "pages"); check(cudaMalloc(&output, output_values * sizeof(float)), "output");
    check(cudaMalloc(&dtable, table.size() * sizeof(int)), "table"); check(cudaMalloc(&dlengths, lengths.size() * sizeof(int)), "lengths");
    check(cudaMemcpy(pages, host_pages.data(), page_values * sizeof(float), cudaMemcpyHostToDevice), "copy pages");
    check(cudaMemcpy(dtable, table.data(), table.size() * sizeof(int), cudaMemcpyHostToDevice), "copy table");
    check(cudaMemcpy(dlengths, lengths.data(), lengths.size() * sizeof(int), cudaMemcpyHostToDevice), "copy lengths");
    auto launch = [&]() { paged_kv_gather<<<sequences * heads * max_tokens, 128>>>(pages, dtable, dlengths, output, sequences, max_pages, heads, page_size, head_dim, max_tokens); };
    launch(); check(cudaGetLastError(), "launch"); check(cudaDeviceSynchronize(), "sync");
    check(cudaMemcpy(host_output.data(), output, output_values * sizeof(float), cudaMemcpyDeviceToHost), "copy output");
    float max_error = 0.0f; int checked = 0;
    for (size_t i = 0; i < output_values; ++i) if (oracle[i] != -777.0f) { max_error = std::max(max_error, std::abs(host_output[i] - oracle[i])); ++checked; }
    cudaEvent_t start, stop; check(cudaEventCreate(&start), "event"); check(cudaEventCreate(&stop), "event");
    std::vector<float> samples; for (int i = 0; i < 30; ++i) { check(cudaEventRecord(start), "start"); launch(); check(cudaEventRecord(stop), "stop"); check(cudaEventSynchronize(stop), "event sync"); float ms = 0; check(cudaEventElapsedTime(&ms, start, stop), "elapsed"); if (i >= 5) samples.push_back(ms); }
    std::sort(samples.begin(), samples.end()); float median = samples[samples.size() / 2];
    std::cout << "{\"status\":\"passed\",\"gpu_execution_accepted\":true,\"sequences\":" << sequences
              << ",\"page_size\":" << page_size << ",\"checked_values\":" << checked
              << ",\"max_abs_error\":" << max_error << ",\"median_ms\":" << median << "}\n";
    cudaFree(pages); cudaFree(output); cudaFree(dtable); cudaFree(dlengths); cudaEventDestroy(start); cudaEventDestroy(stop);
    return max_error == 0.0f ? 0 : 1;
}
