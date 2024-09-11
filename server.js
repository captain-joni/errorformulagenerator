const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const { stdout } = require('process');

const app = express();
const port = 3000;

// Body Parser Middleware
app.use(bodyParser.json());
app.use(express.static('public'));

// API-Route für die Formelverarbeitung
app.post('/api/differentiate', (req, res) => {
    const { formula, variables } = req.body;

    const { exec } = require('child_process');
    console.log('Data recieved')
    exec(`py differ.py "${formula}" "${variables.join(',')}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Fehler: ${error.message}`);
            return res.status(500).json({ error: 'Fehler bei der Differenzierung' });
        }

        if (stderr) {
            console.error(`stderr: ${stderr}`);
            return res.status(500).json({ error: 'Fehler bei der Differenzierung' });
        }
        array = stdout.split('&');
        formul = array[0];
        eqation = array[1];
        res.json({ result: formul, equation: eqation });
       

    });
});



app.post('/api/formel-anzeigen', (req, res) => {
    const { formula} = req.body;

    const { exec } = require('child_process');
    console.log('Data recieved_2')
    exec(`py texen.py "${formula}" `, (error, stdout, stderr) => {
        if (error) {
            console.error(`Fehler: ${error.message}`);
            return res.status(500).json({ error: 'Fehler bei Anzeigen' });
        }

        if (stderr) {
            console.error(`stderr: ${stderr}`);
            return res.status(500).json({ error: 'Fehler bei Anzeigen' });
        }
    
        res.json({ result: stdout });
       

    });
});

const { spawn } = require('child_process');


app.post('/api/calc', (req, res) => {
    const data = req.body;
    
    console.log('Data received', data);
    
    // Starten des Python-Skripts
    const py = spawn('py', ['calc.py']);
    
    // Schreibe die JSON-Daten in das stdin des Python-Prozesses
    py.stdin.write(JSON.stringify(data));
    py.stdin.end();
    
    let stdout = '';
    let stderr = '';
    
    // Fange die Daten von stdout auf (Ergebnisse vom Python-Skript)
    py.stdout.on('data', (data) => {
        stdout += data.toString();
    });
    
    // Fange Fehler auf stderr auf (wenn es welche gibt)
    py.stderr.on('data', (data) => {
        stderr += data.toString();
    });
    
    // Wenn der Python-Prozess beendet ist
    py.on('close', (code) => {
        if (code !== 0) {
            console.log(`Python-Skript endete mit Fehlercode ${code}`);
            return res.status(500).json({ error: stderr });
        }
    
        // Schicke die Ausgabe von Python als JSON-Antwort zurück
        res.json({ result: stdout });
    });
    

});

// Starte den Server
app.listen(port, () => {
    console.log(`Server läuft auf http://localhost:${port}`);
});
