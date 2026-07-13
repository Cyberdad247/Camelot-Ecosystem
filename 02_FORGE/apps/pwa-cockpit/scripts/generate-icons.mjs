import sharp from "sharp";
import { fileURLToPath } from "node:url";

const source = fileURLToPath(new URL("../public/icon.svg", import.meta.url));

await Promise.all(
  [192, 512].map((size) =>
    sharp(source)
      .resize(size, size)
      .png({ compressionLevel: 9 })
      .toFile(fileURLToPath(new URL(`../public/icon-${size}.png`, import.meta.url))),
  ),
);

console.log("Generated PWA icons: 192px, 512px");
