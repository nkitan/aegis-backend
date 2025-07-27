const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Enable CORS for all origins
app.use(cors());

// Serve static files from current directory
app.use(express.static(__dirname));

// Serve the main HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'OK', message: 'Project Aegis Test UI is running!' });
});

app.listen(PORT, () => {
    console.log(`🚀 Project Aegis Test UI is running at:`);
    console.log(`   Local:   http://localhost:${PORT}`);
    console.log(`   Network: http://0.0.0.0:${PORT}`);
    console.log(`\n📋 Features available:`);
    console.log(`   📸 Receipt Scanner with Google Wallet integration`);
    console.log(`   💡 Proactive Financial Insights`);
    console.log(`   💬 Natural Language Finance Questions`);
    console.log(`   🍳 Recipe Suggestions from Virtual Pantry`);
    console.log(`\n⚙️  Make sure your backend service is running:`);
    console.log(`   Backend API: http://localhost:8000 (includes integrated agent functionality)`);
});
