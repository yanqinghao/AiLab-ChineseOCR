NAMESPACE=("shuzhi-amd64")
for i in ${NAMESPACE[*]}
do
    docker build --build-arg NAME_SPACE=${i} -t registry-vpc.cn-shanghai.aliyuncs.com/${i}/ocr-docker-gpu:$1 -f docker/docker_ocr_gpu/Dockerfile .
    sed -i "s/cpu/cu100/g" .dockerignore
    docker build --build-arg NAME_SPACE=${i} -t registry-vpc.cn-shanghai.aliyuncs.com/${i}/ocr-docker:$1 -f docker/docker_ocr/Dockerfile .
    sed -i "s/cu100/cpu/g" .dockerignore

    docker push registry-vpc.cn-shanghai.aliyuncs.com/${i}/ocr-docker:$1
    docker push registry-vpc.cn-shanghai.aliyuncs.com/${i}/ocr-docker-gpu:$1
done