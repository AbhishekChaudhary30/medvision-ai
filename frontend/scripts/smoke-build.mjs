import { existsSync } from "node:fs";

const requiredPaths = ["dist/index.html", "dist/assets"];
const missingPaths = requiredPaths.filter((path) => !existsSync(path));

if (missingPaths.length > 0) {
  throw new Error(`Frontend build smoke validation failed. Missing: ${missingPaths.join(", ")}`);
}

console.log("Frontend build smoke validation passed.");
