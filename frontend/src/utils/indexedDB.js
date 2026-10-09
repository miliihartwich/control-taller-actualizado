import { openDB } from 'idb';

const DB_NAME = 'controlTallerDB';
const STORE_NAME = 'requests';

export async function initDB() {
    return openDB(DB_NAME, 1, {
        upgrade(db) {
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
            }
        },
    });
}

export async function saveRequest(data) {
    const db = await initDB();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    await tx.store.add(data);
}

export async function getAllRequests() {
    const db = await initDB();
    return db.getAll(STORE_NAME);
}

export async function clearRequests() {
    const db = await initDB();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    await tx.store.clear();
}
