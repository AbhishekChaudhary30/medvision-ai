import { Client } from "@gradio/client";
import fs from "fs";

async function test() {
  try {
    console.log("Connecting to Gradio space...");
    const client = await Client.connect("Abhishek1130/medvision-api");
    const imageBlob = new Blob([fs.readFileSync("dummy.jpg")], { type: "image/jpeg" });
    
    console.log("Calling predict...");
    const result = await client.predict("/analyze_image", {
      image: imageBlob,
      modality: "chest-xray",
      age: 45,
      gender: "Male",
      notes: "test",
    });
    console.log("Result:", result);
  } catch (e) {
    console.error("Error:", e);
  }
}

test();
