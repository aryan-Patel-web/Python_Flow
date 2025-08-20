# 🚀 AI Social Media Automation Platform - Complete Frontend Flow

## 🎯 **COMPLETE USER JOURNEY BREAKDOWN**

### **📱 Entry Points & Authentication Flow**

#### **1. Landing Page (`/` → redirects to `/dashboard` or `/login`)**
- **File**: `src/App.jsx` (Route: `<Route path="/" element={<Navigate to="/dashboard" />} />`)
- **Logic**: 
  - ✅ **If user has token** → Redirect to `/dashboard`
  - ❌ **If no token** → Redirect to `/login`

---

#### **2. Login Page (`/login`)**
- **File**: `src/pages/auth/Login.jsx`
- **Components Used**:
  - Email input field
  - Password input field
  - "Login" button
  - "Forgot Password?" link
  - "Sign up" link

**🔄 User Actions & Redirects:**
```
[Email Input] + [Password Input] → [Login Button] 
    ↓
    ✅ Success: → Navigate to `/dashboard`
    ❌ Error: → Show toast error message

[Forgot Password? Link] → Navigate to `/forgot-password`
[Don't have account? Sign up Link] → Navigate to `/register`
```

---

#### **3. Registration Page (`/register`)**
- **File**: `src/pages/auth/Register.jsx`
- **Components Used**:
  - Name input field
  - Email input field
  - Password input field
  - Confirm Password input field
  - "Create Account" button
  - "Sign in" link

**🔄 User Actions & Redirects:**
```
[Fill Form] → [Create Account Button]
    ↓
    ✅ Success: → Navigate to `/dashboard`
    ❌ Error: → Show validation errors

[Already have account? Sign in Link] → Navigate to `/login`
```

---

#### **4. Forgot Password (`/forgot-password`)**
- **File**: `src/pages/auth/ForgotPassword.jsx`
- **Components Used**:
  - Email input field
  - "Send Reset Instructions" button
  - "Back to login" link

**🔄 User Actions & Redirects:**
```
[Email Input] → [Send Reset Instructions Button]
    ↓
    ✅ Success: → Show success message + stay on page
    ❌ Error: → Show error message

[Back to login Link] → Navigate to `/login`
```

---

## 🏠 **MAIN APPLICATION FLOW (Protected Routes)**

### **5. Dashboard (`/dashboard`) - MAIN HUB**
- **File**: `src/pages/dashboard/Dashboard.jsx`
- **Layout**: Uses `src/components/Layout/Layout.jsx`
- **Components**:
  - **Header**: `src/components/common/Header.jsx`
  - **Sidebar**: `src/components/common/Sidebar.jsx`

**📊 Dashboard Components & Actions:**
```
📈 [Metrics Cards] → Display: Total Posts, Engagement, Followers
🔄 [Recent Activity Feed] → Display: Latest posts across platforms
⚡ [Quick Actions]:
    - [Connect Platform Button] → Navigate to `/credentials`
    - [Create Content Button] → Navigate to `/content`
    - [View Analytics Button] → Navigate to `/analytics`
    - [Automation Settings Button] → Navigate to `/automation`
```

**🎯 Header Actions (Available on ALL pages):**
```
🔍 [Search Bar] → Search functionality (TBD)
🔔 [Notifications Bell] → Show notifications dropdown
👤 [Profile Dropdown]:
    - [Settings Icon] → Navigate to `/settings`
    - [Logout Icon] → Logout + Navigate to `/login`
```

**📋 Sidebar Navigation (Available on ALL pages):**
```
🏠 [Dashboard] → Navigate to `/dashboard`
⚙️ [Credentials] → Navigate to `/credentials`
🎯 [Domains] → Navigate to `/domains`
📝 [Content] → Navigate to `/content`
📊 [Analytics] → Navigate to `/analytics`
⚡ [Automation] → Navigate to `/automation`
💳 [Billing] → Navigate to `/billing`
```

---

