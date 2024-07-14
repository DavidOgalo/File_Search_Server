# AS_IntroductoryTask

## Overview

The `AS_IntroductoryTask` is a project designed to implement and benchmark various file search algorithms to efficiently search for strings within large text files. This README provides a comprehensive guide to the project, including setup instructions, detailed descriptions of the implemented algorithms, how to run the benchmarks, and how to interpret the results.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Implemented Algorithms](#implemented-algorithms)
- [Running the Benchmarks](#running-the-benchmarks)
- [Analyzing the Results](#analyzing-the-results)
- [Limitations and Recommendations](#limitations-and-recommendations)
- [Future Enhancements](#future-enhancements)

## Project Structure

The project is organized into the following directories and files:


AS_IntroductoryTask/
│
├── README.md
├── requirements.txt
├── setup.sh
├── 200k.txt
├── server.key
├── server.csr
├── server.crt
├── server.py
├── client.py
├── config.ini
├── file-search_algorithms.py
├── benchmark_results.txt
├── test-suite_server.py
├── multiple-queries_simulation.py
├── speed_report.py
└── benchmark_chart.png


## Setup Instructions

### Prerequisites

Ensure you have the following installed on your machine:
- Python 3.7+
- pip (Python package installer)

### Installation

1. Setup project directory and the virtual environment

2. Install the required Python packages:

   pip install -r requirements.txt
   

## Implemented Algorithms

The following file search algorithms are implemented in this project:

1. **Naive Search**:
   - A straightforward approach that checks each position in the text for a match.

2. **Binary Search**:
   - Requires the data to be sorted; it divides the search interval in half repeatedly.

3. **Knuth-Morris-Pratt (KMP) Algorithm**:
   - Uses the preprocessing of the pattern to avoid unnecessary comparisons.

4. **Boyer-Moore Algorithm**:
   - Skips sections of the text, making it efficient for large alphabets and long patterns.

5. **Rabin-Karp Algorithm**:
   - Uses hashing to find any one of a set of pattern strings in a text.

6. **Z Algorithm**:
   - Computes the Z array which is used for pattern matching in linear time.

## Running the Benchmarks

### Benchmarking Search Algorithms

To benchmark the search algorithms, run the `file-search_algorithms.py` script:

python file-search_algorithms.py


This script will benchmark each algorithm on the generated test files and save the results to `benchmark_results.txt`.

### Generating the Speed Report

Once you have the benchmark results, generate the speed report by running the `speed_report.py` script:

python speed_report.py


This will create a visual representation of the benchmark results and save it as `benchmark_chart.png`.

## Analyzing the Results

The benchmark results are saved in `benchmark_results.txt` and can be visualized using the generated `benchmark_chart.png`. The results include:

- Execution time for each algorithm across different file sizes.
- Comparative performance analysis of all algorithms.


### Performance Analysis

From the generated chart, key observations include:
- **Naive Search** shows a linear increase in execution time with file size.
- **Binary Search** performs well for smaller datasets but requires sorted data.
- **KMP Algorithm** and **Boyer-Moore Algorithm** demonstrate efficient performance for large datasets.
- **Rabin-Karp Algorithm** is effective for multiple pattern searches but less efficient for very large datasets.
- **Z Algorithm** outperforms other algorithms with linear time complexity.

## Limitations and Recommendations

### Identified Limitations

1. **Memory Usage**: Higher memory consumption for certain algorithms (e.g., Rabin-Karp).
2. **Execution Time**: Inefficiency of Naive Search and Binary Search for large datasets.
3. **Scalability**: Performance degradation with high concurrency or extremely large datasets.

### Recommendations

1. **Use Z Algorithm for Large Datasets**: Implement the Z Algorithm for efficient performance.
2. **Optimize Memory Usage**: Optimize algorithms to reduce memory consumption.
3. **Enhance Scalability**: Implement load balancing and optimize server code for better scalability.
4. **Further Testing**: Conduct additional tests with diverse data and query patterns.

## Future Enhancements

1. **Advanced Query Options**: Support regex and fuzzy searching.
2. **Real-Time Analytics**: Monitor server performance and client query statistics in real-time.
3. **Scalability Improvements**: Explore distributed computing techniques.

## Conclusion

The `AS_IntroductoryTask` project provides an efficient solution for searching strings in large text files. By benchmarking various algorithms, we have identified the most suitable algorithm for different scenarios. The project offers a robust framework for further enhancements and optimizations.


This README provides a comprehensive guide to understanding, setting up, and running the `AS_IntroductoryTask` project, ensuring that users can effectively utilize and extend its capabilities.