import 'dotenv/config';
import axios from 'axios';
import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';
import fs from 'fs';
import path from 'path';
import FormData from 'form-data';

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: process.env.FIREBASE_API_KEY,
  authDomain: process.env.FIREBASE_AUTH_DOMAIN,
  projectId: process.env.FIREBASE_PROJECT_ID,
  storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.FIREBASE_APP_ID
};

const testUserEmail = process.env.TEST_USER_EMAIL;
const testUserPassword = process.env.TEST_USER_PASSWORD;
const BASE_URL = 'http://127.0.0.1:8000/api/v1';

// --- Main Test Function ---
async function main() {
  if (!firebaseConfig.apiKey || !firebaseConfig.authDomain || !firebaseConfig.projectId || !firebaseConfig.storageBucket || !firebaseConfig.messagingSenderId || !firebaseConfig.appId || !testUserEmail || !testUserPassword) {
    console.error('Error: Please set FIREBASE_API_KEY, FIREBASE_AUTH_DOMAIN, FIREBASE_PROJECT_ID, FIREBASE_STORAGE_BUCKET, FIREBASE_MESSAGING_SENDER_ID, FIREBASE_APP_ID, TEST_USER_EMAIL, and TEST_USER_PASSWORD environment variables.');
    return;
  }

  // Function to upload a receipt
  async function uploadReceipt(accessToken, filePath) {
    const formData = new FormData();
    const fileContent = fs.readFileSync(filePath);
    const mimeType = filePath.toLowerCase().endsWith('.png') ? 'image/png' : 'image/jpeg';
    
    formData.append('file', fileContent, {
      filename: path.basename(filePath),
      contentType: mimeType,
    });
    
    try {
      const response = await axios.post(`${BASE_URL}/transactions/process`, formData, {
        headers: {
          ...formData.getHeaders(),
          'Authorization': `Bearer ${accessToken}`,
        },
      });
      console.log(`Successfully uploaded receipt ${filePath}:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`Error uploading receipt ${filePath}:`, error.response?.data || error.message);
      throw error;
    }
  }

  // Function to fetch transactions
  async function fetchTransactions(accessToken, startDate, endDate, category = null) {
    try {
      const params = {
        start_date: startDate,
        end_date: endDate,
        ...(category && { category })
      };
      
      const response = await axios.get(`${BASE_URL}/transactions`, {
        params,
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });
      console.log('Transactions:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching transactions:', error.response?.data || error.message);
      throw error;
    }
  }

  // Function to test the agent
  async function testAgent(accessToken, prompt) {
    try {
      const response = await axios.post(`${BASE_URL}/users/me/agent/invoke`, 
        { prompt },
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        }
      );
      console.log('Agent response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error invoking agent:', error.response?.data || error.message);
      throw error;
    }
  }

  // 1. Initialize Firebase and Authenticate
  console.log('1. Authenticating with Firebase...');
  const app = initializeApp(firebaseConfig);
  const auth = getAuth(app);
  let idToken;

  try {
    const userCredential = await signInWithEmailAndPassword(auth, testUserEmail, testUserPassword);
    idToken = await userCredential.user.getIdToken();
    console.log('   Authentication successful.');
  } catch (error) {
    console.error(`   Error authenticating with Firebase: ${error.message}`);
    return;
  }

  const headers = { Authorization: `Bearer ${idToken}` };

  // 2. Upload Sample Receipts
  console.log('\n2. Uploading sample receipts...');
  const receiptsDir = path.join(process.cwd(), '..', 'sample_reciepts');
  const receiptFiles = fs.readdirSync(receiptsDir);
  
  for (const file of receiptFiles) {
    console.log(`   Uploading ${file}...`);
    try {
      await uploadReceipt(idToken, path.join(receiptsDir, file));
    } catch (error) {
      console.error(`   Failed to upload ${file}`);
    }
  }

  // 3. Fetch uploaded transactions to verify they were stored
  console.log('\n3. Fetching transactions...');
  try {
    const currentDate = new Date();
    const oneWeekAgo = new Date(currentDate);
    oneWeekAgo.setDate(currentDate.getDate() - 7);
    
    const startDate = oneWeekAgo.toISOString().split('T')[0];
    const endDate = currentDate.toISOString().split('T')[0];
    
    console.log(`   Fetching transactions from ${startDate} to ${endDate}...`);
    const transactions = await fetchTransactions(idToken, startDate, endDate);
    console.log('   Found transactions:', transactions);
    
    // Also test with category filter
    console.log('\n   Fetching Grocery transactions...');
    const groceryTransactions = await fetchTransactions(idToken, startDate, endDate, 'Groceries');
    console.log('   Found grocery transactions:', groceryTransactions);
  } catch (error) {
    console.error('   Failed to fetch transactions:', error.message);
  }

  // 4. Test the Agent with Queries
  console.log('\n4. Testing agent queries...');
  const queries = [
    "How much did I spend on groceries last month?",
    "What was my total spending in the last week?",
    "Show me my spending trends by category",
    "What store did I spend the most at?"
  ];

  for (const query of queries) {
    console.log(`\n   Testing query: "${query}"`);
    try {
      await testAgent(idToken, query);
    } catch (error) {
      console.error(`   Query failed: ${query}`);
    }
  }

  // 4. Get User Profile
  console.log('\n4. Getting user profile...');
  try {
    const response = await axios.get(`${BASE_URL}/users/me`, { headers });
    console.log('   User Profile:', response.data);
  } catch (error) {
    console.error(`   Error getting user profile: ${error.message}`);
    if (error.response) {
      console.error('   Response data:', error.response.data);
      console.error('   Response status:', error.response.status);
      console.error('   Response headers:', error.response.headers);
    }
  }

  // 4. Invoke the AI Agent
  console.log('\n4. Invoking the AI agent...');
  const prompt = 'How much did I spend on groceries last month?';
  console.log(`   Prompt: ${prompt}`);
  try {
    const response = await axios.post(`${BASE_URL}/users/me/agent/invoke`, { prompt }, { headers });
    console.log('   Agent Response:', response.data);
  } catch (error) {
    console.error(`   Error invoking agent: ${error.message}`);
    if (error.response) {
      console.error('   Response data:', error.response.data);
      console.error('   Response status:', error.response.status);
      console.error('   Response headers:', error.response.headers);
    }
  }
}

main();