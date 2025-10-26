# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install all dependencies directly
RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    uvicorn[standard]==0.32.0 \
    cachetools==5.5.0 \
    google-cloud-aiplatform==1.73.0 \
    google-generativeai==0.8.0 \
    pydantic==2.10.0 \
    pydantic-settings==2.6.0

# Copy local module source code
COPY deps/shared-contracts/src/shared_contracts ./shared_contracts
COPY deps/vector-query-client/src/vector_query_client ./vector_query_client

# Copy search-api source code
COPY src/search_api ./search_api

# Set Python path
ENV PYTHONPATH=/app

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Run the application
CMD ["python", "-m", "uvicorn", "search_api.api:app", "--host", "0.0.0.0", "--port", "8080"]
