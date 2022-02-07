FROM python:3.9

WORKDIR app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/** .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
