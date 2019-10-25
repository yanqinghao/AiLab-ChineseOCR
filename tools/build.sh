docker build -t registry-vpc.cn-shanghai.aliyuncs.com/shuzhi/ocr-docker-gpu:$1 -f docker/docker_ocr_gpu/Dockerfile .
docker build -t registry-vpc.cn-shanghai.aliyuncs.com/shuzhi/ocr-docker:$1 -f docker/docker_ocr/Dockerfile .

docker push registry-vpc.cn-shanghai.aliyuncs.com/shuzhi/ocr-docker:$1
docker push registry-vpc.cn-shanghai.aliyuncs.com/shuzhi/ocr-docker-gpu:$1