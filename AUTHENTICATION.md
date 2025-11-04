# Authentication & Authorization Guide

This document explains the authentication and authorization system implemented in the Expense RAG System, including security measures to protect user data.

## Overview

The system uses **JWT (JSON Web Token)** based authentication to secure all expense-related endpoints. Each user has their own isolated account, and **strict data isolation** ensures users can only access their own expense data.

## Security Features

### ✅ Implemented Security Measures

1. **User Authentication**
   - JWT-based token authentication
   - Bcrypt password hashing
   - Secure token expiration (30 minutes default)

2. **Data Isolation**
   - Each expense is linked to a user via `user_id` foreign key
   - All queries automatically filter by `user_id`
   - Users can NEVER access other users' data

3. **RAG Security**
   - Vector similarity search filters by `user_id`
   - LLM only sees expenses from the authenticated user
   - No cross-user data leakage in embeddings

4. **Database Security**
   - Foreign key constraints with CASCADE delete
   - Indexed user_id for fast filtering
   - Password hashing with bcrypt

## Authentication Flow

### 1. User Registration

**Endpoint:** `POST /auth/register`

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "password": "SecurePassword123",
    "full_name": "John Doe"
  }'
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-01-25T10:00:00",
  "updated_at": "2025-01-25T10:00:00"
}
```

**Security Notes:**
- Password must be at least 8 characters
- Password is hashed using bcrypt before storage
- Username and email must be unique
- Passwords are NEVER returned in responses

### 2. User Login

**Endpoint:** `POST /auth/login`

The login endpoint uses OAuth2 password flow for compatibility with OpenAPI documentation.

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=SecurePassword123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Security Notes:**
- Can login with either username or email
- Passwords are verified using bcrypt
- Token expires after 30 minutes (configurable)
- Inactive users cannot login

### 3. Using the Access Token

All protected endpoints require the access token in the Authorization header:

```bash
curl -X GET "http://localhost:8000/expenses" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 4. Get Current User

**Endpoint:** `GET /auth/me`

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-01-25T10:00:00",
  "updated_at": "2025-01-25T10:00:00"
}
```

## Protected Endpoints

All of the following endpoints require authentication:

| Endpoint | Method | Description | Security |
|----------|--------|-------------|----------|
| `/expenses` | POST | Create expense | Auto-assigns to current user |
| `/expenses` | GET | List expenses | Only returns current user's expenses |
| `/expenses/{id}` | GET | Get expense | Only if it belongs to current user |
| `/expenses/{id}` | PUT | Update expense | Only if it belongs to current user |
| `/expenses/{id}` | DELETE | Delete expense | Only if it belongs to current user |
| `/query` | POST | RAG query | Only searches current user's expenses |

## Data Isolation

### Database Level

The `expenses` table includes a `user_id` foreign key:

```sql
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    embedding VECTOR(384),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_expenses_user_id ON expenses(user_id);
```

### Application Level

Every expense query includes a `user_id` filter:

```python
# Example from expenses.py
query = db.query(Expense).filter(Expense.user_id == current_user.id)
```

### RAG Security

The RAG service explicitly filters by `user_id` in vector search:

```python
# From rag.py
sql = text(
    """
    SELECT * FROM expenses
    WHERE embedding IS NOT NULL
    AND user_id = :user_id  # CRITICAL: User isolation
    ORDER BY embedding <=> CAST(:embedding AS vector)
    LIMIT :limit
"""
)
```

**This ensures:**
- LLM only sees the current user's expense data
- Vector search only retrieves the current user's expenses
- No possibility of cross-user data leakage
- Each user has their own isolated expense dataset

## Example Workflows

### Complete User Journey

```bash
# 1. Register a new user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "username": "alice",
    "password": "SecurePass123",
    "full_name": "Alice Smith"
  }'

# 2. Login to get access token
TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=SecurePass123" \
  | jq -r '.access_token')

# 3. Create an expense (automatically assigned to alice)
curl -X POST "http://localhost:8000/expenses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "groceries",
    "amount": 89.99,
    "date": "2025-01-20",
    "description": "Weekly shopping"
  }'

# 4. Query expenses (only sees alice's expenses)
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How much did I spend on groceries?"
  }'
```

### Multi-User Scenario

```bash
# User 1: Alice
ALICE_TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
  -d "username=alice&password=SecurePass123" | jq -r '.access_token')

# User 2: Bob
BOB_TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
  -d "username=bob&password=SecurePass456" | jq -r '.access_token')

# Alice creates an expense
curl -X POST "http://localhost:8000/expenses" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -d '{"category": "rent", "amount": 1500, "date": "2025-01-01"}'

# Bob creates an expense
curl -X POST "http://localhost:8000/expenses" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -d '{"category": "rent", "amount": 2000, "date": "2025-01-01"}'

# Alice queries her expenses (only sees $1500 rent)
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer $ALICE_TOKEN" \
  -d '{"question": "How much is my rent?"}'

