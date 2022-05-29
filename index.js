const express = require("express");
const path = require("path");
const app = express();
const cors = require('cors');

const corsOptions = {
    origin: 'http://localhost:3000/bestMovie',
    credentials: true,            //access-control-allow-credentials:true
    optionSuccessStatus: 200
}
app.use(cors(corsOptions));

const PORT = process.env.PORT || 5000;

app.use(express.static(path.join(__dirname, "./public")));
app.listen(PORT, () => console.log(`Server started running on port ${PORT}`));
