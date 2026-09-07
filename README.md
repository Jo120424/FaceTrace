# FaceTrace

## Face Identification & Blockchain Verification

FaceTrace is a Python-based prototype developed for **Hackathon Task 3: Face Identification & Blockchain Verification**.

The project combines face detection, face embedding, reverse-image/web search, cryptographic hashing, and blockchain-based verification into a single workflow.

---

## 🎯 Objective

The objective of FaceTrace is to demonstrate how a digital image containing a face can be:

1. Detected and encoded using a face-analysis model.
2. Compared against a reference face.
3. Used for genuine reverse-image/web search.
4. Verified against returned visual-search candidates.
5. Converted into a cryptographic SHA-256 fingerprint.
6. Registered on a blockchain.
7. Re-verified later using the stored on-chain fingerprint.

---

## ✨ Features

- Face detection using **InsightFace**
- Face embedding generation
- Face similarity comparison using cosine similarity
- Genuine web-based visual/reverse-image search
- Face verification of returned visual-search candidates
- SHA-256 image fingerprint generation
- Solidity smart contract for content registration
- Polygon Amoy blockchain integration
- On-chain content verification
- Transaction and block-level verification
- Command-line based implementation with no website dependency

---

## 🏗️ System Workflow

```text
                    INPUT IMAGE
                         │
                         ▼
                ┌─────────────────┐
                │  Face Detection │
                │   InsightFace   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Face Embedding  │
                │   Generation    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Face Similarity │
                │   Comparison    │
                └────────┬────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Reverse Image / Web  │
              │       Search         │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Candidate Face       │
              │ Verification         │
              └──────────┬───────────┘
                         │
                         ▼
                ┌─────────────────┐
                │   SHA-256 Hash  │
                │   Fingerprint   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Polygon Amoy    │
                │   Blockchain    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ On-Chain        │
                │ Verification    │
                └─────────────────┘
🛠️ Technologies Used
Technology	Purpose
Python	Core implementation
OpenCV	Image processing
InsightFace	Face detection and embeddings
ONNX Runtime	Model execution
NumPy	Numerical operations
Requests	Web/API requests
Web3.py	Blockchain interaction
Solidity	Smart contract
Polygon Amoy	Blockchain test network
Remix IDE	Smart contract deployment
MetaMask	Blockchain wallet
📁 Project Structure
FaceTrace/
│
├── app.py
├── requirements.txt
├── .gitignore
│
├── blockchain/
│   └── ContentRegistry.sol
│
├── reference/
│   └── reference.jpg
│
├── sample/
│   └── test.jpg
│
├── search/
│   └── reverse_search.py
│
└── utils/
    └── hashing.py
🔍 1. Face Detection and Encoding

FaceTrace uses InsightFace to detect faces in an input image.

The system generates a numerical face embedding for the detected face. This embedding represents facial characteristics in a machine-readable numerical form.

The project uses the buffalo_l InsightFace model.

Example command:

python app.py --image sample/test.jpg

The application reports:

Number of detected faces
Face similarity score
Match / no-match result
Embedding dimensions
👤 2. Face Similarity Verification

A reference image is stored in:

reference/reference.jpg

The input image is compared with the reference face using cosine similarity between their embeddings.

The prototype was tested using:

The same image
A different image of the same person
An image of a different person

This demonstrates that the system can distinguish between matching and non-matching faces.

The similarity threshold used in this prototype is intended for demonstration purposes and would require further calibration for production deployment.

🌐 3. Reverse Image / Web Search

FaceTrace performs a genuine visual web search rather than relying on hardcoded search results.

The returned visual candidates are downloaded and independently processed using the face-verification pipeline.

Each candidate is checked against the reference face.

Only candidates that satisfy the configured face-similarity threshold are considered potential matches.

This provides an additional verification layer instead of assuming that a visually similar search result is the same person.

🔐 4. SHA-256 Fingerprinting

After processing the image, FaceTrace generates a SHA-256 cryptographic fingerprint of the image file.

Example test fingerprint:

90680046226cadd7b29e5ef40a3d59799be6e4a67773b575920bcfd44a775ff3

The SHA-256 hash is a fixed-length fingerprint of the file contents.

If the file changes, its SHA-256 fingerprint changes.

This allows the system to verify whether the exact file associated with the blockchain record has been modified.

⛓️ 5. Blockchain Registration

The SHA-256 fingerprint was registered on the Polygon Amoy Testnet using the custom Solidity smart contract:

ContentRegistry.sol
Smart Contract
0x951B6D67e7fe43A2e7289A67B0F595a13551F4CB
Network
Polygon Amoy Testnet
Chain ID: 80002
Gas Token: POL

The smart contract provides functions for:

Registering a content hash
Preventing duplicate registration
Recording registration timestamp
Recording the registering wallet address
Verifying whether a hash exists
Retrieving stored registration information
🧾 6. Blockchain Transaction Proof

The successful registration transaction is:

0x203258e41f847bd602d674fc4fb2a139fbf223a123db9aefb5cb94e2e77031de

Transaction status:

SUCCESS

Block:

46981858

Gas used:

100979

The transaction registered the SHA-256 fingerprint on the Polygon Amoy blockchain.

Transaction Explorer

https://amoy.polygonscan.com/tx/0x203258e41f847bd602d674fc4fb2a139fbf223a123db9aefb5cb94e2e77031de

✅ 7. On-Chain Re-Verification

After registration, the same SHA-256 fingerprint was queried against the deployed smart contract.

Verification result:

VERIFY: True

This confirms that the fingerprint exists in the blockchain registry.

Verification Flow
Original Image
      │
      ▼
SHA-256 Fingerprint
      │
      ▼
Register Hash On-Chain
      │
      ▼
Retrieve / Query Hash
      │
      ▼
Compare With Current Hash
      │
      ▼
VERIFY: TRUE

This demonstrates successful blockchain-based proof of registration and re-verification.

📜 Smart Contract

The smart contract is located at:

blockchain/ContentRegistry.sol

The contract stores a record containing:

Content Hash
Timestamp
Registrant Address

The main functions include:

register(bytes32 contentHash)

Registers a new content fingerprint.

verify(bytes32 contentHash)

Checks whether a fingerprint has been registered.

getRecord(bytes32 contentHash)

Retrieves the registration details.

🚀 Installation

Clone the repository:

git clone https://github.com/Jo120424/FaceTrace.git

Move into the project:

cd FaceTrace

Create a virtual environment:

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt
▶️ Running FaceTrace

Run the face-detection pipeline:

python app.py --image sample/test.jpg

The program detects the face, generates an embedding, compares it against the reference image, and reports the similarity result.

🔑 SHA-256 Hash Generation

The project contains a hashing utility:

utils/hashing.py

It can be used to calculate the SHA-256 fingerprint of a file.

Example:

from utils.hashing import sha256_file

print(sha256_file("sample/test.jpg"))

Expected fingerprint for the test image:

90680046226cadd7b29e5ef40a3d59799be6e4a67773b575920bcfd44a775ff3
🔒 Security and Privacy
Private keys are kept outside the Git repository.
API credentials are stored locally using environment variables.
.env is excluded using .gitignore.
The repository does not contain blockchain private keys.
The blockchain stores the content fingerprint rather than the original image.
Face identification should only be performed with appropriate consent and lawful authorization.
⚠️ Limitations
Face Recognition

Face similarity thresholds require proper calibration before being used in a production identity-verification system.

Reverse Search

Reverse-image search depends on publicly indexed web content.

Private, deleted, restricted, or unindexed content may not appear in search results.

Blockchain

Polygon Amoy is a test network and is used here for demonstration and development.

Image Integrity

The SHA-256 fingerprint verifies the exact file contents. A modified version of the image will produce a different hash.

🔮 Future Scope

Future improvements could include:

Improved face-verification threshold calibration
Multi-face processing
Additional reverse-image search providers
Automated evidence reports
Production blockchain deployment
Decentralized storage integration
Web-based user interface
Mobile application
Privacy-preserving face verification
Consent and access-control mechanisms
Automated blockchain verification reports
🎥 Demonstration

The project demonstration covers:

Input image
Face detection
Face embedding generation
Face similarity comparison
Genuine reverse-image/web search
Candidate face verification
SHA-256 fingerprint generation
Smart contract deployment
Blockchain hash registration
Transaction confirmation
On-chain verification returning True
📌 Blockchain Summary
Network:
Polygon Amoy Testnet

Chain ID:
80002

Contract:
0x951B6D67e7fe43A2e7289A67B0F595a13551F4CB

Content SHA-256:
90680046226cadd7b29e5ef40a3d59799be6e4a67773b575920bcfd44a775ff3

Transaction:
0x203258e41f847bd602d674fc4fb2a139fbf223a123db9aefb5cb94e2e77031de

Block:
46981858

Transaction Status:
SUCCESS

Verification:
TRUE
⚖️ Disclaimer

FaceTrace is an educational and hackathon prototype developed to demonstrate the integration of face analysis, visual search, cryptographic hashing, and blockchain verification.

It is not intended to be used as a production-grade identity verification or surveillance system.

Use the system responsibly and only with appropriate authorization and consent.

👩‍💻 Repository

GitHub:

https://github.com/Jo120424/FaceTrace


### After pasting

Click **Commit changes**.

Then your README will appear directly on the repository homepage. Your repo currently contains the project files and the `main` branch as shown in your screenshot; the README is the remaining presentation piece. :contentReference[oaicite:0]{index=0}

**Do not add your `.env`, private key, API key, or `venv` to the README.**
