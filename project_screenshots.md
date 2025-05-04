# Adding Screenshots to Your Project Report

To enhance your project report with visual evidence of your application's functionality, consider adding screenshots of key interfaces and features. This document guides you on which screenshots to include and how to incorporate them into your report.

## Recommended Screenshots to Include

### 1. User Interfaces

#### Authentication
- Login screen
- Registration form
- Password recovery interface

#### Admin Dashboard
- Main dashboard with statistics and graphs
- User management interface
- Campaign management interface
- Analytics page with charts
- Settings page

#### Influencer Experience
- Campaign discovery/browse page
- Campaign detail view
- Ad request submission form
- Profile management page

#### Sponsor Experience
- Campaign creation form
- Active campaigns management
- Influencer applications review
- Performance metrics view

### 2. Key Features

- Export functionality (showing exported data)
- Notification systems
- Search and filter functionality
- Mobile responsive views (on different devices)

## How to Add Screenshots to Your Report

### Step 1: Capture Screenshots
1. Use your operating system's screenshot tool (Windows: Win+Shift+S, macOS: Cmd+Shift+4)
2. Alternatively, use browser developer tools to capture responsive views
3. Consider using a tool like Lightshot or Snagit for more control

### Step 2: Organize Screenshots
1. Create a folder named `screenshots` in your project directory
2. Save all screenshots with descriptive names (e.g., `admin_dashboard.png`, `campaign_creation.png`)
3. Consider grouping by feature or user role

### Step 3: Add to Your Report
When converting your report to PDF, you can incorporate the screenshots in the following ways:

#### If using Markdown with the provided Python script:
Add image references in the `project_report.md` file:

```markdown
![Admin Dashboard](./screenshots/admin_dashboard.png)
*Figure 1: Admin Dashboard with Key Metrics*
```

#### If using a word processor (Microsoft Word, Google Docs):
1. Copy the content from `project_report.md`
2. Paste into your word processor
3. Insert images at appropriate locations
4. Add captions and figure numbers

## Screenshot Documentation Best Practices

1. **Include context**: Add descriptive captions explaining what the screenshot shows
2. **Highlight key elements**: Consider annotating screenshots to point out important features
3. **Maintain consistency**: Use similar dimensions and styles for all screenshots
4. **Protect privacy**: Blur or redact any sensitive information in screenshots
5. **Consider placement**: Place screenshots immediately after the text that describes the feature
6. **Number figures**: Use a consistent figure numbering system (Figure 1, Figure 2, etc.)

## Example Screenshot Documentation Section

```
## Application Interface

### Admin Dashboard
The administrative dashboard (Figure 1) provides a comprehensive overview of platform activity, including user statistics, campaign metrics, and recent flagged content. The interface uses Chart.js to render interactive visualizations of key data points.

![Admin Dashboard](./screenshots/admin_dashboard.png)
*Figure 1: Administrative Dashboard with Real-time Analytics*

The dashboard includes:
- User statistics (total, active, by role)
- Campaign metrics (total, by status)
- Ad request summary
- Recent flagged content for moderation
```

Adding well-documented screenshots will significantly enhance your project report by providing visual evidence of your implementation and giving reviewers a better understanding of your application's functionality and user experience. 