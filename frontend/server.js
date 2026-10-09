const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// 📌 Servir la carpeta "dist"
app.use(express.static(path.join(__dirname, 'dist')));

// 📌 Servir la carpeta "public" para archivos estáticos adicionales
app.use('/public', express.static(path.join(__dirname, 'public')));

// 📌 Manejar todas las rutas con el index.html (modo history de Vue)
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Servidor frontend corriendo en el puerto ${PORT}`);
});

