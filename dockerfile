FROM python:3.11-slim



WORKDIR /app



COPY scanner.py .

COPY targets.txt .



RUN pip install requests



ENTRYPOINT ["python"]

CMD ["scanner.py"]
