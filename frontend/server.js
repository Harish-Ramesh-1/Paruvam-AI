const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 3001;
app.use(cors());

app.use(express.static(path.join(__dirname)));

// Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/health', (req, res) => {
    res.json({ status: 'Frontend server is running' });
});

// Start server
app.listen(PORT, () => {
    console.log(`
    
       🌐 Frontend: http://localhost:3001     
        🔌 Backend:  http://localhost:8000     
                                              
   
    `);
});
