FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt


#--------
FROM python:3.12-slim
RUN useradd -m student
WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

USER student

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
