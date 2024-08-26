# Отдельный сборочный образ, чтобы уменьшить финальный размер образа
FROM python:3.11 as compile-image
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Окончательный образ
FROM python:3.11
COPY --from=compile-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /windi_api

COPY . .


EXPOSE 80

ENTRYPOINT ["python3", "main.py"]
#ENTRYPOINT ["ls"]
