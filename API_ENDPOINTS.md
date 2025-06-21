# Facilitator Platform API Endpoints

## Overview
This document outlines all the API endpoints for the facilitator platform based on the phone-based authentication and session management system.

## Base URLs
- Authentication: `/api/auth/*`
- Facilitator Management: `/api/facilitator/*`
- Offerings Management: `/api/offerings/*`

---

## 🔐 Authentication Endpoints (`/api/auth/`)

### 1. Send OTP
**POST** `/api/auth/send-otp`

**Purpose**: Send OTP to phone number for verification

**Request Body**:
```json
{
  "phone_number": "+1234567890"
}
```

**Response**:
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "phone_number": "+1234567890"
}
```

### 2. Verify OTP
**POST** `/api/auth/verify-otp`

**Purpose**: Verify OTP and determine user status (new/existing)

**Request Body**:
```json
{
  "phone_number": "+1234567890",
  "otp": "123456"
}
```

**Response for Existing User**:
```json
{
  "success": true,
  "is_new_user": false,
  "facilitator": {...},
  "redirect_to": "dashboard"
}
```

**Response for New User**:
```json
{
  "success": true,
  "is_new_user": true,
  "redirect_to": "onboarding"
}
```

### 3. Complete Onboarding
**POST** `/api/auth/complete-onboarding`

**Purpose**: Create facilitator profile after onboarding (new users only)

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "basic_info": {...},
  "professional_details": {...},
  "bio_about": {...},
  "experience": {...},
  "certifications": {...},
  "visual_profile": {...}
}
```

### 4. Logout
**POST** `/api/auth/logout`

**Purpose**: Clear session and logout

### 5. Session Status
**GET** `/api/auth/session-status`

**Purpose**: Check current session status

---

## 👤 Facilitator Profile Endpoints (`/api/facilitator/`)

*All endpoints require session authentication*

### 1. Get Profile
**GET** `/api/facilitator/profile`

**Purpose**: Get current facilitator's complete profile

**Response**:
```json
{
  "success": true,
  "profile": {
    "id": 1,
    "phone_number": "+1234567890",
    "email": "john@example.com",
    "name": "John Doe",
    "basic_info": {...},
    "professional_details": {...},
    "bio_about": {...},
    "experience": {...},
    "certifications": {...},
    "visual_profile": {...},
    "is_active": true,
    "created_at": "2025-06-21T10:00:00Z",
    "updated_at": "2025-06-21T10:00:00Z"
  }
}
```

### 2. Update Profile
**PUT** `/api/facilitator/profile`

**Purpose**: Update complete facilitator profile

**Request Body**:
```json
{
  "name": "John Doe Updated",
  "email": "john.updated@example.com",
  "basic_info": {...},
  "professional_details": {...},
  "bio_about": {...},
  "experience": {...},
  "certifications": {...},
  "visual_profile": {...}
}
```

### 3. Update Profile Section
**PUT** `/api/facilitator/profile/section`

**Purpose**: Update a specific section of the profile

**Request Body**:
```json
{
  "section": "basic_info",
  "data": {
    "age": 30,
    "location": "New York",
    "languages": ["English", "Spanish"]
  }
}
```

**Valid sections**: `basic_info`, `professional_details`, `bio_about`, `experience`, `certifications`, `visual_profile`

### 4. Get Dashboard Data
**GET** `/api/facilitator/dashboard`

**Purpose**: Get complete dashboard data (profile + offerings + session info)

### 5. Check Profile Completeness
**GET** `/api/facilitator/profile/check-completeness`

**Purpose**: Check how complete the facilitator's profile is

**Response**:
```json
{
  "success": true,
  "completeness": {
    "required_fields_complete": true,
    "completed_sections": ["basic_info", "professional_details"],
    "missing_sections": ["bio_about", "experience"],
    "overall_percentage": 75
  }
}
```

### 6. Search Facilitators (Public)
**GET** `/api/facilitator/search`

**Purpose**: Public search for facilitators

**Query Parameters**:
- `name`: Search by name
- `email`: Search by email
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 10, max: 100)

---

## 📚 Facilitator Offerings Endpoints (`/api/facilitator/`)

*All endpoints require session authentication*

### 1. Get Facilitator's Offerings
**GET** `/api/facilitator/offerings`

**Purpose**: Get all offerings for the current facilitator

### 2. Create Offering
**POST** `/api/facilitator/offerings`

