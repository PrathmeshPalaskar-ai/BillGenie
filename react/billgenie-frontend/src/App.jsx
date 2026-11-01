// React se zaroori tools (hooks) la rahe hain. 
// useState: Data (jaise loading status) yaad rakhne ke liye.
// useEffect: Page khulte hi koi automatic kaam (jaise URL check karna) karne ke liye.
import { useState, useEffect } from 'react'

function App() {
  // 'loading' batayega ki button dabne ke baad background me process chal raha hai ya nahi.
  // Shuru mein isko 'false' (band) rakha hai.
  const [loading, setLoading] = useState(false);
  
  // 'paymentSuccess' yaad rakhega ki payment ho chuki hai ya nahi. 
  // Shuru mein false hai, tabhi pehle Pay Now button dikhega.
  const [paymentSuccess, setPaymentSuccess] = useState(false);

  // useEffect tab chalta hai jab page pehli baar load hota hai.
  useEffect(() => {
    // Yeh line browser ke upar wale link (URL) ko padhti hai.
    const urlParams = new URLSearchParams(window.location.search);
    
    // Hum check kar rahe hain ki URL mein "?status=success" likha hai kya?
    // Kyunki FastAPI se payment complete hone ke baad hum user ko ishi URL par wapas bhejenge.
    if (urlParams.get('status') === 'success') {
      // Agar URL mein 'success' mil gaya, toh paymentSuccess ko 'true' kar do.
      setPaymentSuccess(true);
    }
  }, []); // Khali bracket [] ka matlab hai yeh check sirf ek baar karna hai page khulte time.

  // Yeh function tab chalega jab koi 'Pay Now' button dabayega.
  const handlePayment = async () => {
    // Process shuru hote hi loading on kar do (true kar do), 
    // taaki button lock ho jaye aur user baar-baar click na kare.
    setLoading(true);
    
    try {
      // 1. Apne FastAPI backend ko request bhej rahe hain taaki wo PayPal se payment link banwaye.
      const response = await fetch("http://127.0.0.1:8000/create-payment");
      
      // 2. Jo data backend ne wapas diya, use padhne layk (JSON) format mein badal rahe hain.
      const data = await response.json();

      // 3. Agar backend se PayPal ka payment link (payment_url) mil gaya...
      if (data.payment_url) {
        // ...toh browser ko seedha us PayPal link par bhej do (redirect kar do).
        window.location.href = data.payment_url;
      } else {
        // Agar link nahi aaya toh error alert dikhao.
        alert("Payment link banne mein error aayi!");
      }
    } catch (error) {
      // Agar backend server (FastAPI) band hua toh yeh error pakad lega aur website crash nahi hogi.
      console.error("Error:", error);
      alert("Backend se connect nahi ho paya! Apna backend server chalu karo.");
    }
    
    // Process khatam hone ke baad (ya error aane ke baad) loading wapas band kar do.
    setLoading(false);
  };

  // ------------------------------------------------------------------
  // UI (Screen par kya dikhega) - Yahan hum 2 alag screen set kar rahe hain
  // ------------------------------------------------------------------

  // CONDITION 1: Agar payment success ho chuki hai (paymentSuccess = true hai)
  if (paymentSuccess) {
    return (
      // Yeh payment success wala page hai jisme Green Tick dikhega.
      <div style={{ textAlign: 'center', marginTop: '100px', fontFamily: 'sans-serif' }}>
        
        {/* Bada sa hara (green) tick ka emoji aur color */}
        <div style={{ fontSize: '100px', color: '#28a745' }}>✅</div>
        
        {/* Success message */}
        <h1 style={{ color: '#28a745' }}>Payment Successful!</h1>
        <p style={{ fontSize: '20px' }}>Paise account mein aa gaye hain.</p>
        
        {/* 'Go Back' dabane par user wapas normal home page ("/") par chala jayega */}
        <button 
          onClick={() => window.location.href = "/"}
          style={{ padding: '10px 20px', fontSize: '16px', marginTop: '20px', cursor: 'pointer', borderRadius: '5px' }}
        >
          Go Back
        </button>
      </div>
    );
  }

  // CONDITION 2: Agar payment abhi nahi hui hai (paymentSuccess = false hai)
  return (
    // Yeh normal checkout page hai jisme Pay Now button hai.
    <div style={{ textAlign: 'center', marginTop: '100px', fontFamily: 'sans-serif' }}>
      <h1>BillGenie Checkout</h1>
      
      {/* Payment button */}
      <button 
        onClick={handlePayment} // Click karne par upar banaya gaya handlePayment function chalega.
        disabled={loading}      // Jab tak 'loading' true hai, button disable (grey) rahega.
        style={{ 
          padding: '15px 30px', 
          fontSize: '20px', 
          cursor: 'pointer', 
          backgroundColor: '#0070ba', // PayPal jaisa standard blue color
          color: 'white', 
          border: 'none', 
          borderRadius: '5px' 
        }}
      >
        {/* Agar backend ko request ja rahi hai (loading true), toh 'Processing...' dikhao, warna 'Pay Now' */}
        {loading ? "Processing..." : "Pay Now ($10)"}
      </button>
    </div>
  )
}

// Is App function ko bahar bhej rahe hain taaki Vite/React isko screen par render kar sake.
export default App