ARG PYTHON_VERSION=3.7

ARG NAME_SPACE

FROM registry-vpc.cn-shanghai.aliyuncs.com/${NAME_SPACE}/suanpan-python-sdk-cuda:${PYTHON_VERSION} as builder

ENV PYPI_MIRROR "https://mirrors.aliyun.com/pypi/simple"

RUN pip config set global.index-url ${PYPI_MIRROR}

RUN pip install --upgrade pip

RUN pip install --no-cache-dir pyarmor

WORKDIR /build

COPY . /build

RUN bash tools/compress.sh

FROM registry-vpc.cn-shanghai.aliyuncs.com/${NAME_SPACE}/suanpan-python-sdk-cuda:${PYTHON_VERSION}

WORKDIR /yanqing

ENV PYPI_MIRROR "https://mirrors.aliyun.com/pypi/simple"

RUN apt-get update && apt-get install poppler-utils -y && apt-get install tesseract-ocr -y

RUN pip config set global.index-url ${PYPI_MIRROR}

RUN pip install --upgrade pip

COPY --from=builder /build /yanqing

RUN pip install -r requirements_gpu.txt && mv /yanqing/tools/chi_sim.traineddata /usr/share/tesseract-ocr/4.00/tessdata/chi_sim.traineddata

ENTRYPOINT [ "/sbin/my_init", "--" ]

CMD [ "bash" ]
