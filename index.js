const express = require("express");
const path = require("path");
const app = express();
const cors = require('cors');

// Our js server is created using the express and so our execution will start from this file
const PORT = process.env.PORT || 5000;

app.use(express.static(path.join(__dirname, "./public")));
app.listen(PORT, () => console.log(`Server started running on port ${PORT}`));
