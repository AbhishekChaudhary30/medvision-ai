FROM python:3.12-slim

# Create a non-root user (required by some HF Spaces policies)
RUN useradd -m -u 1000 user

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/home/user
ENV PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user pyproject.toml README.md alembic.ini run.py ./
COPY --chown=user backend ./backend

# We also copy requirements.txt to ensure spaces is installed if needed
COPY --chown=user requirements.txt ./

USER user

# Install dependencies
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip install --no-cache-dir -e .

# Expose the HF Space default port
EXPOSE 7860

# Ensure migrations and start uvicorn via run.py
CMD ["sh", "-c", "alembic upgrade head && python run.py"]
