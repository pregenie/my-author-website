# Use an official Python image.
FROM python:3.10-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container.
WORKDIR /app

# Copy and install dependencies.
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code.
COPY backend/ /app/

# Make sure the entrypoint script is executable.
RUN chmod +x entrypoint.sh

# Use the entrypoint script to start the container.
CMD ["./entrypoint.sh"]
