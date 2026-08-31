def classify_counter_row(row: dict[str, float]) -> str:
    if row.get("dram_util_pct", 0) >= 75 and row.get("sm_util_pct", 0) < 70:
        return "memory-bandwidth"
    if row.get("sm_util_pct", 0) >= 75:
        return "compute"
    if row.get("launches", 0) > 1000:
        return "launch-overhead"
    return "mixed-or-unknown"


def main() -> None:
    row = {"dram_util_pct": 86.0, "sm_util_pct": 42.0, "launches": 20}
    print({"status": "ran", "classification": classify_counter_row(row)})


if __name__ == "__main__":
    main()
