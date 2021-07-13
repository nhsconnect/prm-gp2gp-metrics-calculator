FROM python:3.9-slim

COPY . /prmcalculator

RUN cd /prmcalculator && python setup.py install

ENTRYPOINT ["python", "-m", "prmcalculator.pipeline.metrics_calculator.main"]
