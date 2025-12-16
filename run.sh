source .env.run

docker buildx build \
--platform linux/amd64,linux/arm64 \
--build-arg CONTAINER_PORT="$CONTAINER_PORT" \
--output type=docker \
--tag "$APP_NAME":"$TAG" \
--file Dockerfile \
../../python

docker stop "$APP_NAME"
docker rm "$APP_NAME"

docker run \
--name "$APP_NAME" \
--network homeapps \
--publish "$HOST_PORT":"$CONTAINER_PORT" \
--restart "$RESTART_POLICY" \
--volume ~/Code/python/"$APP_NAME"/.env.docker:/.env \
"$APP_NAME":"$TAG"