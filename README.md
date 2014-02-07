# Getting started with ElasticSearch

To deploy ElasticSearch locally:

    juju bootstrap
    juju deploy --repository=../.. local:elasticsearch

Note: before this charm goes in the charm store, it'll
need to be renamed.

You can add more units and they will discover each other and
join the cluster.


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
debian package during install but you can also include the package at
files/elasticsearch-0.90.7.deb and it will not need to be downloaded during
install. To make that easier, you can download the default version into 

    make charm-payload

## TODO
 * Add other ElasticSearch config options as needed.
