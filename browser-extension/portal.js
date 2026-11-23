//////.    MADE BY AI ///////////





let filling = false;
let finished = false;

// Fill only when the user opens the RTI form.
async function fillRTI() {
  if (filling || finished) return;
  filling = true;
  try {
    const data = await chrome.runtime.sendMessage({type: "GET_RTI"});
    if (!data || data.error) return;
    const query = document.querySelector('textarea[name="rtiAppQueries[0].queryDescription"]');
    if (!query || query.value.trim()) return;

    const district = document.getElementById("city");
    const surat = district && Array.from(district.options).find(option => option.text.trim() === "SURAT");
    if (!surat) throw Error("Surat district is unavailable.");
    if (district.value !== surat.value) {
      district.value = surat.value;
      district.dispatchEvent(new Event("change", {bubbles: true}));
    }
    Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, "value").set.call(query, data.text);
    query.dispatchEvent(new Event("input", {bubbles: true}));
    query.dispatchEvent(new Event("change", {bubbles: true}));
    query.dispatchEvent(new KeyboardEvent("keyup", {bubbles: true}));
    const result = await chrome.runtime.sendMessage({type: "FILLED_RTI"});
    if (result?.error) throw Error(result.error);
    finished = true;
    query.scrollIntoView({block: "center"});
  } catch (error) {
    console.warn("OpenCity RTI:", error.message);
  } finally {
    filling = false;
  }
}

// Read the incoming link, save its text, and remove the text from the address bar.
async function receiveRTI() {
  try {
    const parameters = new URLSearchParams(location.hash.slice(1));
    const payload = parameters.get("opencity_rti");
    if (payload) {
      const result = await chrome.runtime.sendMessage({type: "SAVE_RTI", data: JSON.parse(payload)});
      if (result?.error) throw Error(result.error);
      history.replaceState(null, "", location.pathname + location.search);
    }
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", watchForm, {once: true});
    } else {
      watchForm();
    }
  } catch (error) {
    console.warn("OpenCity RTI:", error.message);
  }
}

// Wait on the home/login pages without redirecting the user.
function watchForm() {
  new MutationObserver(fillRTI).observe(document.body, {childList: true, subtree: true});
  document.addEventListener("input", fillRTI);
  fillRTI();
}

receiveRTI();