**Purpose**: Create a new offering

**Request Body**:
```json
{
  "title": "Yoga for Beginners",
  "description": "A comprehensive yoga course for beginners",
  "category": "Fitness",
  "basic_info": {...},
  "details": {...},
  "price_schedule": {...}
}
```

### 3. Get Specific Offering
**GET** `/api/facilitator/offerings/{offering_id}`

**Purpose**: Get details of a specific offering (must belong to current facilitator)

### 4. Update Offering
**PUT** `/api/facilitator/offerings/{offering_id}`

**Purpose**: Update a specific offering

### 5. Delete Offering
**DELETE** `/api/facilitator/offerings/{offering_id}`

**Purpose**: Soft delete a specific offering

### 6. Search Offerings (Public)
**GET** `/api/facilitator/offerings/search`

**Purpose**: Public search for offerings

**Query Parameters**:
- `title`: Search by title
- `description`: Search by description
- `category`: Filter by category
- `page`: Page number
- `limit`: Results per page

---

## 📖 Dedicated Offerings Endpoints (`/api/offerings/`)

*All endpoints require session authentication unless noted*

### 1. List Offerings
**GET** `/api/offerings/`

**Purpose**: List all offerings for current facilitator with filtering

**Query Parameters**:
- `category`: Filter by category
- `active`: Show only active offerings (default: true)

### 2. Create New Offering
**POST** `/api/offerings/`

**Purpose**: Create a new offering (alternative endpoint)

### 3. Get Offering by ID
**GET** `/api/offerings/{offering_id}`

**Purpose**: Get specific offering details

### 4. Update Offering by ID
**PUT** `/api/offerings/{offering_id}`

**Purpose**: Update specific offering

### 5. Delete Offering by ID
**DELETE** `/api/offerings/{offering_id}`

**Purpose**: Soft delete specific offering

### 6. Activate Offering
**PUT** `/api/offerings/{offering_id}/activate`

**Purpose**: Reactivate a previously deactivated offering

### 7. Get Offering Statistics
**GET** `/api/offerings/stats`

**Purpose**: Get statistics about facilitator's offerings

**Response**:
```json
{
  "success": true,
  "statistics": {
    "overall": {
      "total_offerings": 10,
      "active_offerings": 8,
      "inactive_offerings": 2,
      "unique_categories": 3
    },
    "categories": [
      {
        "category": "Fitness",
        "count": 5
      },
      {
        "category": "Education",
        "count": 3
      }
    ]
  }
}
```

### 8. Bulk Update Offerings
**PUT** `/api/offerings/bulk/update`

**Purpose**: Update multiple offerings at once

**Request Body**:
```json
{
  "offerings": [
    {
      "id": 1,
      "title": "Updated Title 1",
      "category": "New Category"
    },
    {
      "id": 2,
      "description": "Updated Description 2"
    }
  ]
}
```

### 9. Bulk Delete Offerings
**DELETE** `/api/offerings/bulk/delete`

**Purpose**: Soft delete multiple offerings at once

**Request Body**:
```json
{
  "offering_ids": [1, 2, 3, 4]
}
```

---

## 🔧 Technical Details

### Authentication
- **Session-based**: Uses Flask sessions with 7-day expiration
- **Phone-first**: Phone number is the primary identifier
- **OTP verification**: 6-digit OTP with 10-minute expiration
- **No passwords**: No traditional password authentication

### Data Structure
- **JSONB fields**: Flexible profile and offering data storage
- **Soft deletes**: Uses `is_active` flag instead of hard deletion
- **Timestamps**: All records have `created_at` and `updated_at`
- **Ownership**: Direct `facilitator_id` foreign keys for data isolation

### Error Handling
- **Consistent format**: All errors follow the same JSON structure
- **HTTP status codes**: Proper HTTP status codes for different scenarios
- **Validation**: Input validation on all endpoints
- **Ownership checks**: All operations verify data ownership

### Security
- **Session validation**: All protected endpoints check for valid sessions
- **Ownership verification**: Users can only access their own data
- **Input sanitization**: All inputs are validated and sanitized
- **CORS configured**: Proper CORS setup for frontend integration

### Pagination
- **Standard parameters**: `page` and `limit` query parameters
- **Reasonable limits**: Maximum 100 results per page
- **Response metadata**: Pagination info included in responses

This API provides a complete backend for a facilitator platform with phone-based authentication, profile management, and offering management capabilities.
