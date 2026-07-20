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
  "https://ckan.data.example.fr",  # the address of your platform
  apikey="SUP3R_S3CR3T",  # your API key (optional, only if you want to modify objects on the platform)
)
```

2. Instanciate objects from their ids (or names, though less recommended)

This project currently implements three main objects: `Package`, `Resource` and `Organization`
```python
pack = ckanc.package("my_dataset_name")  # this creates an instance of Package
res = ckanc.resource("e7a249c8-cfc9-4608-b5d2-ef0541255ba9")  # this creates an instance of Resource
org = ckanc.organization("my_org_name")  # this creates an instance of Organization
```

Then you can access each object's properties:
```python
print(f"The package {pack.title} is attached to {pack.organization['title']}")
print(f"The resource {res.name} was created at {res.created} and contains {res.format} data")
print(f"The organization {org.title} has {len(org.packages)} packages")
```

These objects are accessible from one another:
- a `Package` has the attributes `resources` (list of `Resource`) and `organization`
- a `Resource` has the attribute `package`
- an `Organization` has the attributes `packages` (list of `Package`)

3. Modify objects

If you have filled in your API key in the client, you have the posibility to modify objects (depending on your rights on the platform).

From the client, it is possible to create all available objects:
```python
org = ckanc.create_organization({"name": "my-orga"})  # this creates an instance of Organization
pack = ckanc.create_package({"name": "new-dataset", "owner_org": "my-orga"})  # this creates an instance of Package
res = ckanc.create_resource({"name": "first-resource", "package_id": "new-dataset", "upload": open("file.csv", "rb")})  # this creates an instance of Resource
```
It is also possible to create objects from their "parent":
```python
org = ckanc.create_organization({"name": "my-orga"})
pack = org.create_package({"name": "new-dataset"})  # the package is attached to the organization, owner_org is not needed
res = pack.create_resource({"name": "first-resource", "upload": open("file.csv", "rb")})  #  the resource is attached to the package, package_id is not needed
```

All objects have the `patch` and `delete` methods:

```python
# the patch method allows to modify as many fields of the object as needed, without touching the ones that are not mentionned
pack.patch({"description": "More detailed description", "notes": "Additional insights"})
# the package is updated on the platform, and the pack variable also has the new fields value

# the delete method takes no argument, it deletes the object on the platform
res.delete()
```

## ⚡ Advanced features

Upon client creation, additional arguments can be passed:
- `user_agent`: to set a custom user-agent (defaults to a version specific user-agent)
- `verbose`: whether to display logs when methods are called (defaults to `True`)
- `fetch`: whether to retrieve the objects' metadata on instanciation. Set to `False` to prevent API calls if you only aim at modifiying object (defaults to `True`)
