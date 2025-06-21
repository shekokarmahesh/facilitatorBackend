// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth, RecaptchaVerifier, signInWithPhoneNumber } from "firebase/auth";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAYplRKUjhW_9nB86L3eegoSED9cW_H1Oc",
  authDomain: "ahoumcrm.firebaseapp.com",
  projectId: "ahoumcrm",
  storageBucket: "ahoumcrm.firebasestorage.app",
  messagingSenderId: "1058052705430",
  appId: "1:1058052705430:web:bf4d060dbbf8d1195b86b7",
  measurementId: "G-355BSQSDQK"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);

export { auth, RecaptchaVerifier, signInWithPhoneNumber };
