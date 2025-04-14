# Use Python Alpine as base image
FROM python:alpine

# Install system dependencies
RUN apk add --no-cache \
    build-base \
    curl \
    gcc \
    make \
    musl-dev \
    linux-headers \
    && curl https://sh.rustup.rs -sSf | sh -s -- -y

# Add Rust to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the ports for langgraph server and gradio client
EXPOSE 7860

# Command to run the client application
CMD ["python", "client_chat.py"]