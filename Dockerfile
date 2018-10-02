FROM python:3
MAINTAINER https://github.com/JacobCallahan

RUN mkdir clix
COPY / /clix/
WORKDIR /clix

RUN python3 setup.py install

ENTRYPOINT ["clix"]
CMD ["--help"]
