# Painless scripting

## Overview

Examples and tests for the painless scripting language built into ElasticSearch

## Getting started

### Run ElasticSearch

Start single instance in docker

```
docker run -d --name es -p 9200:9200 -p 9300:9300 elasticsearch:7.13.1
```


### Create Test Data

```
python3 inject-test-data.py 2015-05-07T15:00:26.012 2021-05-07T15:00:26.123 10
```



## Notes

### Pushing a single documents into ElasticSearch

```
curl -X POST http://localhost:9200/backups/backup -H "Content-Type: application/json" -d '
{
  "occurence": "hourly",
  "replicas": [
    "us-west-2",
    "ap-southeast-1",
    "eu-west-1"
  ],
  "timestamp": "2017-02-23 19:54:31.012000",
  "cloud": {
    "availability_zone": "eu-north-1",
    "resident": "persistent"
  }
}
'
```


### Querying the data

Get a count of backup entries

```
curl http://localhost:9200/backups/backup/_count
```

Give the following output 

```
{"count":11010,"_shards":{"total":1,"successful":1,"skipped":0,"failed":0}}
```


### Sorting data

```
curl http://localhost:9200/backups/backup/_search -H "Content-Type: application/json" -d '
{
  "query": {
    "match_all": {}
  },
  "sort": {
    "_script": {
        "type": "string",
        "order": "asc",
        "script": {
          "lang": "painless",
          "source": "doc['timestamp'].value"
        } 
    }
  }
}'
```

TODO: THe above doesn't work



## References

### ElasticSearch

* [Painless walkthrough](https://www.elastic.co/guide/en/elasticsearch/painless/7.13/painless-walkthrough.html#painless-walkthrough)
* [ElasticSearch docker image](https://hub.docker.com/_/elasticsearch)
* [Multi-target syntax](https://www.elastic.co/guide/en/elasticsearch/reference/current/multi-index.html)

### Python

* [What '__name__ == ...' does](https://stackoverflow.com/questions/419163/what-does-if-name-main-do)
* [Datetime iso parsing](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)
* [Converting between types](https://www.digitalocean.com/community/tutorials/how-to-convert-data-types-in-python-3)
* [Random library](https://docs.python.org/3/library/random.html)
* [HTTP Client](https://docs.python.org/3/library/http.client.html)
* 



