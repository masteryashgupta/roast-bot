#!/usr/bin/env node

import readline from 'readline';
import { getApiKey, setApiKey } from '../src/config.js';
import { getRoast, testApiKey } from '../src/roast.js';

// ANSI Colors
const RED = '\x1b[91m';
const CYAN = '\x1b[96m';
const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';

function printBanner() {
    const banner = `
${RED}${BOLD}===============================================================${RESET}
${CYAN}${BOLD} _____                 _     ___       _   ${RESET}
${CYAN}${BOLD}|  __ \\               | |   |  _ \\    | |  ${RESET}
${CYAN}${BOLD}| |__) |___  __ _ ___ | |_  | |_) | ___| |_ ${RESET}
${CYAN}${BOLD}|  _  // _ \\/ _\` / __|| __| |  _ < / _ \\ __|${RESET}
${CYAN}${BOLD}| | \\ \\ (_) | (_| \\__ \\| |_  | |_) | (_) | |_ ${RESET}
${CYAN}${BOLD}|_|  \\_\\___/ \\__,_|___/ \\__| |____/ \\___/ \\__|${RESET}
${RED}${BOLD}===============================================================${RESET}
${BOLD}🔥 Unfiltered Roast Bot - Terminal Edition 🔥${RESET}
`;
    console.log(banner);
}

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

async function promptForApiKey() {
    return new Promise((resolve) => {
        console.log(`\n${CYAN}You need a Groq API Key to use Roast Bot.${RESET}`);
        console.log(`Get one for free at: ${BOLD}https://console.groq.com${RESET}`);
        rl.question(`\n${CYAN}${BOLD}Paste your GROQ_API_KEY: ${RESET}`, async (key) => {
            const trimmed = key.trim();
            if (!trimmed) {
                console.log(`${RED}Key cannot be empty.${RESET}`);
                resolve(await promptForApiKey());
                return;
            }
            
            console.log(`\n${CYAN}Validating key...${RESET}`);
            const isValid = await testApiKey(trimmed);
            if (isValid) {
                await setApiKey(trimmed);
                console.log(`${CYAN}Key saved ✅${RESET}\n`);
                resolve();
            } else {
                console.log(`${RED}Invalid API Key. Please try again.${RESET}`);
                resolve(await promptForApiKey());
            }
        });
    });
}

async function startChat() {
    printBanner();
    
    const exitCommands = ["exit", "quit", "bye"];
    
    function chatLoop() {
        rl.question(`${CYAN}${BOLD}you ➜ ${RESET}`, async (input) => {
            const userText = input.trim();
            if (!userText) {
                return chatLoop();
            }
            
            if (exitCommands.includes(userText.toLowerCase())) {
                console.log(`\n${RED}${BOLD}roastbot ➜ ${RESET}Bhag yaha se nalle. Fursat me aana! 👋`);
                rl.close();
                return;
            }
            
            try {
                const roast = await getRoast(userText);
                console.log(`${RED}${BOLD}roastbot ➜ ${RESET}${roast}\n`);
            } catch (err) {
                console.log(`${RED}${BOLD}roastbot ➜ ${RESET}Error: ${err.message}\n`);
            }
            
            chatLoop();
        });
    }
    
    chatLoop();
}

async function main() {
    const args = process.argv.slice(2);
    
    if (args.includes('--set-key')) {
        await promptForApiKey();
        console.log("Exiting. Run without --set-key to chat.");
        process.exit(0);
    }
    
    let apiKey = await getApiKey();
    if (!apiKey) {
        await promptForApiKey();
    }
    
    startChat();
}

rl.on('SIGINT', () => {
    console.log(`\n${RED}${BOLD}roastbot ➜ ${RESET}Darr ke bhag gaya? Bye loser! 👋`);
    process.exit(0);
});

main().catch(console.error);
