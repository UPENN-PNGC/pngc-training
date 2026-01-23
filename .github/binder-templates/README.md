# Binder Environment Setup Instructions

This directory contains configuration files for [Binder](https://mybinder.org/), which allows students to launch a reproducible Jupyter environment for your course.

## Customizing Your Binder Environment

**NOTE**: Course materials, including Jupyter notebooks and data stay within the course root directory (parent directory to this `/binder` folder).

1. **Software Version**
   - The `runtime.txt` file specifies the Python (or R) version for Binder. Change `3.12` (`4.3.1`) to another version if needed (e.g., `3.11`).
   - The Dockerfile also sets the Python version in the `FROM python:3.12-slim` line. If you change the Python version, update both `runtime.txt` and the Dockerfile `FROM` line to match.  Similarly, you will need to change the version of the `rocker/binder` source image in the Dockerfile for R.

2. **Python Requirements**
   - Add any required Python (R) packages to `requirements.txt`, one per line. Leave it empty if you do not need extra packages.

3. **Custom Dockerfile**
   - The `Dockerfile` is used for advanced customization. By default, it installs Jupyter and Python 3.12 (or R 4.3.1).
   - To add system-level packages (e.g., samtools, htslib), add lines like:

     ```dockerfile
     RUN apt-get update && apt-get install -y samtools libhts-dev && rm -rf /var/lib/apt/lists/*
     ```

4. **More Information**
   - See the [Binder documentation](https://mybinder.readthedocs.io/en/latest/) for more options and examples.
