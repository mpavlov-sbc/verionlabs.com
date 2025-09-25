# Church Directory Website Configuration Guide

## Overview

The Church Directory website has been made fully configurable through the Django admin interface, similar to the main VerionLabs website. All previously hardcoded content can now be customized by administrators.

## New Configurable Models

### 1. WebsiteConfig (Enhanced)
The main configuration model that controls all aspects of the website:

**Basic Site Information:**
- Site title and description
- Company name and domain
- Contact information (support email, sales email, phone, address)

**Page Content:**
- Hero section (headline, subline, CTA buttons)
- About page content (headline, subline, story title, values title)
- Section headlines for features, pricing, use cases
- Call-to-action sections

**Feature Toggles:**
- Show/hide pricing section
- Show/hide testimonials/use cases
- Show/hide team section
- Maintenance mode toggle

**Social Media & Links:**
- App store links
- Social media profiles
- Footer links (help center, privacy policy, terms of service)

**SEO Settings:**
- Meta keywords

### 2. Feature Model
Configurable features displayed on the homepage and features page:
- Title and description
- Icon selection (users, shield, clipboard, mobile, etc.)
- Featured on homepage toggle
- Display order

### 3. Value Model
Company values displayed on the about page:
- Title and description
- Icon selection (heart, shield, check, users, etc.)
- Display order

### 4. UseCase Model
Customer testimonials/use cases for the homepage:
- Persona name and role
- Testimonial quote
- Display order

### 5. AboutStoryParagraph Model
Individual paragraphs for the "Our Story" section:
- Content text
- Display order
- Active/inactive toggle

### 6. TeamMember Model (Enhanced)
Team member profiles for the about page:
- Name, title, bio
- Avatar initials and color customization
- Display order

## Context Processor

A new context processor (`church_directory_config`) makes all configuration data available in templates:
- `church_config` - Main website configuration
- `church_featured_features` - Features for homepage (limited to 6)
- `church_all_features` - All features for features page
- `church_values` - Company values
- `church_use_cases` - Use cases/testimonials (limited to 3)
- `church_story_paragraphs` - Story paragraphs in order
- `church_team_members` - Active team members
- `church_featured_tiers` - Featured pricing tiers (limited to 3)

## Admin Interface

All models have comprehensive admin interfaces with:
- List displays showing key information
- Filters for easy management
- Inline editing where appropriate
- Proper ordering and organization
- Validation to prevent duplicate configurations

## Template Updates

**Updated Templates:**
- `home.html` - Uses configurable content for hero, features, use cases, pricing, CTA
- `about.html` - Uses configurable content for hero, story, values, team

**Template Features:**
- Fallback content if no configuration exists
- Conditional sections based on feature toggles
- Dynamic icon rendering based on selections
- Responsive grid layouts that adapt to content count

## Population Command

A management command `populate_church_directory_config` creates default content:

```bash
python manage.py populate_church_directory_config
```

This command creates:
- Default website configuration
- 6 default features
- 6 default company values
- 3 default use cases
- 3 default story paragraphs
- 3 default team members

## Usage Instructions

### For Administrators:

1. **Access Admin Interface:**
   - Navigate to `/admin/`
   - Look for the "Church Directory" section

2. **Configure Website Settings:**
   - Edit "Website Configuration" to customize headlines, descriptions, contact info
   - Use feature toggles to show/hide sections
   - Update social media links and footer links

3. **Manage Content:**
   - Add/edit Features for homepage and features page
   - Add/edit Values for the about page
   - Add/edit Use Cases for testimonials
   - Add/edit About Story Paragraphs to customize the story
   - Add/edit Team Members for the about page

4. **Customize Appearance:**
   - Choose icons for features and values
   - Set display order for all content sections
   - Use avatar colors and initials for team members

### For Developers:

1. **Database Setup:**
   ```bash
   python manage.py makemigrations church_directory
   python manage.py migrate
   python manage.py populate_church_directory_config
   ```

2. **Template Usage:**
   Templates automatically use configurable content via the context processor.
   All content has fallbacks for graceful degradation.

3. **Extending Configuration:**
   To add new configurable fields:
   - Add fields to appropriate models
   - Update admin interfaces
   - Update context processor if needed
   - Update templates to use new fields
   - Create/update migrations

## Benefits

1. **Full Customization:** All website content can be modified without code changes
2. **Easy Management:** User-friendly admin interface for non-technical users
3. **Flexible Content:** Add/remove/reorder content sections as needed
4. **Feature Toggles:** Show/hide entire sections based on business needs
5. **SEO Friendly:** Configurable meta information and content
6. **Consistent Design:** All content follows the same visual design patterns
7. **Fallback Safety:** Default content ensures the site always works

## Migration Notes

- All existing functionality is preserved
- Templates gracefully degrade if configuration is missing
- The population command ensures a working configuration exists
- Admin users can gradually customize content as needed

This implementation makes the Church Directory website as flexible and maintainable as the main VerionLabs website, allowing for easy customization without developer intervention.