version=0.1

IMG_NAME=myflask
CONTAINER_NAME=flask-tut

build:
	docker image build -t ${IMG_NAME}:${version} --build-arg VERSION=${version} .

test: build
	docker run --rm --name ${CONTAINER_NAME} ${IMG_NAME}:${version}

run: build
	docker run -d -it -p 80:80 \
		--name ${CONTAINER_NAME} \
		--mount type=bind,src=`pwd`/../app,dst=/app \
		${IMG_NAME}:${version} /bin/bash

stop:
	docker stop ${CONTAINER_NAME}

bash:
	docker exec -it ${CONTAINER_NAME} /bin/bash

clean:
	docker rm -f ${CONTAINER_NAME}
	docker image rm ${IMG_NAME}:${version}
