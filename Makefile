check: clean
	find hudjango -name '*.py'  -exec pep8 --ignore=E501,W291 --repeat {} \;
	pylint hudjango

build:
	python setup.py build

upload:
	python setup.py build sdist bdist_egg
	rsync dist/* root@cybernetics.hudora.biz:/usr/local/www/apache22/data/dist/huDjango/

publish:
	# remove development tag
	perl -npe 's/^tag_build = .dev/# tag_build = .dev/' -i setup.cfg
	svn commit -m "publishing `grep version= setup.py` to http://pypi.python.org/pypi/"
	python setup.py build sdist bdist_egg upload
	# add development tag
	#perl -npe 's/^\# tag_build = .dev/tag_build = .dev/' -i setup.cfg
	rsync dist/* root@cybernetics.hudora.biz:/usr/local/www/apache22/data/dist/huDjango/
	echo "now bump version number in setup.py, commit"
	echo " and update https://cybernetics.hudora.biz/projects/wiki/huDjango"

install: build
	sudo python setup.py install

clean:
	rm -Rf build dist html test.db
	find . -name '*.pyc' -or -name '*.pyo' -delete

.PHONY: test build clean install upload check
