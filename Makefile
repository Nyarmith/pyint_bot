.PHONY: default build run shell remove inspect status stop rm

include makefile.config

default: build

build:
	docker build --force-rm=true --tag=$(img-name):$(tag) $(ARGS) .

run:
	docker run \
	--name=$(name) \
	$(runargs) \
	$(img-name):$(tag) \
	$(ARGS)


shell:
	docker exec --interactive=true --tty=true $(name) /bin/bash $(ARGS)

inspect:
	docker inspect $(ARGS) $(name)

status:
	docker ps $(ARGS) --all=true --filter=name=$(name)

stop:
	docker stop $(ARGS) $(name)

rm:
	docker rm -f --volumes=true $(ARGS) $(name)
