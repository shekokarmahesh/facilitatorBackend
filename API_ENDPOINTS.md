# API Endpoints Summary

## Implemented API Endpoints

### 1. Authentication & User Management
- `POST /api/auth/register` - Register new user (sends OTP)
- `POST /api/auth/verify-otp` - Verify OTP and complete registration
- `POST /api/auth/resend-otp` - Resend OTP for registration
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `POST /api/auth/forgot-password` - Send password reset OTP
- `POST /api/auth/reset-password` - Reset password with OTP
- `GET /api/auth/me` - Get current user info
- `PUT /api/auth/profile` - Update user profile (email, password)
- `POST /api/auth/refresh-token` - Refresh JWT token

### 2. Facilitator Profile Management
- `GET /api/facilitator/profile` - Get facilitator profile
- `POST /api/facilitator/profile` - Create facilitator profile
- `PUT /api/facilitator/profile` - Update entire facilitator profile
- `DELETE /api/facilitator/profile` - Delete facilitator profile

#### Section-specific updates:
- `PUT /api/facilitator/profile/basic-info` - Update basic information
- `PUT /api/facilitator/profile/professional-details` - Update professional details
- `PUT /api/facilitator/profile/bio-about` - Update bio/about section
- `PUT /api/facilitator/profile/experience` - Update experience
- `PUT /api/facilitator/profile/certifications` - Update certifications
- `PUT /api/facilitator/profile/visual-profile` - Update visual profile

### 3. Offerings Management
- `GET /api/offerings` - Get all offerings (with filtering)
- `POST /api/offerings` - Create new offering
- `GET /api/offerings/{id}` - Get specific offering
- `PUT /api/offerings/{id}` - Update offering
- `DELETE /api/offerings/{id}` - Delete offering

#### Status management:
- `PUT /api/offerings/{id}/publish` - Publish offering
- `PUT /api/offerings/{id}/archive` - Archive offering
- `PUT /api/offerings/{id}/draft` - Set offering to draft

#### Bulk operations:
- `POST /api/offerings/duplicate/{id}` - Duplicate offering

#### Search and filtering:
- `GET /api/offerings/search` - Search offerings with query parameters
- `GET /api/offerings/categories` - Get available categories
- `GET /api/offerings/tags` - Get available tags

## Database Schema

### Tables:
1. **users** - User authentication and basic info
2. **otps** - OTP verification for registration/password reset
3. **facilitator_profiles** - Detailed facilitator information (JSONB fields)
4. **offerings** - Course/workshop offerings (JSONB fields)

### JSONB Structure:
- **facilitator_profiles**: basic_info, professional_details, bio_about, experience, certifications, visual_profile
- **offerings**: basic_info, details, price_schedule

## Authentication:
- JWT-based authentication
- Token required for protected endpoints
- OTP verification for registration and password reset

## Features:
- Stepwise profile creation/update
- Comprehensive CRUD operations
- Search and filtering capabilities
- Status management for offerings
- Bulk operations support
- Error handling and validation
