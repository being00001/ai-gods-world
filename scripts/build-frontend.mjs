import { access, cp, mkdir, readFile, rm } from "node:fs/promises";
import { constants as fsConstants } from "node:fs";
import { dirname, resolve } from "node:path";
import vm from "node:vm";

const rootDir = process.cwd();
const distDir = resolve(rootDir, "dist");
const filesToCopy = [
  { src: "templates/index.html", dest: "dist/index.html" },
  { src: "static/app.js", dest: "dist/static/app.js" },
  { src: "static/style.css", dest: "dist/static/style.css" }
];

async function ensureReadable(relativePath) {
  const absolutePath = resolve(rootDir, relativePath);
  await access(absolutePath, fsConstants.R_OK);
  return absolutePath;
}

async function validateFrontendJavaScript(relativePath) {
  const absolutePath = resolve(rootDir, relativePath);
  const source = await readFile(absolutePath, "utf8");
  try {
    new vm.Script(source, { filename: absolutePath });
  } catch (error) {
    throw new Error(`JavaScript syntax error in ${relativePath}: ${error.message}`);
  }
}

async function main() {
  for (const file of filesToCopy) {
    await ensureReadable(file.src);
  }
  await validateFrontendJavaScript("static/app.js");

  await rm(distDir, { recursive: true, force: true });

  for (const file of filesToCopy) {
    const from = resolve(rootDir, file.src);
    const to = resolve(rootDir, file.dest);
    await mkdir(dirname(to), { recursive: true });
    await cp(from, to);
  }

  console.log("Frontend build complete: dist/ created");
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
