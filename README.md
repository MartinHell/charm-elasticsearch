# Getting started with ElasticSearch

To deploy ElasticSearch locally:

    juju bootstrap
    juju deploy --repository=../.. local:elasticsearch

You can add more units and they will discover each other and
join the cluster.


## Relating to the Elasticsearch cluster

This charm currently provides the website http interface to the
consuming service, ie. the private address of an elasticsearch unit. The
consuming service can use this on the website-relation-joined
relation to query the cluster for the list of nodes (many client
elasticsearch apis will do this for you [1]).

If it's needed, we can add an elasticsearch cluster interface that
returns the lists of hosts in the cluster.

[1] http://elasticsearch-py.readthedocs.org/en/latest/api.html#elasticsearch


## Discovery

This charm uses unicast discovery which utilises the orchestration
of juju so that the discovery method is the same whether you deploy
on EC2, lxc or any other cloud provider.

When a new unit first joins the cluster, it will update its config
with the other units in the cluster (via the peer-relation-joined
hook), after which ElasticSearch handles the rest.


## Testing the ElasticSearch charm

Run the unit-tests with `make test`.

Run the functional tests with `juju test`.


## Downloading ElasticSearch

By default, the charm will download (and check) the elasticsearch
debian package during the install hook but this is not ideal in
production environments (you don't want the deploy to fail because a
third-party site is down). For this reason, the charm provides two other
methods for installing elasticsearch:

First, you can ensure the versioned deb package as available at
files/elasticsearch-0.90.7.deb as part of your build step, and it will not need
to be downloaded during install. To make that easier, you can download the
default version into

    make pre-download-deb

The other alternative is to ensure a relevant debian package is available
in an archive that you've configured via the execd_preinstall in the install
hook, and set the archive-package-name config option. This will ensure that
no download is required either during a build phase or the install hook,
other than from your archive.
