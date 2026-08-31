def classify(flops: float, bytes_moved: float, peak_tflops: float, peak_gbps: float) -> dict[str, float | str]:
    arithmetic_intensity = flops / bytes_moved
    compute_ceiling = peak_tflops * 1e12
    memory_ceiling = arithmetic_intensity * peak_gbps * 1e9
    bound = "memory-bandwidth" if memory_ceiling < compute_ceiling else "compute"
    return {"arithmetic_intensity": round(arithmetic_intensity, 4), "bound": bound}


def main() -> None:
    print(classify(flops=2 * 4096**3, bytes_moved=3 * 4096**2 * 2, peak_tflops=125, peak_gbps=3000))


if __name__ == "__main__":
    main()
