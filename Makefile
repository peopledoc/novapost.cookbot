BUILDOUT_BOOTSTRAP_URL="http://svn.zope.org/*checkout*/zc.buildout/tags/1.5.2/bootstrap/bootstrap.py?content-type=text%2Fplain"
PROJECT_NAME="novapost.cookbot"

develop:
	@test -f lib/buildout/bootstrap.py || \
	    (mkdir -p lib/buildout \
	     && wget ${BUILDOUT_BOOTSTRAP_URL} -O lib/buildout/bootstrap.py \
	     && python lib/buildout/bootstrap.py --distribute)
	bin/buildout -N

uninstall:
	rm -r bin/ lib/

documentation:
	rm -f docs/api/generated/*
	bin/sphinx-autogen --output-dir=docs/api/generated/ --suffix=txt --templates=docs/_templates/ docs/api/index.txt
	bin/sphinx-autogen --output-dir=docs/api/generated/ --suffix=txt --templates=docs/_templates/ docs/api/generated/*.txt
	cd docs && make clean html

readme:
	mkdir -p docs/_build/html
	bin/rst2 html README.rst > docs/_build/html/README.html

tests:
	bin/nosetests -v --rednose --with-doctest --with-coverage --cover-erase --cover-package=${PROJECT_NAME}
	bin/lettuce
