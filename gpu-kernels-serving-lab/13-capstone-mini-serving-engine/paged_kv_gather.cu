#include <cuda_runtime.h>

// Gather a logical sequence from fixed-size pages into a contiguous KV view.
// One block handles one (sequence, head, token) row; threads cover head_dim.
__global__ void paged_kv_gather(const float* pages, const int* page_table,
                                const int* lengths, float* output,
                                int sequences, int max_pages, int heads,
                                int page_size, int head_dim, int max_tokens) {
    int row = blockIdx.x;
    int total_rows = sequences * heads * max_tokens;
    if (row >= total_rows) return;
    int token = row % max_tokens;
    int head = (row / max_tokens) % heads;
    int sequence = row / (max_tokens * heads);
    if (token >= lengths[sequence]) return;
    int page_index = token / page_size;
    int in_page = token % page_size;
    int physical_page = page_table[sequence * max_pages + page_index];
    for (int d = threadIdx.x; d < head_dim; d += blockDim.x) {
        size_t source = (((size_t)physical_page * heads + head) * page_size + in_page) * head_dim + d;
        size_t destination = (((size_t)sequence * heads + head) * max_tokens + token) * head_dim + d;
        output[destination] = pages[source];
    }
}
