

all:
	@echo "This makefile just contains a clean target"


clean:
	rm -rf Schematics/*/*/*.svg
	rm -rf Schematics/*/*/*-backups
	find . -name __pycache__ -print | xargs rm -rf
	find . -name '_*' -print | xargs rm -rf
