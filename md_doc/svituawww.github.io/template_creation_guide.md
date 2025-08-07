**Objective:**
To refactor a static `index.html` file into a modular, reusable template system using Python and Jinja2.

**The Core Idea:**
The goal is to break down your `index.html` into smaller, reusable components. We will create a "base" template that contains the common structure of all pages and then create page-specific templates that "inherit" from this base.

---

### Step 1: Analyze Your `index.html`

First, open your `index.html` and identify the sections that are repeated across most pages. These typically include:
*   **Header/Navigation Bar:** The top section with the logo and menu.
*   **Footer:** The bottom section with contact information and links.
*   **Core Content:** The main content area that is unique to each page.

### Step 2: Create a Base Template

Create a new file named `templates/base_template.html`. Copy the entire content of your `index.html` into this file.

Now, we'll modify it to make it a generic template.

1.  **Find the main content area** in `base_template.html`. This is the part that is *not* the header or footer.
2.  **Replace this entire content area** with a Jinja2 content block:
    ```html
    {% block content %}{% endblock %}
    ```
3.  **Optionally, create partials** for the header and footer to keep your code even cleaner.
    *   Cut the header HTML from `base_template.html` and paste it into a new file: `templates/partials/header.html`.
    *   Do the same for the footer, creating `templates/partials/footer.html`.
    *   In `base_template.html`, replace the areas where the header and footer used to be with `include` statements:
        ```html
        {% include 'partials/header.html' %}
        
        <main>
            {% block content %}{% endblock %}
        </main>
        
        {% include 'partials/footer.html' %}
        ```

**Example `base_template.html`:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
</head>
<body>
    {% include 'partials/header.html' %}

    <main>
        {% block content %}{% endblock %}
    </main>

    {% include 'partials/footer.html' %}
</body>
</html>
```

### Step 3: Create a Page-Specific Template

Now, create a new template for your home page, for example, `templates/home_template.html`. This file will be very simple:

1.  It will **extend** the base template.
2.  It will define the content for the `content` block.

**Example `home_template.html`:**
```html
{% extends "base_template.html" %}

{% block content %}
    <h1>Welcome to our Homepage!</h1>
    <p>This is the unique content for the main page.</p>
{% endblock %}
```

### Step 4: Use a Python Script to Build the Final HTML

Finally, create a Python script (`build.py`) to render these templates into the final `index.html`.

```python
from jinja2 import Environment, FileSystemLoader

# --- Configuration ---
# You can later move this to a separate config.json file
page_data = {
    "title": "Home Page",
    # Add any other data you need in your template
}

# --- Build Script ---
# Set up the Jinja2 environment
env = Environment(loader=FileSystemLoader('templates/'))

# Load the home page template
template = env.get_template('home_template.html')

# Render the template with the data
output_html = template.render(page_data)

# Save the final HTML to the root directory
with open('index.html', 'w') as f:
    f.write(output_html)

print("index.html has been successfully generated!")
```

By following this process, you can convert any static HTML page into a powerful, maintainable, and scalable templating system.