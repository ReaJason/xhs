## 多架构构建

> 参考：https://yeasy.gitbook.io/docker_practice/buildx/multi-arch-images


```bash
docker buildx create --name mybuilder --driver docker-container

docker buildx use mybuilder

docker buildx build --platform linux/arm64,linux/amd64 -t reajason/xhs-api . --push
```
