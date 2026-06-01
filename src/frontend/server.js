const express = require("express");
const path = require("path");

const app = express();
const port = Number(process.env.PORT || 5500);
const frontendRoot = __dirname;
const publicRoot = path.join(frontendRoot, "public");

app.use(express.static(frontendRoot));
app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") {
    res.sendStatus(204);
    return;
  }
  next();
});
app.use("/data", express.static(path.join(publicRoot, "data")));

app.get("/", (_req, res) => {
  res.sendFile(path.join(frontendRoot, "main.html"));
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

app.listen(port, () => {
  console.log(`Frontend server running at http://localhost:${port}`);
});