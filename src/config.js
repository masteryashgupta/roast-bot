import fs from 'fs/promises';
import path from 'path';
import os from 'os';

const CONFIG_FILE = path.join(os.homedir(), '.roast-bot-rc');

export async function loadConfig() {
    try {
        const data = await fs.readFile(CONFIG_FILE, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        return {};
    }
}

export async function saveConfig(config) {
    await fs.writeFile(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf-8');
}

export async function getApiKey() {
    const config = await loadConfig();
    return config.apiKey || process.env.GROQ_API_KEY || null;
}

export async function setApiKey(apiKey) {
    const config = await loadConfig();
    config.apiKey = apiKey;
    await saveConfig(config);
}
