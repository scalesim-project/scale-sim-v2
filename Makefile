venvdir := venv

all: clean create_venv
	@echo "Done"

create_venv: ${venvdir}

${venvdir}: requirements.txt
	# test -d ${venvdir} || python3.8 -m venv ${venvdir}
	test -d ${venvdir} || python3 -m venv ${venvdir}
	${venvdir}/bin/pip install  --upgrade pip
	${venvdir}/bin/pip install setuptools wheel
	${venvdir}/bin/pip install  -Ur requirements.txt
	touch ${venvdir}/bin/activate
	chmod +x ${venvdir}/bin/activate
	touch source_me.sh
	echo "source ${venvdir}/bin/activate" > source_me.sh

# Clean Python and Emacs backup and cache files
clean:
	find . -name '*.pyc' -delete
	find . -name '*.yaml' -delete
	find . -name '*~' -delete
	find . -name '__pycache__' -type d | xargs rm -rf
	find . -name '.ipynb_checkpoints' -type d | xargs rm -rf
	find . -name '${venvdir}' -type d | xargs rm -rf
	find . -name 'source_me.sh' -delete
	find . -name 'nosetest_results.txt' -delete
	rm -rf dist
	rm -rf build

