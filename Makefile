# setting the PATH seems only to work in GNUmake not in BSDmake
PATH := ./testenv/bin:$(PATH)

default: dependencies check

hudson:  dependencies statistics
	find hudjango -name '*.py' | xargs /usr/local/hudorakit/bin/hd_pep8
	/usr/local/hudorakit/bin/hd_pylint -f parseable hudjango
	# we can't use tee because it eats the error code from hd_pylint
	/usr/local/hudorakit/bin/hd_pylint -f parseable hudjango > pylint.out

check:
	-find hudjango -name '*.py' | xargs /usr/local/hudorakit/bin/hd_pep8
	-/usr/local/hudorakit/bin/hd_pylint hudjango

# test:
# 	python manage.py test --verbosity=2 hudjango

dependencies:
	virtualenv testenv
	pip -q install -E testenv -r requirements.txt
	sh -c 'echo p | svn co https://cybernetics.hudora.biz/intern/svn/code/projects/html/trunk/templates generic_templates'

statistics:
	sloccount --wide --details hudjango > sloccount.sc

build:
	python setup.py build sdist bdist_egg
	rsync -rvapP dist/* root@cybernetics.hudora.biz:/usr/local/www/data/nonpublic/eggs/

upload: build
	rsync dist/* root@cybernetics.hudora.biz:/usr/local/www/apache22/data/nonpublic/eggs/
	rsync dist/* root@cybernetics.hudora.biz:/usr/local/www/apache22/data/dist/huDjango/

install: build
	sudo python setup.py install

runserver: deploy
	python manage.py runserver

clean:
	rm -Rf testenv generic_templates build dist html test.db sloccount.sc pylint.out pip-log.txt
	find . -name '*.pyc' -or -name '*.pyo' -delete

.PHONY: test build clean install upload check deploy
