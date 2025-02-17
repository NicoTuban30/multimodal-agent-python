FROM python:3.13

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and switch to it
RUN useradd -m -d /home/appuser -s /bin/bash appuser

# Ensure the app directory is owned by the non-root user
RUN mkdir -p /app && chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Copy and install Python dependencies
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY --chown=appuser:appuser . .

# Expose the application port
EXPOSE 8000

# Set the default command
CMD ["python", "agent.py", "start"]
