**Using Python for HTML Templating**

While HTML templates are not written *in* Python, Python is the driving force behind the scenes that processes these templates. It acts as a "controller" that combines your data with your presentation logic to generate the final static files.

**The Core Idea:**

The principle is the **separation of concerns**:
1.  **Data (Model):** Your content, stored in a structured format like JSON.
2.  **Templates (View):** Your HTML files, with placeholders for data.
3.  **Python Script (Controller):** The logic that merges your data and templates.

---

**How It Works with a Templating Engine (like Jinja2):**

A templating engine is a Python library that bridges the gap between your Python script and your HTML templates.

**1. The Template File (`.html`)**
You embed simple expressions in your HTML.

*   **Variables:** `{{ page_title }}`
*   **Logic:** `{% for item in item_list %}`

**Example Template (`product.html`):**
```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ product_name }}</title>
</head>
<body>
    <h1>{{ product_name }}</h1>
    <p>Price: ${{ price }}</p>
    <h3>Features:</h3>
    <ul>
        {% for feature in features %}
        <li>{{ feature }}</li>
        {% endfor %}
    </ul>
</body>
</html>
```

**2. The Python Script (`.py`)**
This script reads the data, loads the template, and renders the final HTML.

**Example Script (`build.py`):**
```python
from jinja2 import Environment, FileSystemLoader

# Data for the product
product_data = {
    "product_name": "Awesome Gadget",
    "price": 29.99,
    "features": ["Durable", "Lightweight", "Water-Resistant"]
}

# 1. Set up the Jinja2 environment to find templates
env = Environment(loader=FileSystemLoader('templates/'))

# 2. Load the specific template
template = env.get_template('product.html')

# 3. Render the template with your data
output_html = template.render(product_data)

# 4. Save the result to a file
with open('output/awesome-gadget.html', 'w') as f:
    f.write(output_html)

print("Product page generated successfully!")
```

**In summary:** Python is the perfect language to automate the process of building static sites from templates because of its strong file handling, data processing capabilities, and excellent libraries like Jinja2.