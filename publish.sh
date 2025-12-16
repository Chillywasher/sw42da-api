source .env.publish

docker buildx build \
--platform linux/amd64,linux/arm64 \
--output type=docker \
--build-arg CONTAINER_PORT="$CONTAINER_PORT" \
--tag 192.168.67.10:30095/"$APP_NAME":"$TAG" \
--file Dockerfile ../../python

docker push 192.168.67.10:30095/"$APP_NAME":"$TAG"

