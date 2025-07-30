FastAPI Authentication Project Setup Guide : 

Prerequisites

1. Python 3.8+ installed on your system
2. MongoDB installed and running locally

Step 1: Install MongoDB

-- For Windows:

1. Download MongoDB Community Server from mongodb.com
2. Install and start MongoDB service
3. MongoDB will run on default port 27017

-- For Ubuntu/Linux:

# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

-- For macOS:

# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb/brew/mongodb-community

Step 2: Install Dependencies

pip install -r requirements.txt

Step 3: Create Environment File
Create .env.local file in the root directory:

MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=auth_db
SECRET_KEY=your-super-secret-key-change-this-in-production
<!-- algorithm=HS256 -->

Step 4: Verify MongoDB is Running

# Check if MongoDB is running
# For Windows (in Command Prompt):
net start | find "MongoDB"

# For Linux/macOS:
sudo systemctl status mongod
# or
ps aux | grep mongod


Step 5: Run the Application
uvicorn main:app --host 0.0.0.0 --port 8000 --reload


Step 6: Test the Application

1. Check if API is running:
Open browser and go to: http://localhost:8000

2. Create your first API key:

curl -X POST "http://localhost:8000/auth/api-keys" \
     -H "Content-Type: application/json" \
     -d '{"name": "admin-key"}'

3. Access Protected Documentation:

1. Go to http://localhost:8000/docs
2. Enter: Bearer sk-your-generated-key
3. Click "Access Docs"
4. Now you can access all API endpoints!


Step 7: Test API Endpoints

List API Keys (Protected):

curl -X GET "http://localhost:8000/auth/api-keys" \
     -H "Authorization: Bearer sk-your-generated-key"

Test Protected Endpoint:

curl -X GET "http://localhost:8000/protected" \
     -H "Authorization: Bearer sk-your-generated-key"




`Production Deployment`
For production deployment:

1. Change SECRET_KEY in .env
2. Use production MongoDB URL
3. Set reload=False in uvicorn
4. Use a production WSGI server like Gunicorn
5. Set up proper logging
6. Use environment variables for sensitive data


-- For the users registration OTP based login via mobile number using Twilio 
update .env files with the following variable

1. TWILIO_ACCOUNT_SID
2. TWILIO_AUTH_TOKEN
3. TWILIO_PHONE_NUMBER