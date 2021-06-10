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


### Creating Mapping for Index

```
curl -X PUT http://localhost:9200/backups -H "Content-Type: application/json" -d '{
  "mappings": {
  "properties": {
      "timestamp": {
        "type": "date",
        
        "format": "yyyy-MM-dd'"'"'T'"'"'HH:mm:ss.SSSSSS"
      }
    }
  }
}'
```


### Pushing a single documents into ElasticSearch

```
curl -X POST http://localhost:9200/backups/_doc -H "Content-Type: application/json" -d '
{
  "occurence": "hourly",
  "replicas": [
    "us-west-2",
    "ap-southeast-1",
    "eu-west-1"
  ],
  "timestamp": "2017-02-23T19:54:31.012000",
  "cloud": {
    "availability_zone": "eu-north-1",
    "resident": "persistent"
  }
}'
```


### Querying the data

Get a count of backup entries

```
curl http://localhost:9200/backups/_count
```

Give the following output 

```
{"count":11010,"_shards":{"total":1,"successful":1,"skipped":0,"failed":0}}
```


### Sorting data

```
curl http://localhost:9200/backups/_search -H "Content-Type: application/json" -d '
{
  "query": {
    "match_all": {}
  },
  "sort": {
    "_script": {
        "type": "number",
        "order": "asc",
        "script": {
          "lang": "painless",
          "source": "doc['"'"'timestamp'"'"'].value.getMillis()"
        }
    }
  }
}' | json_pp
```

TODO: THe above gives this error


### Default query

```
curl http://localhost:9200/backups/_search
```




## References

### ElasticSearch

* [Painless walkthrough](https://www.elastic.co/guide/en/elasticsearch/painless/7.13/painless-walkthrough.html#painless-walkthrough)
* [ElasticSearch docker image](https://hub.docker.com/_/elasticsearch)
* [Multi-target syntax](https://www.elastic.co/guide/en/elasticsearch/reference/current/multi-index.html)
* [Date format](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-date-format.html)


### Python

* [What '__name__ == ...' does](https://stackoverflow.com/questions/419163/what-does-if-name-main-do)
* [Datetime iso parsing](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)
* [Converting between types](https://www.digitalocean.com/community/tutorials/how-to-convert-data-types-in-python-3)
* [Random library](https://docs.python.org/3/library/random.html)
* [HTTP Client](https://docs.python.org/3/library/http.client.html)
* [Output ISO format date](https://www.tutorialspoint.com/How-do-I-get-an-ISO-8601-date-in-string-format-in-Python)
* [Removal of mapping types](https://www.elastic.co/guide/en/elasticsearch/reference/current/removal-of-types.html)
* [Sort contexyt](https://www.elastic.co/guide/en/elasticsearch/painless/current/painless-sort-context.html)


### Shell

* [Escaping single quotes in single quotes](https://stackoverflow.com/questions/1250079/how-to-escape-single-quotes-within-single-quoted-strings)




