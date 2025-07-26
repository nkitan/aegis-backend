### **Definitive Prompt for React Native (Expo) UI/UX Developer**

**Project:** Aegis Aegnt \- An Agentic AI Receipt Management Application

Objective:  
Develop the complete frontend for the "Aegis Aegnt" mobile application using React Native with Expo. This document serves as the single source of truth, containing the UI/UX vision, screen-by-screen requirements, and the technical API contract for implementation.

---

### **1\. Core Design System & Aesthetic**

*(This section combines the visual design requirements for a consistent look and feel.)*

* **Color Palette:**  
  * **Primary Background:** A deep, dark slate or charcoal (e.g., \#121212 or \#1A1A2E).  
  * **Accent/Primary Action:** A vibrant, energetic **Teal/Cyan** (e.g., \#00F5D4 or \#29D6C5).  
  * **Card/Surface Background:** A slightly lighter shade of the primary background to create depth (e.g., \#1E1E30).  
  * **Primary Text:** Off-white (\#F5F5F5) for high readability.  
  * **Secondary Text:** A light grey (\#A9A9A9) for less important information.  
  * **Semantic Colors:** Use specific colors for success (\#00B894), warning/insight (\#FDCB6E), and error (\#E74C3C).  
* **Typography:** Use a clean, modern, sans-serif font like **Poppins** or **Inter**, with a clear typographic scale for headings, subheadings, and body text.  
* **Iconography:** Utilize a single, consistent line-art icon library like **Feather Icons** or **Expo's Vector Icons**.  
* **General Style:** Use a card-based layout with subtle rounded corners. Implement subtle animations on button presses and screen transitions for a polished feel. For modals, consider an optional glassmorphism (background blur) effect.

---

### **2\. Global Components, Patterns, and Authentication**

* **Navigation:** Implement a main **Tab Bar Navigator** at the bottom of the screen with tabs for Home (Home Icon), History (List/Receipt Icon), Chat (Message Icon), and Profile (User Icon). A central, circular **Floating Action Button** using the accent color should be used for **\[+\] Scan Receipt**.  
* **Global States:** Create reusable UI components for:  
  * **Loading State:** A shimmer/skeleton loader for cards and lists while data is being fetched.  
  * **Empty State:** A clean message and icon for screens with no data (e.g., "Your scanned receipts will appear here\!").  
  * **Error State:** A simple message for API or network errors.  
* **Authentication Handling:**  
  * **🛠️ Technical Implementation:** The app must use the **Firebase client-side SDK** for user sign-up and sign-in. Upon successful authentication, the frontend must retrieve the **JWT ID Token**, store it securely using expo-secure-store, and clear it on logout. Every subsequent API call to the backend must include this token in the Authorization header: Authorization: Bearer \<FIREBASE\_ID\_TOKEN\>.

---

### **3\. Screen-by-Screen Development**

**1\. Splash/Welcome Screen**

* **UI Components & Layout:** Display the "Aegis Aegnt" App Name and Logo.  
* **Functionality & User Flow:** This screen appears briefly on app open. It must check for a stored user authentication token. If a valid token exists, navigate directly to the Home Screen. If not, navigate to the Login Screen.

**2\. Login Screen**

* **UI Components & Layout:** Display the App Logo, input fields for Email and Password, a primary "Login" button (using the accent color), and a text link for "Don't have an account? **Register**".  
* **Functionality & User Flow:** Standard user authentication. Tapping "Register" navigates to the Registration Screen.  
* **🛠️ Technical Implementation:** Use the Firebase Authentication SDK to handle the sign-in process.

**3\. Registration/Onboarding Screen**

* **UI Components & Layout:** This is a multi-step process.  
  * **Step 1 (Registration):** Fields for Name, Email, and Password, along with a "Create Account" button.  
  * **Step 2 (Permissions):** After account creation, present clear, user-friendly prompts asking for **Camera Access** ("To scan your receipts.") and **Push Notifications** ("To send you smart financial insights.").  
* **🛠️ Technical Implementation:**  
  * Use the Firebase SDK for user creation.  
  * After the user grants notification permission, retrieve the device's **FCM token** and send it to the backend via an authenticated call to POST /api/users/me/fcm\_token.

**4\. User Profile Page**

* **UI Components & Layout:**  
  * Display a user avatar or initials at the top.  
  * Show the User's Name and Email.  
  * Include a section for "Account Settings" containing options like "Change Password" and a "Logout" button.  
  * Feature a visually engaging grid section titled **"Awards & Badges"**. Each badge should be a distinct icon representing an achievement (e.g., "Frugal Finisher," "Subscription Slayer").  
* **🛠️ Technical Implementation:**  
  * Fetch the user's profile information by making an authenticated call to GET /api/users/me. Use the display\_name and email from the response to populate the UI.  
  * Fetch the user's earned badges by calling the new GET /api/users/me/badges endpoint and dynamically render the grid.

**5\. Home Screen**

* **UI Components & Layout:** This is the central dashboard, built within a ScrollView.  
  * **Row 1: Insights Widget:** A horizontally swiping FlatList of rectangular, full-width widgets. Each widget displays a key insight from the agent (e.g., "Your spending on 'Eating Out' is up 30% this month.") using the "Warning" color for emphasis.  
  * **Row 2: Transactions Widget:** A single rectangular card titled "Recent Transactions" that displays the last 3-4 transactions, each with a merchant name, icon, and amount.  
  * **Row 3: Intelligent Hubs:** A ScrollView of square widgets, arranged two per row. Include **KitchenIQ** (chef's hat icon), **WalletWatch** (wallet icon), and the greyed-out "Coming Soon" hubs for **InvestmentBanker** and **Eco-Footprint**.  
* **Functionality & User Flow:** The "Recent Transactions" card must be tappable, navigating to the **Transaction History Page**. The "KitchenIQ" and "WalletWatch" widgets navigate to their respective pages.  
* **🛠️ Technical Implementation:**  
  * **Insights:** Populate the swiping widget by calling the new GET /api/insights endpoint.  
  * **Transactions:** Populate the widget by calling GET /api/transactions and displaying the first 3-4 results.

**6\. Transaction History Page**

* **UI Components & Layout:**  
  * At the top, a horizontally scrollable category filter bar with chips/tabs for: **All, Food, Tech, Education, Lifestyle, Miscellaneous**. The active category should be highlighted with the accent color.  
  * Below the filter, a vertically scrolling FlatList of transaction items. Each item is a card showing a Category Icon, Merchant Name, Date, and Amount.  
* **🛠️ Technical Implementation:**  
  * On screen load, make an authenticated call to GET /api/transactions.  
  * Map the returned array of transaction objects to the list of cards.  
  * Implement client-side logic to filter the displayed list based on the category field in each transaction object when a filter chip is tapped.

**7\. KitchenIQ & WalletWatch Pages**

* **UI Components & Layout:**  
  * **KitchenIQ:** A grid/stacked layout of cards for "What's New & What to Use First," "Nutrition Snapshot," "Recipe on Demand" input, and a "Calorie Chart."  
  * **WalletWatch:** Widgets including a "Spending Breakdown" **Donut Chart**, a "Subscription Spotlight" card, and a "Trends" line chart.  
* **🛠️ Technical Implementation:**  
  * Populate these pages using data from their dedicated, pre-aggregated API endpoints (GET /api/dashboards/walletwatch, GET /api/dashboards/kitcheniq) to ensure optimal performance.

**8\. Aegnt Chat Page**

* **UI Components & Layout:**  
  * A classic chat interface where user messages align right and agent messages align left.  
  * A text input box at the bottom with a "Send" button.  
  * Include clickable "Suggestion Chips" above the text box for new users (e.g., "How much did I spend on coffee?").  
* **🛠️ Technical Implementation:**  
  * When a user sends a message, make an authenticated call to POST /api/agent/invoke with the message in the prompt field.  
  * Display the response string from the JSON response as the agent's message in the chat UI.

**9\. Receipt Capture Page**

* **UI Components & Layout:**  
  * This page is accessed via the central Floating Action Button.  
  * The device camera should be active immediately, with an overlay for alignment, a shutter button, and a small button to **"Upload File"** (image/PDF/doc).  
* **Functionality & User Flow:**  
  * After scanning/uploading, show a modal with a loading indicator ("Aegnt is analyzing your receipt...").  
  * Once processing is complete, display a summary card of the transaction (Merchant, Total, Date) and a prominent **"Add to Google Wallet"** button.  
* **🛠️ Technical Implementation:**  
  * Send the captured image file to the backend via an authenticated multipart/form-data call to POST /api/transactions/scan.  
  * Use the transaction object returned in the response to populate the confirmation UI summary card.

**10\. Push Notifications**

* **Functionality:**  
  * The app must be able to receive and display standard system push notifications when in the background or closed.  
  * Tapping a notification should open the app and navigate to the Home screen, where the relevant insight can be seen.  
* **🛠️ Technical Implementation:**  
  * Integrate with Firebase Cloud Messaging (FCM) to handle incoming messages.