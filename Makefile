#!/usr/bin/make
PYTHON := /usr/bin/env python
ES_VERSION ?= 0.90.7
ES_SHA256 ?= a3ec3c05ffabf8048642aa431b675f3c132b4fae755e1b7aee0cb9fe3f2a37ba
ES_DOWNLOAD_URL ?=https://download.elasticsearch.org/elasticsearch/elasticsearch/

build: sync-charm-helpers test

charm-payload: files/elasticsearch-${ES_VERSION}.deb files/elasticsearch-${ES_VERSION}.deb.sha1.txt sync-charm-helpers
	@cd files && sha1sum elasticsearch-${ES_VERSION}.deb.sha1.txt --check --quiet

lint:
	@flake8 --exclude hooks/charmhelpers --ignore=E125 hooks
	@flake8 --exclude hooks/charmhelpers --ignore=E125 unit_tests
	@charm proof

test:
	@echo Starting unit tests...
	@PYTHONPATH=./hooks $(PYTHON) /usr/bin/nosetests3 --nologcapture unit_tests

bin/charm_helpers_sync.py:
	@bzr cat lp:charm-helpers/tools/charm_helpers_sync/charm_helpers_sync.py \
		> bin/charm_helpers_sync.py

sync-charm-helpers: bin/charm_helpers_sync.py
	@$(PYTHON) bin/charm_helpers_sync.py -c charm-helpers.yaml

deploy:
	@echo Deploying local elasticsearch charm
	@juju deploy --repository=../.. local:elasticsearch

files/elasticsearch-${ES_VERSION}.deb:
	@cd files && wget ${ES_DOWNLOAD_URL}/elasticsearch-${ES_VERSION}.deb

files/elasticsearch-${ES_VERSION}.deb.sha1.txt:
	@cd files && wget ${ES_DOWNLOAD_URL}/elasticsearch-${ES_VERSION}.deb.sha1.txt
