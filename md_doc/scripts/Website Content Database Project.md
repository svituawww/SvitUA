# SVIT UA Website Content Database Project

**Format:** JSON Database System

## Project Goal
Create comprehensive content management database for entire SVIT UA website

## Database Structure Requirements:
1. **Pages Database** - All website pages with navigation paths and hierarchy levels
2. **Content Sections** - Page components (header, footer, main content, sidebars)
3. **Unique Identifiers** - UUID format for all database entries  
4. **Media Database** - Complete image and asset inventory
5. **Navigation Mapping** - Site structure and routing information

## Implementation Plan:
**STEP 1 (Current):** Develop page models and database schema
**STEP 2 (Next):** Build content section models and relationships
**STEP 3 (Future):** Create media database and asset management

## Current Task:
Develop JSON models for all existing pages in the SVIT UA website.
Await confirmation before proceeding to next implementation step.

*Status: Step 1 - Page Models Development*
comnfirmed Step 1.

*Status: Step 2 - Image Models Development*

## Step 2: Image Database Schema

{
  "database_info": {
    "name": "SVIT UA Image Database",
    "version": "1.0.0",
    "created": "2025-07-28",
    "description": "Complete database of all website images and media assets with metadata and usage tracking",
    "format": "JSON",
    "uuid_format_image": "8",
    "uuid_format_global": "4-4-8",
    "directory_included": {
        "dir1": "svituawww.github.io/uploads",
        "dir2": "svituawww.github.io/images",
        "dir3": "svituawww.github.io/assets"
    },
    "directory_excluded": {
        "dir1": "svituawww.github.io/testpages",
        "dir2": "svituawww.github.io/templates",
        "dir3": "svituawww.github.io/.git"
    }
  },
  "images": {
    "10000001": {
      "id_image": "10000001",
      "id_global": "1001-2001-10000001",
      "title": "SVIT UA Main Logo",
      "filename": "logo-svit-ua.png",
      "pathdir": "svituawww.github.io/uploads/logos/",
      "full_url": "https://svituawww.github.io/uploads/logos/logo-svit-ua.png",
      "type": "logo",
      "format": "PNG",
      "size_bytes": 15432,
      "dimensions": {
        "width": 200,
        "height": 80
      },
      "alt_text": "SVIT UA Official Logo",
      "usage": {
        "pages": ["1", "2"],
        "sections": ["header", "footer"],
        "frequency": "site_wide"
      },
      "metadata": {
        "created": "2025-07-20",
        "modified": "2025-07-25",
        "author": "SVIT UA Team",
        "copyright": "© 2025 SVIT UA"
      }
    },
    "10000002": {
      "id_image": "10000002",
      "id_global": "1001-2002-10000002",
      "title": "Team Member Photo - Director",
      "filename": "team-director-photo.jpg",
      "pathdir": "svituawww.github.io/uploads/team/",
      "full_url": "https://svituawww.github.io/uploads/team/team-director-photo.jpg",
      "type": "team_photo",
      "format": "JPEG",
      "size_bytes": 89456,
      "dimensions": {
        "width": 400,
        "height": 400
      },
      "alt_text": "SVIT UA Team Director Portrait",
      "usage": {
        "pages": ["2"],
        "sections": ["team_section"],
        "frequency": "page_specific"
      },
      "metadata": {
        "created": "2025-07-15",
        "modified": "2025-07-15",
        "author": "SVIT UA Photography",
        "copyright": "© 2025 SVIT UA"
      }
    }
  },
  "image_types": {
    "logo": "Brand and identity images",
    "team_photo": "Staff and team member portraits", 
    "gallery": "Project and event gallery images",
    "background": "Page background and decorative images",
    "icon": "UI icons and small graphics",
    "banner": "Header banners and promotional images"
  },
  "statistics": {
    "total_images": 2,
    "total_size_mb": 0.1,
    "formats": {
      "PNG": 1,
      "JPEG": 1,
      "SVG": 0,
      "WEBP": 0
    },
    "usage_tracking": {
      "site_wide": 1,
      "page_specific": 1,
      "unused": 0
    }
  }
}


## Step 3: Collect needed image info

Collect needed image info for image database (Step 2: Image Database Schema) from pages svituawww.github.io/index.html, svituawww.github.io/team.html 
and store it in image db json.

step 3.1 clarify
scan in js code, json data, html place and look for any image source and put it to following type "usage_array": [...]