### **6. Credentials Page (`/credentials`) - PLATFORM SETUP**
- **File**: `src/pages/credentials/CredentialsPage.jsx`
- **Purpose**: Add social media platform credentials

**🔗 Platform Connection Flow:**
```
📱 Platform Cards Display:
    - [Instagram Card] → [Connect Button] → Modal: Enter username/password
    - [Facebook Card] → [Connect Button] → Modal: Enter username/password  
    - [YouTube Card] → [Connect Button] → Modal: Enter username/password
    - [Twitter Card] → [Connect Button] → Modal: Enter username/password
    - [LinkedIn Card] → [Connect Button] → Modal: Enter username/password

🔄 For Each Platform:
[Connect Button] → [Credential Form Modal]
    ↓
    [Username Input] + [Password Input] → [Test Connection Button]
        ↓
        ✅ Success: → [Save Credentials Button] → Close modal + Update UI
        ❌ Error: → Show error message

[Connected Platform] → [Disconnect Button] → Confirm dialog → Remove credentials

[Next: Setup Content Domains Button] → Navigate to `/domains`
```

---

### **7. Domains Page (`/domains`) - CONTENT SELECTION**
- **File**: `src/pages/domains/DomainsPage.jsx`
- **Purpose**: Select content niches and posting settings

**🎯 Domain Selection Flow:**
```
📋 Content Domain Cards:
    - [Memes] → Checkbox + Preview
    - [Tech News] → Checkbox + Preview  
    - [Coding Tips] → Checkbox + Preview
    - [Lifestyle] → Checkbox + Preview
    - [Business] → Checkbox + Preview
    - [Health & Fitness] → Checkbox + Preview

⚙️ Posting Settings:
[Posting Frequency Slider] → 1-6 posts per day
[Posting Times] → Morning/Afternoon/Evening checkboxes
[Content Style] → Dropdown: Casual/Professional/Funny

🔄 User Actions:
[Domain Checkbox] → Toggle domain selection + Show preview
[Preview Button] → Show sample content for domain
[Save Settings Button] → Save preferences + Navigate to `/content`
[Start Automation Button] → Save + Navigate to `/automation`
```

---

### **8. Content Library (`/content`) - CONTENT MANAGEMENT**
- **File**: `src/pages/content/ContentLibrary.jsx`
- **Purpose**: View, edit, and manage generated content

**📚 Content Management Flow:**
```
📊 Content Filters:
[Platform Filter] → Instagram/Facebook/YouTube/Twitter/LinkedIn
[Domain Filter] → Memes/Tech/Lifestyle/etc.
[Status Filter] → Scheduled/Posted/Draft
[Date Range Picker] → Filter by date

📝 Content Grid:
Each Content Card Shows:
    - Platform icon
    - Content preview
    - Scheduled time
    - Status badge
    - Engagement metrics (if posted)

🔄 Content Actions:
[Content Card] → Click → [Content Detail Modal]
    - [Edit Button] → Open editor
    - [Reschedule Button] → Change posting time
    - [Delete Button] → Confirm + Delete
    - [Post Now Button] → Immediate posting

[Generate New Content Button] → API call → Add to grid
[Bulk Actions]:
    - [Select Multiple] → [Delete Selected] / [Reschedule Selected]

📈 Content Performance:
[View Analytics Button] → Navigate to `/analytics` with content filter
```

---

### **9. Analytics Page (`/analytics`) - PERFORMANCE TRACKING**
- **File**: `src/pages/analytics/AnalyticsPage.jsx`
- **Purpose**: View engagement metrics and growth

**📊 Analytics Dashboard Flow:**
```
📈 Overview Metrics:
[Total Posts] [Total Engagement] [Follower Growth] [Best Performing Post]

📊 Charts Section:
[Engagement Chart] → Line chart showing likes/comments/shares over time
[Platform Breakdown] → Pie chart showing performance by platform
[Content Type Performance] → Bar chart showing best performing domains

🎯 Filters:
[Date Range] → Last 7/30/90 days
[Platform Filter] → All/Instagram/Facebook/etc.
[Content Type] → All/Memes/Tech/etc.

🔄 Analytics Actions:
[Export Data Button] → Download CSV/PDF report
[View Detailed Report] → Navigate to expanded analytics
[Content Insights] → Click on chart → Filter content library
```

