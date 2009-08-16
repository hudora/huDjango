# setting the PATH seems only to work in GNUmake not in BSDmake
PATH := ./testenv/bin:$(PATH)

default: dependencies check test

hudson: dependencies test statistics coverage
	find hudjango -name '*.py' | xargs /usr/local/hudorakit/bin/hd_pep8
	/usr/local/hudorakit/bin/hd_pylint -f parseable hudjango
	# we can't use tee because it eats the error code from hd_pylint
	/usr/local/hudorakit/bin/hd_pylint -f parseable hudjango > pylint.out

check:
	-find hudjango -name '*.py' | xargs /usr/local/hudorakit/bin/hd_pep8
	-/usr/local/hudorakit/bin/hd_pylint hudjango

test: dependencies
	# PYTHONPATH=hudjango/tests/:. DJANGO_SETTINGS_MODULE=settings_tests python hudjango/testall.py
	PYTHONPATH=hudjango/tests/:. DJANGO_SETTINGS_MODULE=settings_tests python hudjango/tests/runtests.py --verbosity=2

dependencies:
	virtualenv testenv
	pip -q install -E testenv -r requirements.txt

statistics:
	sloccount --wide --details hudjango > sloccount.sc

coverage: dependencies
	rm .figleaf
	PYTHONPATH=hudjango/tests/:. DJANGO_SETTINGS_MODULE=settings_tests python /usr/local/hudorakit/bin/hd_figleaf --ignore-pylibs hudjango/testall.py
	# runtests automatically generates a cveraage dump
	PYTHONPATH=hudjango/tests/:. DJANGO_SETTINGS_MODULE=settings_tests hudjango/tests/runtests.py
	echo "testenv/.*" > figleaf-exclude.txt
	echo "/opt/.*" >> figleaf-exclude.txt
	echo "/usr/local/lib/.*" >> figleaf-exclude.txt
	# fix pathnames
	perl -npe "s|`pwd`/||g;" -i.bak .figleaf
	python /usr/local/hudorakit/bin/hd_figleaf2html -d ./coverage -x figleaf-exclude.txt
	echo "Coverage: " `grep -A3 ">totals:<" coverage/index.html|tail -n1|cut -c 9-13|cut -d'<' -f1`
	# Error if coverage < 60 %
	test `grep -A3 ">totals:<" coverage/index.html|tail -n1|cut -c 9-13|cut -d'.' -f1` -gt 60

build:
	python setup.py build sdist bdist_egg
	rsync -rvapP dist/* root@cybernetics.hudora.biz:/usr/local/www/data/nonpublic/eggs/

upload: build
	rsync dist/* root@cybernetics.hudora.biz:/usr/local/www/apache22/data/nonpublic/eggs/
	rsync dist/* root@cybernetics.hudora.biz:/usr/local/www/apache22/data/dist/huDjango/

install: build
	sudo python setup.py install

runserver: dependencies
	python manage.py syncdb
	python manage.py runserver

clean:
	rm -Rf testenv generic_templates build dist html test.db sloccount.sc pylint.out pip-log.txt
	rm -Rf huDjango.egg-info figleaf-exclude.txt interesting-files.txt .figleaf coverage
	find . -name '*.pyc' -or -name '*.pyo' -or -name 'svn-commit*tmp' -delete

.PHONY: test build clean install upload check deploy