# Bob queries his expenses (only sees $2000 rent)
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer $BOB_TOKEN" \
  -d '{"question": "How much is my rent?"}'
```

**Result:** Each user only sees their own data. No cross-user access.

## Security Best Practices

### For Development

1. **Use the default settings** from `.env.example`
2. **Don't commit `.env`** to version control (already in .gitignore)
3. **Test with multiple users** to verify isolation

### For Production

1. **Change the SECRET_KEY**
   ```bash
   # Generate a secure key
   openssl rand -hex 32

   # Update .env
   SECRET_KEY=your_generated_secure_key_here
   ```

2. **Use HTTPS**
   - Deploy behind a reverse proxy (nginx, traefik)
   - Enable SSL/TLS certificates
   - Never transmit tokens over HTTP

3. **Environment Variables**
   - Store secrets in environment variables or vault services
   - Never hardcode passwords or keys in code
   - Use different keys for dev/staging/production

4. **Token Expiration**
   - Consider shorter expiration for sensitive data (15 minutes)
   - Implement refresh tokens for longer sessions
   - Add token blacklisting for logout

5. **Rate Limiting**
   - Add rate limiting to /auth/login endpoint
   - Prevent brute force attacks
   - Use tools like slowapi or nginx

6. **Password Policies**
   - Enforce strong passwords (length, complexity)
   - Add password strength validation
   - Consider adding 2FA

7. **Database Security**
   - Use strong database passwords
   - Limit database user permissions
   - Enable database SSL connections
   - Regular backups

## Common Errors

### 401 Unauthorized

**Cause:** Missing or invalid token

**Solution:**
- Ensure you're including the Authorization header
- Check token hasn't expired (login again)
- Verify token format: `Bearer YOUR_TOKEN`

```bash
# Correct
curl -H "Authorization: Bearer eyJhbGc..."

# Incorrect
curl -H "Authorization: eyJhbGc..."  # Missing "Bearer"
```

### 403 Forbidden

**Cause:** User account is inactive

**Solution:**
- Contact administrator to activate account
- Check `is_active` field in user record

### 404 Not Found (on expense endpoints)

**Cause:** Expense doesn't belong to the current user

**Solution:**
- Verify you're querying your own expenses
- Check the expense ID is correct
- Cannot access other users' expenses (this is intentional)

## API Documentation

The interactive API documentation includes authentication:

1. **Visit:** http://localhost:8000/docs
2. **Click "Authorize"** button (top right)
3. **Enter credentials:**
   - Username: your_username
   - Password: your_password
4. **Click "Authorize"**
5. **All requests** will now include the token

## JWT Token Structure

The JWT token contains:

```json
{
  "sub": "1",           // User ID
  "username": "alice",  // Username
  "exp": 1706184000     // Expiration timestamp
}
```

**Security Notes:**
- Token is signed with SECRET_KEY (HMAC-SHA256)
- Cannot be tampered with without SECRET_KEY
- Expiration is enforced server-side
- User ID used for all authorization checks

## Testing Authentication

Use the included test users (after running seed script):

| Username | Email | Password |
|----------|-------|----------|
| testuser1 | test1@example.com | TestPass123 |
| testuser2 | test2@example.com | TestPass456 |

## Troubleshooting

### Can see other users' expenses

This should **NEVER** happen if the system is working correctly. If you can see other users' data:

1. Check that `user_id` filter is present in all queries
2. Verify middleware is loading current_user correctly
3. Review database constraints
4. Report as a critical security bug

### Token not working

```bash
# Decode token to check contents (for debugging)
echo "YOUR_TOKEN" | cut -d'.' -f2 | base64 -d | jq
```

### Password reset

Currently not implemented. To reset a user's password:

```python
from app.core.security import get_password_hash
from app.models.user import User

# In a Python shell with database access
user = db.query(User).filter(User.username == "alice").first()
user.hashed_password = get_password_hash("NewPassword123")
db.commit()
```

## Future Enhancements

Potential additions for even more security:

- [ ] Refresh tokens for longer sessions
- [ ] Token blacklisting for logout
- [ ] Two-factor authentication (2FA)
- [ ] OAuth2 social login (Google, GitHub)
- [ ] Email verification for new accounts
- [ ] Password reset via email
- [ ] Account lockout after failed attempts
- [ ] Audit logging for all actions
- [ ] API rate limiting
- [ ] Session management

## Summary

**Key Security Points:**

✅ All expense endpoints require authentication
✅ Users can ONLY access their own data
✅ LLM never sees other users' expenses
✅ Passwords are securely hashed
✅ Tokens expire after 30 minutes
✅ Database enforces user isolation
✅ Vector search filters by user_id
✅ No cross-user data leakage possible

The system implements **defense in depth** with multiple layers of security:
- Authentication (JWT)
- Authorization (user_id checks)
- Database constraints (foreign keys)
- Application logic (filters)
- RAG isolation (vector search filtering)

**Your expense data is private and secure.** 🔒
