import matplotlib.pyplot as plt
from typing import Dict, List, Tuple


def parse_benchmark_results(file_path: str) -> Dict[str, List[Tuple[int, float, bool]]]:
    """
    Parse benchmark results from a file.

    Args:
        file_path: Path to the benchmark results file.

    Returns:
        A dictionary where keys are algorithm names and values are lists of tuples (file_size, execution_time).
    """
    with open(file_path, "r") as f:
        lines = f.readlines()

    lines = lines[1:]  # Skip the header line

    results: Dict[str, List[Tuple[int, float, bool]]] = {}

    for line in lines:
        parts = line.strip().split()
        if len(parts) == 4:
            algorithm = parts[0]
            size = int(parts[1])
            time = float(parts[2])
            reread = parts[3] == "1"

            if algorithm not in results:
                results[algorithm] = []
            results[algorithm].append((size, time, reread))

    return results


def plot_results(
    results: Dict[str, List[Tuple[int, float, bool]]], reread: bool
) -> None:
    """
    Plot the benchmark results.

    Args:
        results: A dictionary where keys are algorithm names and values are lists of tuples (file_size, execution_time).
        reread: Boolean indicating whether to plot results for REREAD_ON_QUERY=True or False.
    """
    plt.figure(figsize=(10, 6))

    for algorithm, data in results.items():
        data = sorted(data)
        relevant_data = [
            (size, time) for size, time, reread_flag in data if reread_flag == reread
        ]

        if relevant_data:
            sizes, times = zip(*relevant_data)
            plt.plot(
                sizes,
                times,
                marker="o" if reread else "x",
                label=f"{algorithm} ({'reread' if reread else 'no reread'})",
            )

    plt.xlabel("File Size")
    plt.ylabel("Execution Time (s)")
    plt.title(
        f"Execution Time vs. File Size for Different Algorithms ({'reread' if reread else 'no reread'})"
    )
    plt.legend()
    plt.grid(True)
    plt.savefig(f"benchmark_chart_{'reread' if reread else 'no_reread'}.png")
    plt.show()


if __name__ == "__main__":
    benchmark_results = parse_benchmark_results("benchmark_results.txt")
    plot_results(benchmark_results, reread=True)
    plot_results(benchmark_results, reread=False)
