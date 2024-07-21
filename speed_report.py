import matplotlib.pyplot as plt
from typing import Dict, List, Tuple

def parse_benchmark_results(file_path: str) -> Dict[str, List[Tuple[int, float]]]:
    """
    Parse benchmark results from a file.

    Args:
        file_path: Path to the benchmark results file.

    Returns:
        A dictionary where keys are algorithm names and values are lists of tuples (file_size, execution_time).
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Skip the header lines
    lines = lines[2:]

    results: Dict[str, List[Tuple[int, float]]] = {}

    for line in lines:
        parts = line.strip().split()
        if len(parts) == 3:
            algorithm = parts[0]
            size = int(parts[1])
            time = float(parts[2])

            if algorithm not in results:
                results[algorithm] = []
            results[algorithm].append((size, time))

    return results

def plot_results(results: Dict[str, List[Tuple[int, float]]]) -> None:
    """
    Plot the benchmark results.

    Args:
        results: A dictionary where keys are algorithm names and values are lists of tuples (file_size, execution_time).
    """
    plt.figure(figsize=(10, 6))

    for algorithm, data in results.items():
        data = sorted(data)  # Ensure data is sorted by file size
        sizes, times = zip(*data)
        plt.plot(sizes, times, marker='o', label=algorithm)

    plt.xlabel('File Size')
    plt.ylabel('Execution Time (s)')
    plt.title('Execution Time vs. File Size for Different Algorithms')
    plt.legend()
    plt.grid(True)
    plt.savefig('benchmark_chart.png')
    plt.show()

if __name__ == "__main__":
    benchmark_results = parse_benchmark_results('benchmark_results.txt')
    plot_results(benchmark_results)
