# Investigating Smart Home Security: Is Blockchain the Answer?

*This document is structured to be easily copy-pasted into a Canva Presentation Template. Each section represents a potential slide or section in your presentation.*

---

## [Slide 1: Title & Introduction]
**Headline:** Investigating Smart Home Security: Is Blockchain the Answer?
**Sub-headline:** Securing IoT Communications using Ethereum Smart Contracts and Lightweight Cryptography.

**Overview:**
Modern Smart Homes are vulnerable to security breaches due to the low processing power of IoT devices and centralized data storage. This project investigates whether combining Decentralized Blockchain Technology (Ethereum) with Lightweight Stream Ciphers (ChaCha20) can secure Smart Home networks without sacrificing performance.

---

## [Slide 2: The Problem]
**Headline:** The Vulnerabilities of Smart Homes

**Key Points:**
*   **Centralized Points of Failure:** Cloud servers storing IoT data can be hacked, compromising the entire home network.
*   **Resource Constraints:** IoT sensors (like smart bulbs) have limited memory, CPU, and battery. They cannot handle heavy, traditional encryption like RSA.
*   **Data Tampering:** Over-the-air commands are vulnerable to interception, Man-in-the-Middle (MitM) attacks, and replay attacks.
*   **Lack of Transparency:** Users have no verifiable, immutable log of who accessed their home devices and when.

---

## [Slide 3: Proposed Solution & Methodology]
**Headline:** A Hybrid Security Architecture

**Core Components:**
1.  **Decentralized Ledger (Ethereum Blockchain):** 
    Eliminates centralized databases. Every user registration and device command is permanently, unalterably recorded as a Smart Contract transaction.
2.  **Lightweight Cryptography (ChaCha20 vs AES):** 
    Replaces heavy encryption with ChaCha20—a high-speed stream cipher designed specifically for devices without hardware cryptography acceleration. 
3.  **Data Integrity (SHA-256):** 
    Every command payload is hashed before transmission to guarantee it was not altered in transit.

---

## [Slide 4: System Architecture Diagram]
**Headline:** How the System Works

*(Insert a visual diagram in Canva showing this flow)*

**The Flow:**
1.  **User Interface (Django Web App):** User authenticates and sends a command (e.g., "Bulb ON").
2.  **Encryption & Hashing:** The web app hashes the command using SHA-256 and encrypts the payload using AES/ChaCha20.
3.  **Blockchain Verification:** The web app interacts with the `SmartHome.sol` Smart Contract via `web3.py`. The contract verifies the user and logs the command permanently on the Ethereum ledger.
4.  **Wireless Routing (TCP Sockets):** The encrypted command travels over a simulated TCP connection to the IoT Base Station (SN).
5.  **Multi-Hop Sensor Network:** The Base Station calculates the shortest Euclidean distance to route the encrypted command hop-by-hop to the target sensor.
6.  **Decryption & Execution:** The target sensor decrypts the package, processes the command, and sends an execution receipt back.

---

## [Slide 5: Technology Stack]
**Headline:** Tools & Technologies Used

*   **Frontend & Backend:** Python, Django Framework, HTML/CSS
*   **Blockchain Infrastructure:** Ethereum, Truffle Suite, Ganache (Local Testnet), Solidity (Smart Contracts)
*   **Web3 Integration:** `web3.py` (Connecting Python to Ethereum)
*   **Cryptography:** `pycryptodome` (ChaCha20), `pyaes` (Advanced Encryption Standard), `hashlib` (SHA-256)
*   **IoT Simulation:** Python `Tkinter` (GUI), `socket` (Network Communication), `math` (Euclidean Routing)
*   **Data Visualization:** `matplotlib`, `numpy` (Real-time performance graphing)

---

## [Slide 6: Performance Evaluation]
**Headline:** Results & Benchmarks

**1. Blockchain Response Time:**
The system measures the exact transaction latency (in milliseconds) required to mine a Smart Contract command. The real-time graph demonstrates the feasibility of using blockchain for near real-time IoT control.

**2. Encryption Optimization (AES vs ChaCha20):**
The extension benchmark compares the computation time of standard AES block-cipher encryption against the proposed ChaCha20 stream cipher. 
*   **Result:** ChaCha20 significantly reduces computational overhead, making it the superior choice for securing low-power IoT constraints without causing noticeable lag for the end-user.

---

## [Slide 7: Conclusion]
**Headline:** Is Blockchain the Answer?

**Conclusion:**
Yes. By stripping away heavy cryptographic overhead (using ChaCha20) and decentralizing access control (using Ethereum), this architecture successfully mitigates standard IoT vulnerabilities. It proves that a secure, immutable, and performant Smart Home ecosystem is achievable today.

---

## [Running the Project Locally (Instructions)]

**1. Start the Blockchain**
```bash
cd hello-eth
npx truffle develop
truffle(develop)> migrate
```

**2. Start the Django Web Server**
```bash
cd SmartHome
python manage.py runserver
```

**3. Start the IoT Sensor Network Simulation**
```bash
cd SmartHome
python IOTSimulation.py
```
