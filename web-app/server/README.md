# CityLens API Server

Backend API server for CityLens reports management with MongoDB Atlas.

## Setup

1. **Install dependencies:**
```bash
cd server
npm install
```

2. **Configure environment variables:**
Create a `.env` file in the `server` directory:
```env
# MongoDB Atlas Connection String
# Replace username and password with your MongoDB Atlas credentials
# Format: mongodb+srv://username:password@citylensdb.lipe0zx.mongodb.net/citylens?appName=CityLensDB&retryWrites=true&w=majority
MONGODB_URI=mongodb+srv://username:password@citylensdb.lipe0zx.mongodb.net/citylens?appName=CityLensDB&retryWrites=true&w=majority
MONGODB_DB_NAME=citylens
PORT=3001
CORS_ORIGIN=http://localhost:8081
```

**Important:** 
- Replace `username` and `password` with your MongoDB Atlas credentials
- The connection string includes the database name `/citylens` before the query parameters
- Make sure your IP address is whitelisted in MongoDB Atlas Network Access settings

**Note:** Make sure your IP address is whitelisted in MongoDB Atlas Network Access settings.

3. **Start the server:**
```bash
npm start
# or for development with auto-reload:
npm run dev
```

## API Endpoints

### POST /api/reports
Create a new report.

**Request Body:**
```json
{
  "reportType": "Ổ gà",
  "ward": "Phường Cầu Giấy",
  "addressDetail": "Số 123, Ngõ 456",
  "location": {
    "lat": 21.0285,
    "lng": 105.8542
  },
  "title": "Tiêu đề phản ánh",
  "content": "Nội dung phản ánh chi tiết...",
  "media": [
    {
      "uri": "data:image/jpeg;base64,...",
      "type": "image",
      "filename": "image1.jpg"
    }
  ],
  "userId": "optional-user-id"
}
```

### GET /api/reports
Get all reports with optional filters.

**Query Parameters:**
- `limit` (optional): Number of results (default: 20)
- `skip` (optional): Number of results to skip (default: 0)
- `status` (optional): Filter by status (pending, processing, resolved, rejected)

### GET /api/reports/:id
Get a specific report by ID.

### GET /api/media/report/:reportId/:mediaIndex
Serve media file (image/video) from a report. Converts base64 data URI to accessible URL.

**Example:**
```
GET /api/media/report/507f1f77bcf86cd799439011/0
```

Returns the actual image/video file that can be viewed in browser or used in `<img>` or `<video>` tags.

## Testing

Run the test script to verify data:
```bash
node test-reports.js
```

This will:
- Connect to MongoDB
- Fetch all reports
- Display report details including media files
- Verify media URIs
- Show statistics by status

## Database Schema

Reports are stored in the `reports` collection with the following schema:

```javascript
{
  _id: ObjectId,
  reportType: String,
  ward: String,
  addressDetail: String,
  location: {
    lat: Number,
    lng: Number
  },
  title: String,
  content: String,
  media: [{
    uri: String,
    type: String, // 'image' or 'video'
    filename: String
  }],
  userId: String | null,
  status: String, // 'pending', 'processing', 'resolved', 'rejected'
  createdAt: Date,
  updatedAt: Date
}
```

