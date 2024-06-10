

[PEP 8 Followed](https://code.visualstudio.com/docs/python/linting)

# Prerequisites
* Python 3.10
* Postgresql 16


# Django Commands

<details>
    <summary><h3>djanog Commands</h3></summary>


### Create Project
```
djnaog-admin startproject recipe_radar
```

### Create APP
Create the nreccessary folders
```
mkdir -p app/recipe_finder
```
Create the `__init__.py` file
```
touch app/__init__.py
```
```
django-admin startapp recipe_finder app/recipe_finder
```
</details>


<details>
    <summary><h3>.env<h3></summary>

```
SECRET_KEY="django-insecure-_r_vy22q!ce%@0l^8lr5oc+nyjmifs6_p_s$*v-l7_$)1p(rfa"

DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=recipe_radar
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432
```
</details>


<details>
    <summary><h3>API Filter Guide</h3></summary>


To apply filters using the `ListRequestRecipeSerializer` in your Django REST framework API, you need to send a JSON body in your request that follows the structure defined by your serializer. Here's how you can format the JSON body to apply filters:

### JSON Format for Filters

Assuming your `ListRequestRecipeSerializer` looks something like this:

```python
class ListRequestRecipeSerializer(serializers.Serializer):
    filters = serializers.DictField(child=serializers.CharField(), required=False)
```

You would send the filters in the JSON body like this:

```json
{
  "filters": {
    "category": "Desserts",
    "cooking_time__lte": 30,
    "title__icontains": "chocolate"
  }
}
```

### Explanation

- **"filters"**: The key for the dictionary containing your filters.
  - **"category"**: Filter by the category of the recipe. Replace "Desserts" with the desired category.
  - **"cooking_time__lte"**: Filter recipes with a cooking time less than or equal to 30 minutes. The `__lte` suffix stands for "less than or equal to".
  - **"title__icontains"**: Filter recipes where the title contains the word "chocolate". The `__icontains` suffix stands for "case-insensitive contains".

### Supported Filters

You can use any valid Django field lookup in your filters. Here are some common lookups:

- **Exact Match**: `"field_name": "value"`
- **Case-Insensitive Exact Match**: `"field_name__iexact": "value"`
- **Contains**: `"field_name__contains": "value"`
- **Case-Insensitive Contains**: `"field_name__icontains": "value"`
- **Greater Than**: `"field_name__gt": value`
- **Greater Than or Equal To**: `"field_name__gte": value`
- **Less Than**: `"field_name__lt": value`
- **Less Than or Equal To**: `"field_name__lte": value`
- **In a List**: `"field_name__in": ["value1", "value2"]`

### Example Requests

#### Example 1: Filter by Category
```json
{
  "filters": {
    "category": "Desserts"
  }
}
```

#### Example 2: Filter by Cooking Time Less Than or Equal to 30 Minutes
```json
{
  "filters": {
    "cooking_time__lte": 30
  }
}
```

#### Example 3: Filter by Title Containing "chocolate"
```json
{
  "filters": {
    "title__icontains": "chocolate"
  }
}
```

#### Example 4: Multiple Filters
```json
{
  "filters": {
    "category": "Desserts",
    "cooking_time__lte": 30,
    "title__icontains": "chocolate"
  }
}
```

### Sending the Request

When you send a POST request to your API endpoint, make sure to include this JSON body in the request payload. Here’s how you might do it using `curl`:

```sh
curl -X POST "http://yourapiendpoint/api/recipes" -H "Content-Type: application/json" -H "Authorization: Bearer your_token_here" -d '{
  "filters": {
    "category": "Desserts",
    "cooking_time__lte": 30,
    "title__icontains": "chocolate"
  }
}'
```

Replace `"http://yourapiendpoint/api/recipes"` with your actual API endpoint, and `"your_token_here"` with a valid authentication token if required.
</details>


### Deployment

I referred [this](django-with-gunicorn-and-nginx.md) documentation for deployment