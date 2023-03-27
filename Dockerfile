FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY compare_tool.py .

ENTRYPOINT ["python", "compare_tool.py"]
