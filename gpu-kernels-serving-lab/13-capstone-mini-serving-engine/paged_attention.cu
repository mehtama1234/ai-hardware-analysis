#include <cuda_runtime.h>
#include <math.h>

// Correctness-first paged attention reference. One block handles one
// (sequence, head) query; thread 0 evaluates the bounded softmax and all
// threads cooperate on the final value accumulation. The page-table access is
// the same indirection a production paged-KV kernel must preserve.
__global__ void paged_attention(const float* query, const float* pages,
                                const int* page_table, const int* lengths,
                                float* output, int sequences, int max_pages,
                                int heads, int page_size, int head_dim,
                                int max_tokens) {
    int row = blockIdx.x;
    if (row >= sequences * heads) return;
    int sequence = row / heads, head = row % heads, length = lengths[sequence];
    __shared__ float scores[128];
    __shared__ float normalizer;
    if (threadIdx.x == 0) {
        float max_score = -1.0e30f;
        for (int token = 0; token < length; ++token) {
            int physical = page_table[sequence * max_pages + token / page_size];
            int in_page = token % page_size;
            float dot = 0.0f;
            for (int d = 0; d < head_dim; ++d) {
                size_t qi = ((size_t)sequence * heads + head) * head_dim + d;
                size_t ki = (((size_t)physical * heads + head) * page_size + in_page) * head_dim + d;
                dot += query[qi] * pages[ki];
            }
            scores[token] = dot / sqrtf((float)head_dim);
            max_score = fmaxf(max_score, scores[token]);
        }
        float sum = 0.0f;
        for (int token = 0; token < length; ++token) { scores[token] = expf(scores[token] - max_score); sum += scores[token]; }
        normalizer = sum;
    }
    __syncthreads();
    for (int d = threadIdx.x; d < head_dim; d += blockDim.x) {
        float value = 0.0f;
        for (int token = 0; token < length; ++token) {
            int physical = page_table[sequence * max_pages + token / page_size];
            int in_page = token % page_size;
            size_t vi = (((size_t)physical * heads + head) * page_size + in_page) * head_dim + d;
            value += (scores[token] / normalizer) * pages[vi];
        }
        output[((size_t)sequence * heads + head) * head_dim + d] = value;
    }
}
