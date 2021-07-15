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

Ensure that the mapping is created first for dates

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

Then populate the index with a chunk of data

```
python3 inject-test-data.py 2010-01-07T09:00:26.012 2021-07-15T14:00:26.123 90 jade > 01_jade.log &
python3 inject-test-data.py 2010-01-07T09:00:26.012 2021-07-15T14:00:26.123 61 igorina > 02_igorina.log &
python3 inject-test-data.py 2010-01-07T09:00:26.012 2021-07-15T14:00:26.123 45 alice > 03_alice.log &
python3 inject-test-data.py 2010-01-07T09:00:26.012 2021-07-15T14:00:26.123 60 maladicta > 04_maladicta.log &
python3 inject-test-data.py 2010-01-07T09:00:26.012 2021-07-15T14:00:26.123 55 magda > 05_magda.log &
python3 inject-test-data.py 2010-01-07T09:00:26.012 2021-07-15T14:00:26.123 85 tilda > 06_magda.log &
python3 inject-test-data.py 2010-01-07T09:00:26.012 2021-07-15T14:00:26.123 60 polly > 07_polly.log &
```

This will take several minutes to complete

Check number of documents using the following

```
curl http://localhost:9200/backups/_count
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
      },
      "millis": {
        "type": "long"
      }
    }
  }
}'
```

Check the mapping for the index using this curl

``` 
curl http://localhost:9200/backups/_mapping | json_pp
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


### Default query

```
curl http://localhost:9200/backups/_search
```


### Sorting data

```
curl http://localhost:9200/backups/_search -H "Content-Type: application/json" -d '
{
  "size": 100,
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
}' | json_pp | less
```

The above will sort the data according to the timestamp millis


### Output just the time in millis

```
curl http://localhost:9200/backups/_search -H "Content-Type: application/json" -d '
{
  "size": 10,
  "query": {
    "match_all": {}
  },
  "script_fields": {
    "time_in_millis": {
        "script": {
            "lang": "painless",
            "source": "doc['"'"'timestamp'"'"'].value.getMillis()"
        }
    }
  },
  "sort": {
    "timestamp": {
        "order": "desc"
    }
  }
}' | json_pp | less
```

It seems that the timestamp is being stored using millis anyway as the above gives identical output for the 
sort value and `time_in_millis`.


### Aggregation Script


```
curl -X GET "http://localhost:9200/backups/_search" -H "Content-Type: application/json" -d '
{
  "size": 20,
  "query": {
    "range": {
      "timestamp": {
        "gte": "2021-05-07T09:00:26.012000",
        "lt": "2021-05-07T21:30:26.012000"
      }
    }
  },
  "aggs": {
    "average_gap": {
      "scripted_metric": {
        "init_script": "state.timestamps = new java.util.TreeSet()",
        "map_script": "state.timestamps.add(doc.timestamp.value.getMillis())",
        "combine_script": "List result = state.timestamps.stream().sorted().collect(java.util.stream.Collectors.toList()); return result",
        "reduce_script": "double previous = 0 ; List timestamps = states[0] ; int count = 0; double total = 0; for(timestamp in timestamps) { if (previous == 0) { previous = timestamp} else { total += (timestamp - previous); previous = timestamp ; count++ } } return total/count"
      }
    }
  }
}' | json_pp
```

The above script appears to work.  Based on a sample of the test data it approximates to a value of 
3600000 milliseconds, aka, 1hr.

### Aggregation Script Simplfied

```
curl -X GET "http://localhost:9200/backups/_search" -H "Content-Type: application/json" -d '
{
  "size": 0
  "query": {
    "range": {
      "timestamp": {
        "gte": "2021-05-07T09:00:26.012000",
        "lt": "2021-05-07T21:30:26.012000"
      }
    }
  },
  "aggs": {
    "average_gap": {
      "scripted_metric": {
        "init_script": "state.timestamps = new ArrayList()",
        "map_script": "state.timestamps.add(doc.timestamp.value.getMillis())",
        "combine_script": "List gaps = new ArrayList(); long previous = 0; for (timestamp in state.timestamps) { if(previous == 0) { previous = timestamp } else { gaps.add(timestamp - previous) ; previous = timestamp  } } return gaps",
        "reduce_script": "int count = 0; double total = 0; for(timestamp in states[0]) { total += timestamp ; count++ } return total/count"
      }
    }
  }
}' | json_pp
```







## Important points

In case of lots of scripting need to keep an eye on the [caches](https://www.elastic.co/guide/en/elasticsearch/reference/7.13/scripts-and-search-speed.html) and relevant settings. 


## References

### ElasticSearch

* [Painless walkthrough](https://www.elastic.co/guide/en/elasticsearch/painless/7.13/painless-walkthrough.html#painless-walkthrough)
* [ElasticSearch docker image](https://hub.docker.com/_/elasticsearch)
* [Multi-target syntax](https://www.elastic.co/guide/en/elasticsearch/reference/current/multi-index.html)
* [Date format](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-date-format.html)
* [Metric aggregation map context](https://www.elastic.co/guide/en/elasticsearch/painless/current/painless-metric-agg-map-context.html)
* [Script caching and search speed](https://www.elastic.co/guide/en/elasticsearch/reference/7.13/scripts-and-search-speed.html)
* [Scritped metric aggregation](https://www.elastic.co/guide/en/elasticsearch/reference/7.13/search-aggregations-metrics-scripted-metric-aggregation.html)
* [Deleting index](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-delete.html)
* [Numeric types](https://www.elastic.co/guide/en/elasticsearch/reference/current/number.html)
* [Aggregations](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations.html)


### Python

* [What '__name__ == ...' does](https://stackoverflow.com/questions/419163/what-does-if-name-main-do)
* [Datetime iso parsing](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat)
* [Converting between types](https://www.digitalocean.com/community/tutorials/how-to-convert-data-types-in-python-3)
* [Random library](https://docs.python.org/3/library/random.html)
* [HTTP Client](https://docs.python.org/3/library/http.client.html)
* [Output ISO format date](https://www.tutorialspoint.com/How-do-I-get-an-ISO-8601-date-in-string-format-in-Python)
* [Removal of mapping types](https://www.elastic.co/guide/en/elasticsearch/reference/current/removal-of-types.html)
* [Sort contexyt](https://www.elastic.co/guide/en/elasticsearch/painless/current/painless-sort-context.html)
* [Date time object](https://javadoc.io/static/org.elasticsearch/elasticsearch/7.5.0/org/elasticsearch/script/JodaCompatibleZonedDateTime.html)
* [Numbers in python](https://www.tutorialspoint.com/python3/python_numbers.htm)


### Java

* [Date time formatter](https://docs.oracle.com/javase/8/docs/api/java/time/format/DateTimeFormatter.html)


### Shell

* [Escaping single quotes in single quotes](https://stackoverflow.com/questions/1250079/how-to-escape-single-quotes-within-single-quoted-strings)




