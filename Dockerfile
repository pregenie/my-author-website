# Use an official Python image.
FROM python:3.10-slim

# Prevent Python from buffering stdout/stderr.
ENV PYTHONUNBUFFERED=1

# Set the working directory.
WORKDIR /app

# Copy and install dependencies.
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code.
COPY backend/ /app/
COPY frontend/ /app/frontend/

# Copy the entrypoint script.
COPY backend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose the Flask application port.
EXPOSE 5000

# Use the entrypoint script to start the container.
CMD ["./entrypoint.sh"]