---

### **10. Automation Page (`/automation`) - AUTOMATION CONTROL**
- **File**: Placeholder (needs to be created)
- **Purpose**: Start/stop automation and configure settings

**⚡ Automation Control Flow:**
```
🎛️ Automation Status:
[Status Indicator] → Running/Stopped/Paused
[Total Accounts Connected] [Posts Generated Today] [Next Post In: X minutes]

🔄 Automation Controls:
[Start Automation Button] → Begin auto-posting
[Pause Automation Button] → Temporarily stop
[Stop Automation Button] → Completely stop

⚙️ Automation Settings:
[Posting Schedule] → Configure optimal times
[Content Quality] → AI creativity level slider
[Safety Settings] → Content approval before posting
[Platform Priorities] → Which platforms to focus on

🔄 Settings Actions:
[Save Settings Button] → Update automation config
[Test Automation] → Generate 1 test post
[View Automation Logs] → See posting history and errors
```

---

### **11. Billing Page (`/billing`) - SUBSCRIPTION MANAGEMENT**
- **File**: Placeholder (needs to be created)
- **Purpose**: Manage subscription and payments

**💳 Billing Flow:**
```
📊 Current Plan Display:
[Plan Name] [Monthly Cost] [Features List] [Usage Stats]

💰 Plan Options:
[Starter Plan] → $29/month → [Select Plan Button]
[Pro Plan] → $79/month → [Select Plan Button]  
[Agency Plan] → $299/month → [Select Plan Button]

🔄 Billing Actions:
[Upgrade Plan] → Payment modal → Process upgrade
[Downgrade Plan] → Confirmation → Schedule downgrade
[Cancel Subscription] → Confirmation → Cancel at period end
[Update Payment Method] → Payment form modal

📋 Billing History:
[Invoice List] → [Download Invoice] buttons
[Usage Reports] → View API calls, posts generated, etc.
```

---

### **12. Settings Page (`/settings`) - USER PREFERENCES**
- **File**: Placeholder (needs to be created)
- **Purpose**: User profile and app settings

**⚙️ Settings Flow:**
```
👤 Profile Settings:
[Name Input] [Email Input] [Password Change] [Avatar Upload]

🔔 Notification Settings:
[Email Notifications] → Checkboxes for different events
[Push Notifications] → Mobile app settings
[Slack/Discord Integration] → Webhook URLs

🎨 Preferences:
[Time Zone] → Dropdown selection
[Content Language] → Dropdown selection
[Dashboard Layout] → Card/List view toggle

🔄 Settings Actions:
[Save Profile Button] → Update user profile
[Change Password Button] → Password change modal
[Export Data Button] → Download user data
[Delete Account Button] → Confirmation modal → Account deletion
```

---

## 🔐 **PROTECTED ROUTE LOGIC**

### **Route Protection Flow:**
```
User visits any protected route (dashboard, credentials, etc.)
    ↓
ProtectedRoute component checks: localStorage.getItem('auth_token')
    ↓
    ✅ Token exists: → Render requested page
    ❌ No token: → <Navigate to="/login" />
```

### **Authentication Context Flow:**
```
App.jsx wraps everything in <AuthProvider>
    ↓
AuthProvider uses useAuth hook
    ↓
useAuth manages: user, login, logout, loading states
    ↓
All components can access auth via: const { user, logout } = useAuth()
```

---

## 🎯 **COMPLETE BUTTON → ACTION → REDIRECT MAP**

