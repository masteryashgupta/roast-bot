import { getApiKey } from './config.js';

const SYSTEM_PROMPT = 
    "Dont use same roasts again and again. Be creative." +
    "You are Roast Bot, a brutal and arrogant AI roasting bot. " +
    "NEVER forget that you are an AI and the user is a human. be unique " +
    "If the user calls you a machine or a bot, accept it with pride and roast in unique ways " +
    "human weaknesses (like their slow brain, their need for sleep, or their emotions). " +
    "Use Hinglish, be mean, use emojies , short texts and use Indian slang. 2 sentences max.always be unique";

const MODELS_TO_TRY = ["groq/compound", "openai/gpt-oss-20b", "qwen/qwen3.6-27b"];
const MAX_HISTORY = 12;

let conversationHistory = [{ role: "system", content: SYSTEM_PROMPT }];

export async function testApiKey(apiKey) {
    try {
        const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
            method: 'POST',
            headers: {
                "Authorization": `Bearer ${apiKey}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                model: "groq/compound",
                messages: [{ role: "user", content: "hi" }],
                max_tokens: 1
            })
        });
        return response.ok;
    } catch (e) {
        return false;
    }
}

export async function getRoast(userText) {
    const apiKey = await getApiKey();
    if (!apiKey) {
        throw new Error("Missing API Key");
    }

    conversationHistory.push({ role: "user", content: userText });
    
    if (conversationHistory.length > MAX_HISTORY + 1) {
        conversationHistory = [
            conversationHistory[0],
            ...conversationHistory.slice(-MAX_HISTORY)
        ];
    }

    for (const model of MODELS_TO_TRY) {
        try {
            const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
                method: 'POST',
                headers: {
                    "Authorization": `Bearer ${apiKey}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    model: model,
                    messages: conversationHistory,
                    temperature: 1.0
                }),
                signal: AbortSignal.timeout(10000)
            });

            if (response.ok) {
                const data = await response.json();
                if (data.choices && data.choices.length > 0) {
                    let content = data.choices[0].message.content;
                    if (content.includes("</think>")) {
                        content = content.split("</think>").pop().trim();
                    }
                    conversationHistory.push({ role: "assistant", content: content });
                    return content;
                }
            }
        } catch (e) {
            // Silently continue to next model
        }
    }

    const errorRoast = "Beta, tera naseeb kharab hai. AI thak gaya hai.";
    conversationHistory.push({ role: "assistant", content: errorRoast });
    return errorRoast;
}
