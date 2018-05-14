
#   Name

zktx

#   Status

This library is considered production ready.

#   Description

Transaction implementation on Zookeeper.

#   Classes

##  zktx.KVAccessor

**syntax**:
`zktx.KVAccessor()`

An abstract class that defines an underlaying storage access API.
An implementation of `KVAccessor` must provides with 4 API:

```python
def create(self, key, value):
def delete(self, key, version=None):
def set(self, key, value, version=None):
def get(self, key):
```

They are similar to zk APIs, except that `version` does not have to be a version
number. It could be any data type the implementation could understand.


##  zktx.ValueAccessor

Same as `KVAccessor` except the API it defines does not require the argument
`key`.
It is used to access a single node:

```python
def create(self, value):
def delete(self, version=None):
def set(self, value, version=None):
def get(self):
```


#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
