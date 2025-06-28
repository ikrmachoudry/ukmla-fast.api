# 📦 Use official Python image
FROM python:3.10-slim

# 🏠 Set working directory
WORKDIR /app

# 📁 Copy all project files
COPY . .

# 🐍 Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 🌍 Expose FastAPI port
EXPOSE 8000

# 🚀 Default command to run FastAPI
CMD ["uvicorn", "main_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
