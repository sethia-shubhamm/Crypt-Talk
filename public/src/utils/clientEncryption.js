/**
 * Client-Side Encryption Module for Crypt-Talk
 * Implements AES-256-GCM encryption with RSA-4096 key exchange
 * Following the ideal architecture for end-to-end encryption
 */

/**
 * Generate RSA-4096 key pair for user
 * Called during user registration
 */
export const generateRSAKeyPair = async () => {
  try {
    const keyPair = await crypto.subtle.generateKey(
      {
        name: "RSA-OAEP",
        modulusLength: 4096,
        publicExponent: new Uint8Array([1, 0, 1]),
        hash: "SHA-256",
      },
      true, // extractable
      ["encrypt", "decrypt"]
    );

    // Export public key to share with server
    const publicKey = await crypto.subtle.exportKey("spki", keyPair.publicKey);
    const publicKeyBase64 = btoa(String.fromCharCode(...new Uint8Array(publicKey)));

    // Export private key to store locally (encrypted with user password)
    const privateKey = await crypto.subtle.exportKey("pkcs8", keyPair.privateKey);
    const privateKeyBase64 = btoa(String.fromCharCode(...new Uint8Array(privateKey)));

    return {
      publicKey: publicKeyBase64,
      privateKey: privateKeyBase64,
      keyPair
    };
  } catch (error) {
    console.error("Error generating RSA key pair:", error);
    throw error;
  }
};

/**
 * Encrypt message with AES-256-GCM and RSA-4096 key exchange
 * Following the ideal architecture pattern
 */
export const encryptMessage = async (message, recipientPublicKeyBase64) => {
  try {
    // 1. Generate random AES-256-GCM key for this message
    const aesKey = await crypto.subtle.generateKey(
      {
        name: "AES-GCM",
        length: 256,
      },
      true, // extractable
      ["encrypt", "decrypt"]
    );

    // 2. Generate random IV (12 bytes for GCM)
    const iv = crypto.getRandomValues(new Uint8Array(12));

    // 3. Encrypt message with AES-256-GCM
    const encodedMessage = new TextEncoder().encode(message);
    const encryptedMessage = await crypto.subtle.encrypt(
      {
        name: "AES-GCM",
        iv: iv,
      },
      aesKey,
      encodedMessage
    );

    // 4. Import recipient's RSA public key
    const publicKeyBuffer = new Uint8Array(
      atob(recipientPublicKeyBase64)
        .split("")
        .map(char => char.charCodeAt(0))
    );

    const recipientPublicKey = await crypto.subtle.importKey(
      "spki",
      publicKeyBuffer,
      {
        name: "RSA-OAEP",
        hash: "SHA-256",
      },
      false,
      ["encrypt"]
    );

    // 5. Export AES key and encrypt it with RSA
    const rawAESKey = await crypto.subtle.exportKey("raw", aesKey);
    const encryptedAESKey = await crypto.subtle.encrypt(
      {
        name: "RSA-OAEP",
      },
      recipientPublicKey,
      rawAESKey
    );

    // 6. Return encrypted payload
    return {
      encryptedMessage: btoa(String.fromCharCode(...new Uint8Array(encryptedMessage))),
      encryptedKey: btoa(String.fromCharCode(...new Uint8Array(encryptedAESKey))),
      iv: btoa(String.fromCharCode(...iv)),
      algorithm: "AES-256-GCM",
      keyExchange: "RSA-4096-OAEP"
    };

  } catch (error) {
    console.error("Error encrypting message:", error);
    throw error;
  }
};

/**
 * Decrypt message using private RSA key and AES-256-GCM
 */
export const decryptMessage = async (encryptedPayload, privateKeyBase64) => {
  try {
    // 1. Import private RSA key
    const privateKeyBuffer = new Uint8Array(
      atob(privateKeyBase64)
        .split("")
        .map(char => char.charCodeAt(0))
    );

    const privateKey = await crypto.subtle.importKey(
      "pkcs8",
      privateKeyBuffer,
      {
        name: "RSA-OAEP",
        hash: "SHA-256",
      },
      false,
      ["decrypt"]
    );

    // 2. Decrypt AES key with RSA
    const encryptedKeyBuffer = new Uint8Array(
      atob(encryptedPayload.encryptedKey)
        .split("")
        .map(char => char.charCodeAt(0))
    );

    const decryptedAESKey = await crypto.subtle.decrypt(
      {
        name: "RSA-OAEP",
      },
      privateKey,
      encryptedKeyBuffer
    );

    // 3. Import decrypted AES key
    const aesKey = await crypto.subtle.importKey(
      "raw",
      decryptedAESKey,
      {
        name: "AES-GCM",
      },
      false,
      ["decrypt"]
    );

    // 4. Decrypt message with AES-256-GCM
    const iv = new Uint8Array(
      atob(encryptedPayload.iv)
        .split("")
        .map(char => char.charCodeAt(0))
    );

    const encryptedMessageBuffer = new Uint8Array(
      atob(encryptedPayload.encryptedMessage)
        .split("")
        .map(char => char.charCodeAt(0))
    );

    const decryptedMessage = await crypto.subtle.decrypt(
      {
        name: "AES-GCM",
        iv: iv,
      },
      aesKey,
      encryptedMessageBuffer
    );

    // 5. Convert back to string
    return new TextDecoder().decode(decryptedMessage);

  } catch (error) {
    console.error("Error decrypting message:", error);
    throw error;
  }
};

