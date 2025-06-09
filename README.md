# Journal Backend

A simple Flask backend with JWT authentication for the Journal of Recognition Science.

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` file** (optional but recommended):
   ```
   JWT_SECRET_KEY=your-super-secret-key-change-this
   ```

3. **Run the server:**
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`

## API Endpoints

### Public Endpoints
- `GET /health` - Health check
- `POST /api/register` - Register new user
- `POST /api/login` - Login user

### Protected Endpoints (require JWT token)
- `GET /api/profile` - Get user profile
- `POST /api/submit-paper` - Submit a paper
- `GET /api/my-papers` - Get user's papers
- `POST /api/gpt-review` - GPT review (simulated)

## Usage

### Register a new user:
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123", "name": "John Doe"}'
```

### Login:
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Access protected endpoint:
```bash
curl -X GET http://localhost:5000/api/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Frontend Integration

The frontend pages automatically handle authentication:
- Login page: `/login.html`
- Submit paper: `/submit-paper/index.html` (requires authentication)

## Production Considerations

1. **Database**: Replace the JSON file storage with a real database (PostgreSQL, MySQL, etc.)
2. **JWT Secret**: Use a strong, random secret key in production
3. **HTTPS**: Always use HTTPS in production
4. **CORS**: Configure CORS settings appropriately for your domain
5. **GPT Integration**: Replace the simulated GPT review with actual API calls to OpenAI/Anthropic

## Deployment Options

### Local Development
The current setup is perfect for local development and testing.

### Cloud Deployment
For production, consider:
- **Heroku**: Easy deployment with minimal configuration
- **AWS Lambda**: Serverless option with API Gateway
- **Google Cloud Run**: Container-based serverless
- **DigitalOcean App Platform**: Simple PaaS solution

### Example Deployment (Heroku)
1. Add `Procfile`:
   ```
   web: gunicorn app:app
   ```

2. Add `gunicorn` to requirements.txt

3. Deploy:
   ```bash
   heroku create your-journal-backend
   git push heroku main
   ``` 