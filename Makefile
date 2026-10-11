.PHONY: env hooks lab check build

env:            ## create the conda env
	conda env create -f environment.yml || conda env update -f environment.yml --prune

hooks:          ## register nbstripout for this clone (run once per member)
	nbstripout --install

lab:
	jupyter lab notebooks/

check:          ## forbidden-library / greyscale / TODO checks only
	python scripts/build_submission.py --check

build:          ## merge + execute -> submission/P1_Transformations.ipynb
	python scripts/build_submission.py