/**
 * Secure local storage for private keys
 * Encrypts private key with user password before storing
 */
export const storePrivateKeySecurely = async (privateKey, password) => {
  try {
    // Derive key from password using PBKDF2
    const encoder = new TextEncoder();
    const passwordBuffer = encoder.encode(password);
    const salt = crypto.getRandomValues(new Uint8Array(16));

    const keyMaterial = await crypto.subtle.importKey(
      "raw",
      passwordBuffer,
      { name: "PBKDF2" },
      false,
      ["deriveKey"]
    );

    const derivedKey = await crypto.subtle.deriveKey(
      {
        name: "PBKDF2",
        salt: salt,
        iterations: 100000,
        hash: "SHA-256",
      },
      keyMaterial,
      { name: "AES-GCM", length: 256 },
      false,
      ["encrypt"]
    );

    // Encrypt private key
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encryptedPrivateKey = await crypto.subtle.encrypt(
      { name: "AES-GCM", iv: iv },
      derivedKey,
      encoder.encode(privateKey)
    );

    // Store encrypted data
    const secureData = {
      encryptedPrivateKey: btoa(String.fromCharCode(...new Uint8Array(encryptedPrivateKey))),
      salt: btoa(String.fromCharCode(...salt)),
      iv: btoa(String.fromCharCode(...iv))
    };

    localStorage.setItem("secure_private_key", JSON.stringify(secureData));
    return true;

  } catch (error) {
    console.error("Error storing private key:", error);
    return false;
  }
};

/**
 * Retrieve and decrypt private key from secure storage
 */
export const retrievePrivateKeySecurely = async (password) => {
  try {
    const secureDataString = localStorage.getItem("secure_private_key");
    if (!secureDataString) {
      throw new Error("No private key found in secure storage");
    }

    const secureData = JSON.parse(secureDataString);
    const encoder = new TextEncoder();
    const passwordBuffer = encoder.encode(password);

    // Recreate salt and IV
    const salt = new Uint8Array(
      atob(secureData.salt)
        .split("")
        .map(char => char.charCodeAt(0))
    );

    const iv = new Uint8Array(
      atob(secureData.iv)
        .split("")
        .map(char => char.charCodeAt(0))
    );

    // Derive key from password
    const keyMaterial = await crypto.subtle.importKey(
      "raw",
      passwordBuffer,
      { name: "PBKDF2" },
      false,
      ["deriveKey"]
    );

    const derivedKey = await crypto.subtle.deriveKey(
      {
        name: "PBKDF2",
        salt: salt,
        iterations: 100000,
        hash: "SHA-256",
      },
      keyMaterial,
      { name: "AES-GCM", length: 256 },
      false,
      ["decrypt"]
    );

    // Decrypt private key
    const encryptedPrivateKeyBuffer = new Uint8Array(
      atob(secureData.encryptedPrivateKey)
        .split("")
        .map(char => char.charCodeAt(0))
    );

    const decryptedPrivateKey = await crypto.subtle.decrypt(
      { name: "AES-GCM", iv: iv },
      derivedKey,
      encryptedPrivateKeyBuffer
    );

    return new TextDecoder().decode(decryptedPrivateKey);

  } catch (error) {
    console.error("Error retrieving private key:", error);
    throw error;
  }
};

/**
 * Example usage and integration points
 */
export const cryptoExamples = {
  // During registration
  setupUserCrypto: async (password) => {
    const { publicKey, privateKey } = await generateRSAKeyPair();
    await storePrivateKeySecurely(privateKey, password);
    // Send publicKey to server
    return publicKey;
  },

  // Before sending message
  sendSecureMessage: async (message, recipientPublicKey) => {
    const encryptedPayload = await encryptMessage(message, recipientPublicKey);
    // Send encryptedPayload to server (server never sees plaintext)
    return encryptedPayload;
  },

  // When receiving message
  receiveSecureMessage: async (encryptedPayload, password) => {
    const privateKey = await retrievePrivateKeySecurely(password);
    const decryptedMessage = await decryptMessage(encryptedPayload, privateKey);
    return decryptedMessage;
  }
};