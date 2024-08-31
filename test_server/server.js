const express = require("express");
const body_parser = require("body-parser");
const path = require("path");

const app = express();

// Middleware to parse form data
app.use(body_parser.urlencoded({ extended: true }));

// Serve static files (HTML, CSS, etc.)
app.use(express.static(path.join(__dirname, "public")));

// Handle form submission
app.post("/submit", (req, res) => {
  const form_data = req.body;
  console.log("Form Data:", form_data);
  res.send("Form submitted successfully!");
});

// Start the server
const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
