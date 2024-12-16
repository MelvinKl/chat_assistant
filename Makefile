COMPONENTS_DIR := components

format:
	cd assistant;isort .; black .; cd ..;
	@for f in $(shell ls ${COMPONENTS_DIR}); do set -e; cd ${COMPONENTS_DIR}/$${f};isort .; black .; cd ../..; done