def estimate_kv_cache_mb(batch: int, sequence: int, layers: int, hidden: int, bytes_per_value: int = 2) -> float:
    keys_and_values = 2
    return batch * sequence * layers * hidden * keys_and_values * bytes_per_value / 1e6


def main() -> None:
    print({"status": "ran", "kv_cache_mb": round(estimate_kv_cache_mb(1, 8192, 32, 4096), 2)})


if __name__ == "__main__":
    main()
