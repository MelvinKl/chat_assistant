COMPONENTS_DIR := components

format:
	@for f in $(shell ls ${COMPONENTS_DIR}); do set -e; cd ${COMPONENTS_DIR}/$${f};isort .; black .; cd ../..; done