### **Authentication Flow:**
| Button/Link | File | Action | Redirect |
|-------------|------|--------|----------|
| "Login" button | Login.jsx | Call login API | → `/dashboard` |
| "Create Account" button | Register.jsx | Call register API | → `/dashboard` |
| "Forgot Password?" link | Login.jsx | Navigate | → `/forgot-password` |
| "Sign up" link | Login.jsx | Navigate | → `/register` |
| "Sign in" link | Register.jsx | Navigate | → `/login` |
| "Send Reset" button | ForgotPassword.jsx | Call API | → Stay (show success) |
| "Back to login" link | ForgotPassword.jsx | Navigate | → `/login` |

### **Dashboard Actions:**
| Button/Link | File | Action | Redirect |
|-------------|------|--------|----------|
| "Connect Platform" | Dashboard.jsx | Navigate | → `/credentials` |
| "Create Content" | Dashboard.jsx | Navigate | → `/content` |
| "View Analytics" | Dashboard.jsx | Navigate | → `/analytics` |
| "Automation" | Dashboard.jsx | Navigate | → `/automation` |

### **Sidebar Navigation:**
| Button/Link | File | Action | Redirect |
|-------------|------|--------|----------|
| Dashboard | Sidebar.jsx | Navigate | → `/dashboard` |
| Credentials | Sidebar.jsx | Navigate | → `/credentials` |
| Domains | Sidebar.jsx | Navigate | → `/domains` |
| Content | Sidebar.jsx | Navigate | → `/content` |
| Analytics | Sidebar.jsx | Navigate | → `/analytics` |
| Automation | Sidebar.jsx | Navigate | → `/automation` |
| Billing | Sidebar.jsx | Navigate | → `/billing` |

### **Header Actions:**
| Button/Link | File | Action | Redirect |
|-------------|------|--------|----------|
| Logout icon | Header.jsx | Call logout + clear token | → `/login` |
| Settings icon | Header.jsx | Navigate | → `/settings` |
| Notifications | Header.jsx | Show dropdown | → Stay |

### **Platform Connection Flow:**
| Button/Link | File | Action | Redirect |
|-------------|------|--------|----------|
| "Connect" button | CredentialsPage.jsx | Open modal | → Stay |
| "Save Credentials" | CredentialsPage.jsx | Save + close modal | → Stay |
| "Test Connection" | CredentialsPage.jsx | API call | → Stay |
| "Next: Domains" | CredentialsPage.jsx | Navigate | → `/domains` |

### **Content Management:**
| Button/Link | File | Action | Redirect |
|-------------|------|--------|----------|
| "Generate Content" | ContentLibrary.jsx | API call | → Stay |
| Content card | ContentLibrary.jsx | Open modal | → Stay |
| "Edit" button | ContentLibrary.jsx | Open editor | → Stay |
| "Delete" button | ContentLibrary.jsx | Delete + refresh | → Stay |

---

## 🔄 **STATE MANAGEMENT FLOW**

### **Global State (useAuth hook):**
```
Login → Set user + token → All components update
Logout → Clear user + token → Redirect to login
Token expires → Auto logout → Redirect to login
```

### **Local Component State:**
```
Forms: useState for input values, errors, loading
Modals: useState for open/close state  
Data fetching: useState for data, loading, errors
Filters: useState for filter values
```

---

## 🎪 **COMPLETE USER JOURNEY EXAMPLE**

### **New User Experience:**
```
1. Visit app → Redirect to /login
2. Click "Sign up" → /register
3. Fill form + submit → Login automatically → /dashboard
4. Dashboard shows "Connect your first platform" 
5. Click "Connect Platform" → /credentials
6. Add Instagram credentials → Test → Save
7. Click "Next: Setup Domains" → /domains  
8. Select "Memes" + "Tech News" → Save → /content
9. See generated content → /automation
10. Click "Start Automation" → AI takes over!
```

### **Returning User Experience:**
```
1. Visit app → Auto login → /dashboard
2. View metrics and recent posts
3. Click content card → Edit/reschedule
4. Check /analytics for performance
5. Adjust settings in /automation
6. Manage subscription in /billing
```

This complete flow shows every button, every redirect, and every user interaction in your AI Social Media Automation Platform! 🚀