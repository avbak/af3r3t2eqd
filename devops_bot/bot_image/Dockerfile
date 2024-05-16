FROM python:3.9-slim-bookworm

RUN mkdir ./telegram
COPY bot.py requirements.txt ./telegram/
WORKDIR ./telegram
RUN pip3 install --no-cache-dir -r requirements.txt
CMD ["python3", "bot.py"]
