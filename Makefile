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
	./testenv/bin/python ./hudjango/templatetags/hudjango.py
	PYTHONPATH=.:./tests DJANGO_SETTINGS_MODULE=settings_tests python testall.py
	PYTHONPATH=tests/:. DJANGO_SETTINGS_MODULE=settings_tests python tests/runtests.py --verbosity=1

dependencies:
	virtualenv testenv
	pip -q install -E testenv -r requirements.txt

statistics:
	sloccount --wide --details hudjango > sloccount.sc

coverage: dependencies
	rm -Rf .figleaf*
	PYTHONPATH=.:./tests DJANGO_SETTINGS_MODULE=settings_tests python /usr/local/hudorakit/bin/hd_figleaf --ignore-pylibs testall.py
	# runtests automatically generates a cveraage dump
	PYTHONPATH=tests/:. DJANGO_SETTINGS_MODULE=settings_tests tests/runtests.py
	printf 'tests/.*\n.*test.py\n' > figleaf-exclude.txt
	printf '/usr/local/lib/.*\n/opt/.*\ntestenv/.*\n' >> figleaf-exclude.txt
	printf '.*manage.py\n.*settings.py\n.*setup.py\n.*urls.py\n' >> figleaf-exclude.txt
	# fix pathnames
	perl -npe "s|`pwd`/||g;" -i.bak .figleaf
	python /usr/local/hudorakit/bin/hd_figleaf2html -d ./coverage -x figleaf-exclude.txt
	echo "Coverage: " `grep -A3 ">totals:<" coverage/index.html|tail -n1|cut -c 9-13|cut -d'<' -f1`
	# Error if coverage < 60 %
	test `grep -A3 ">totals:<" coverage/index.html|tail -n1|cut -c 9-13|cut -d'.' -f1` -gt 70

build:
	python setup.py sdist

upload: build
	python setup.py sdist upload

install: build
	sudo python setup.py install

runserver: dependencies
	python manage.py syncdb
	python manage.py runserver

clean:
	rm -Rf testenv generic_templates build dist html test.db sloccount.sc pylint.out pip-log.txt
	rm -Rf huDjango.egg-info figleaf-exclude.txt interesting-files.txt .figleaf* coverage
	find . -name '*.pyc' -or -name '*.pyo' -or -name 'svn-commit*tmp' | xargs rm

.PHONY: test build clean install upload check deploy
