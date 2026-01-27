# Binder Environment Setup Instructions

This directory contains configuration files for [Binder](https://mybinder.org/), which allows students to launch a reproducible JupyterHub or RStudio environment for your course simply by clicking on the shared link.

> **NOTE**: Default files are currently **UNTESTED** for **R** which may require additional configuration steps.

## Customizing Your Binder Environment

**NOTE**: Course materials, including Jupyter notebooks and data stay within the course root directory (parent directory to this `/binder` folder).

### Binder Configuration Files

Zero or more of the following supporting files should be created in the course `/binder` directory as needed for your project

#### Required

- runtime.txt
  
#### Optional

- requirements.txt / pyproject.toml (Python)
- environment.yml (conda)
- install.R / DESCRIPTION (R)

### Python Configuration

- Create and add any required Python packages to `requirements.txt` or provide `pyproject.toml` file.
- Update the required Python version as needed in `runtime.txt`.  Default: `python-3.12`.

### R Configuration

- Update the required R version `runtime.txt`. R versioning is indicated as follows
  
  ```r-<version>-<YYY-MM_DD>```

  where the date indicates the snapshot at MRAN that will be used to install libraries.  Replace `<version>` with the R version you require (e.g., `4.3.1`).  **NOTE:** Default is `3.6` on the day the course folder was created.
- Add any required R packages to `install.R` or provide a `DESCRIPTION` file

### Conda Environments

- If your project requires complex dependencies or non-Python packages, you can specify an `environment.yml` file for [conda](https://docs.conda.io/en/latest/). Binder will use this file to create the environment. See the [Binder conda documentation](https://mybinder.readthedocs.io/en/latest/config_files.html#environment-yml-conda-environment) for details.

### More Information

Binder supports configuration files for package installation, environment specification, post-build shell scripts, and more.  For example, it is possible to set up complex configurations, such as running notebooks on Python 2.x and 3.x in the same binder by customization of the `runtime.txt`.  If absolutely necessary, you can also create a `Dockerfile` in the `/binder` directory to be deployed, but it must adhere to the requirements for custom containers outlined in the Binder documentation.

See the [Binder documentation](https://mybinder.readthedocs.io/en/latest/) for details.
