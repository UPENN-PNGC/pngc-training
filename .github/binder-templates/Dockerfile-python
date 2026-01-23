FROM python:3.12-slim

# Copy requirements.txt and install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Install Jupyter and any additional packages here
RUN pip install --no-cache-dir notebook jupyterlab

EXPOSE 8888

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser", "--allow-root"]
