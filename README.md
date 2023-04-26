# SpeakLeash Benchmark

SpeakLeash benchmark is a Python script that evaluates the average processing time using SpeakLeash post-processor. The script can be executed using the `main.py` file and supports several command-line arguments to customize its behavior.

## Installation

To install the required packages for the SpeakLeash benchmark script, you can use the following command:

```
python -m pip install -r requirements.txt
```

This command installs the packages listed in the `requirements.txt` file.

### Using Virtual Environments

It is highly recommended to use virtual environments when working with Python projects. Virtual environments allow you to manage dependencies for each project separately, ensuring that different projects do not interfere with each other.


## Usage

To run the SpeakLeash benchmark script, use the following command:

```
python main.py [arguments]
```

The script accepts the following command-line arguments:

### `--large`

- Use this argument to evaluate processing time of 64 large (>1MB) text documents derived from usenet dataset.
- This argument does not require a value.
- If this argument is omitted, the script will assume usage of 1024 small documents derived from news_4_business_corpus dataset
- Example usage: `python main.py --large`

### `--num_pass`

- Use this argument to specify number of iterations of processing the dataset.
- This argument requires an integer value.
- The default value is 1
- Example usage: `python main.py --num_pass 3`

### `--processes`

- Use this argument to specify the number of parallel processes used for calculating metrics.
- This argument requires an integer value representing the number of required processes to spawn.
- If this argument is omitted, the script will use the value returned by os.cpu_count()
- Please not: the total system memory in GB / expected processes number should exceed 5GB when used with --large parameter. Otherwise it may cause system to run  out of RAM while processing multiple large documents.
- Example usage: `python main.py --processes 8`

## Additional Information

For more information about the SpeakLeash benchmark script and its functionalities, please refer to the source code and comments within the `main.py` file.
