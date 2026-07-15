# **ckan-client**

A higher level overlay around [`ckanapi`](https://pypi.org/project/ckanapi/) to interact with a [CKAN platform](https://ckan.org/).

## 🛠️ Install
> 🚧 coming soon

```bash
pip install ckan-client
```

## 🚀 Use

1. Set up your client

```python
from ckan_client import CkanClient

ckanc = CkanClient(
  "https://ckan.data.example.fr",  # the base URL of your platform
  apikey="SUP3R_S3CR3T",  # your API key (optional, only if you want to modify objects on the platform)
)
```

2. Instanciate objects from their ids

This project currently implements two main objects: `Package` and `Resource`
```python
pack = ckanc.package("my_dataset_id")  # this creates an instance of Package
res = ckanc.resource("e7a249c8-cfc9-4608-b5d2-ef0541255ba9")  # this creates an instance of Resource
```

Then you can access each object's properties:
```python
print(f"The package {pack.title} is attached to {pack.organization['title']}")
print(f"The resource {res.name} was craated at {res.created} and contains {res.format} data")
```
