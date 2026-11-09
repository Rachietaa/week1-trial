# The scoring service's image.
#   build:  docker build -t credit-risk-api .
#   run:    docker run -p 8080:8080 -v "$PWD/models:/app/models" credit-risk-api
#
# PROVIDED: a slim base image. Use the SAME Python minor version as the laptop that exported
# the model (the second line of requirements-api.txt says which), so the saved model loads.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080
WORKDIR /app

# The pinned requirements, before the code: Docker reuses this slow layer when only code changes.
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# PROVIDED: only the service's code goes into the image. No data, no model (the service
# downloads it from your bucket when it starts), no tests, no notebooks.
COPY api/ api/

# A user without root rights: a break-in does not control the whole container.
RUN useradd --create-home appuser
USER appuser

# Start the service on every network interface, on the port Cloud Run gives us.
CMD ["sh", "-c", "exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
