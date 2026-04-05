import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'

const firebaseConfig = {
  apiKey: "AIzaSyDlWIWRvCR3jONopM8Px3Io3necwPYviRw",
  authDomain: "minlog-491211.firebaseapp.com",
  projectId: "minlog-491211",
  storageBucket: "minlog-491211.firebasestorage.app",
  messagingSenderId: "966165311681",
  appId: "1:966165311681:web:a8fed1096d0783412fe440",
  measurementId: "G-TH8HG8GWT7"
}

const app = initializeApp(firebaseConfig)
export const auth = getAuth(app)
