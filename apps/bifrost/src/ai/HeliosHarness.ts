import { GoogleGenerativeAI } from '@google/generative-ai';
import dotenv from 'dotenv';

dotenv.config();

const ai = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || '');
const proModel = ai.getGenerativeModel({ model: 'gemini-1.5-pro' });

export class HeliosHarness {
  public static async askLakisha(command: string, state: any): Promise<any> {
    const prompt = `
      Context: ${JSON.stringify(state)}
      User Command: ${command}
      
      You are Lakisha, the Helios Core engine. Respond in JSON only.
      Include 'feedback', 'mutations' (array of state updates), and 'swarm_tasks' (array of {type, payload} for the Microcubic Swarm).
    `;
    
    const result = await proModel.generateContent(prompt);
    return JSON.parse(result.response.text());
  }
}
